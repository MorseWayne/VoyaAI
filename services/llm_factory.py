"""
LLM Factory - Creates OpenAI client and Agent for tool calling.
Uses native OpenAI SDK with custom Agent loop.
"""
import json
import logging
from pathlib import Path
from typing import Optional, Callable, Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall

from config import get_settings

logger = logging.getLogger(__name__)

# Prompt directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str) -> str:
    """Load a prompt from the prompts directory."""
    prompt_path = PROMPTS_DIR / filename
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    logger.warning(f"Prompt file not found: {prompt_path}")
    return ""


def create_client() -> AsyncOpenAI:
    """Create an OpenAI client configured for the proxy service."""
    settings = get_settings()
    return AsyncOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    )


class Agent:
    """
    Simple Agent that handles tool calling with OpenAI API.
    
    Implements a loop that:
    1. Sends messages to the LLM
    2. If LLM requests tool calls, executes them
    3. Sends tool results back to LLM
    4. Repeats until LLM returns a final response
    """
    
    def __init__(
        self,
        client: AsyncOpenAI,
        model: str,
        system_prompt: str,
        tools: Optional[list[dict]] = None,
        tool_functions: Optional[dict[str, Callable]] = None,
        max_iterations: int = 15,
    ):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_functions = tool_functions or {}
        self.max_iterations = max_iterations
    
    async def run(
        self,
        user_input: str,
        chat_history: Optional[list[dict]] = None,
    ) -> str:
        """
        Run the agent with user input.
        
        Args:
            user_input: The user's message
            chat_history: Optional previous conversation history
        
        Returns:
            The agent's final response text
        """
        # Build messages
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if chat_history:
            messages.extend(chat_history)
        
        messages.append({"role": "user", "content": user_input})
        
        # Agent loop
        for iteration in range(self.max_iterations):
            logger.debug(f"Agent iteration {iteration + 1}/{self.max_iterations}")
            
            # Call LLM
            response = await self._call_llm(messages)
            assistant_message = response.choices[0].message
            
            # Check if we have tool calls
            if assistant_message.tool_calls:
                # Add assistant message with tool calls
                messages.append(self._message_to_dict(assistant_message))
                
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_result = await self._execute_tool(tool_call)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })
                    logger.info(f"Tool {tool_call.function.name} executed")
            else:
                # No tool calls, we have the final response
                return assistant_message.content or ""
        
        # Max iterations reached
        logger.warning("Agent reached max iterations")
        return assistant_message.content or "抱歉，处理时间过长，请重试。"
    
    async def _call_llm(self, messages: list[dict]) -> Any:
        """Call the LLM with messages and optional tools."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "timeout": 300,
        }
        
        if self.tools:
            kwargs["tools"] = self.tools
            kwargs["tool_choice"] = "auto"
        
        return await self.client.chat.completions.create(**kwargs)
    
    async def _execute_tool(self, tool_call: ChatCompletionMessageToolCall) -> str:
        """Execute a tool call and return the result."""
        function_name = tool_call.function.name
        
        if function_name not in self.tool_functions:
            return f"Error: Unknown tool '{function_name}'"
        
        try:
            # Parse arguments
            arguments = json.loads(tool_call.function.arguments)
            
            # Call the tool function
            func = self.tool_functions[function_name]
            result = await func(**arguments)
            
            return str(result)
        except json.JSONDecodeError as e:
            return f"Error parsing tool arguments: {e}"
        except Exception as e:
            logger.error(f"Error executing tool {function_name}: {e}")
            return f"Error executing tool: {e}"
    
    def _message_to_dict(self, message: ChatCompletionMessage) -> dict:
        """Convert a ChatCompletionMessage to a dict for the messages list."""
        msg_dict = {
            "role": message.role,
            "content": message.content,
        }
        
        if message.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in message.tool_calls
            ]
        
        return msg_dict


def create_agent(
    system_prompt: Optional[str] = None,
    use_tools: bool = True,
) -> Agent:
    """
    Create an agent with optional tool support.
    
    Args:
        system_prompt: Custom system prompt. If None, uses default travel guide prompt.
        use_tools: Whether to enable MCP tools.
    
    Returns:
        Configured Agent instance.
    """
    settings = get_settings()
    client = create_client()
    
    # Load default prompt if not provided
    if system_prompt is None:
        system_prompt = load_prompt("travel_guide.txt")
    
    if use_tools:
        from mcp import get_tools_schema, get_tool_functions
        tools = get_tools_schema()
        tool_functions = get_tool_functions()
    else:
        tools = None
        tool_functions = None
    
    return Agent(
        client=client,
        model=settings.llm_model,
        system_prompt=system_prompt,
        tools=tools,
        tool_functions=tool_functions,
    )


async def simple_chat(content: str) -> str:
    """
    Simple chat without tools - for basic LLM calls.
    
    Args:
        content: The user's message
    
    Returns:
        The LLM's response
    """
    settings = get_settings()
    client = create_client()
    
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": content}],
        timeout=300,
    )
    
    return response.choices[0].message.content or ""
