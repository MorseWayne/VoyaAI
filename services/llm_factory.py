"""
LLM Factory - Creates language model instances based on configuration.
"""
import logging
from pathlib import Path
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

from config import get_settings
from mcp import get_mcp_tools

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


def create_llm(
    provider: Optional[str] = None,
    for_tools: bool = True
) -> BaseChatModel:
    """
    Create a language model instance.
    
    Args:
        provider: LLM provider (anthropic, openai, google). 
                  If None, uses settings default.
        for_tools: If True, use the primary model for tool calling.
                   If False, may use a faster/cheaper model.
    
    Returns:
        Configured language model instance.
    """
    settings = get_settings()
    provider = provider or settings.llm_provider
    
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        
        return ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            timeout=300,
            max_retries=2,
        )
    
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout=300,
            max_retries=2,
        )
    
    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        return ChatGoogleGenerativeAI(
            google_api_key=settings.google_api_key,
            model=settings.google_model,
            timeout=300,
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def create_agent(
    system_prompt: Optional[str] = None,
    use_tools: bool = True,
) -> AgentExecutor:
    """
    Create an agent with optional tool support.
    
    Args:
        system_prompt: Custom system prompt. If None, uses default travel guide prompt.
        use_tools: Whether to enable MCP tools.
    
    Returns:
        Configured agent executor.
    """
    # Load default prompt if not provided
    if system_prompt is None:
        system_prompt = load_prompt("travel_guide.txt")
    
    # Create the LLM
    llm = create_llm(for_tools=use_tools)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    if use_tools:
        # Create tool-calling agent
        tools = get_mcp_tools()
        agent = create_tool_calling_agent(llm, tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=15,
            handle_parsing_errors=True,
        )
    else:
        # For non-tool tasks, use a simpler chain
        from langchain_core.output_parsers import StrOutputParser
        
        simple_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        chain = simple_prompt | llm | StrOutputParser()
        
        # Wrap in a compatible interface
        class SimpleAgentWrapper:
            def __init__(self, chain):
                self._chain = chain
            
            async def ainvoke(self, inputs: dict) -> dict:
                result = await self._chain.ainvoke(inputs)
                return {"output": result}
            
            def invoke(self, inputs: dict) -> dict:
                result = self._chain.invoke(inputs)
                return {"output": result}
        
        return SimpleAgentWrapper(chain)
