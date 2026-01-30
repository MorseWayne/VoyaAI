"""
Travel Service - Core business logic for travel planning.
"""
import logging
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from .llm_factory import create_agent, load_prompt

logger = logging.getLogger(__name__)


@dataclass
class TravelPlan:
    """Represents a generated travel plan."""
    guide_text: str
    html_content: str
    destination: str = ""
    

class TravelService:
    """
    Travel planning service that combines multiple AI agents
    to generate comprehensive travel itineraries.
    """
    
    OUTPUT_DIR = Path("output")
    
    def __init__(self):
        self.OUTPUT_DIR.mkdir(exist_ok=True)
    
    async def generate_travel_guide(self, requirements: str) -> TravelPlan:
        """
        Generate a complete travel guide based on user requirements.
        
        This is a two-step process:
        1. Use tool-calling agent to gather information and create the guide
        2. Use a simpler agent to convert the guide to beautiful HTML
        
        Args:
            requirements: User's travel requirements and preferences
        
        Returns:
            TravelPlan with both text guide and HTML content
        """
        logger.info(f"Generating travel guide for: {requirements[:100]}...")
        
        # Step 1: Generate travel guide using tool-calling agent
        guide_text = await self._generate_guide_text(requirements)
        logger.info("Travel guide text generated successfully")
        
        # Step 2: Convert to beautiful HTML
        html_content = await self._generate_html(guide_text)
        logger.info("HTML content generated successfully")
        
        # Clean HTML output
        html_content = self._clean_html(html_content)
        
        # Save outputs
        await self._save_outputs(guide_text, html_content)
        
        return TravelPlan(
            guide_text=guide_text,
            html_content=html_content,
        )
    
    async def _generate_guide_text(self, requirements: str) -> str:
        """Generate the travel guide text using MCP tools."""
        agent = create_agent(use_tools=True)
        
        result = await agent.ainvoke({
            "input": requirements,
            "chat_history": [],
        })
        
        return result.get("output", "")
    
    async def _generate_html(self, guide_text: str) -> str:
        """Convert travel guide text to beautiful HTML."""
        html_prompt = load_prompt("html_template.txt")
        
        # Use a non-tool agent for HTML generation
        agent = create_agent(
            system_prompt=html_prompt,
            use_tools=False,
        )
        
        result = await agent.ainvoke({
            "input": f"请将以下旅行攻略转换为精美的HTML页面：\n\n{guide_text}",
        })
        
        return result.get("output", "")
    
    def _clean_html(self, html: str) -> str:
        """Clean HTML output from markdown code blocks."""
        # Remove ```html prefix
        if html.startswith("```html"):
            html = html[7:]
        elif html.startswith("```"):
            html = html[3:]
        
        # Remove trailing ```
        if html.endswith("```"):
            html = html[:-3]
        
        return html.strip()
    
    async def _save_outputs(self, guide_text: str, html_content: str) -> None:
        """Save generated content to files."""
        try:
            # Save HTML
            html_path = self.OUTPUT_DIR / "travel.html"
            html_path.write_text(html_content, encoding="utf-8")
            logger.info(f"HTML saved to: {html_path}")
            
            # Save text guide
            text_path = self.OUTPUT_DIR / "travel_guide.txt"
            text_path.write_text(guide_text, encoding="utf-8")
            logger.info(f"Guide text saved to: {text_path}")
            
        except Exception as e:
            logger.error(f"Error saving outputs: {e}")
    
    def generate_travel_guide_sync(self, requirements: str) -> TravelPlan:
        """Synchronous version of generate_travel_guide."""
        import asyncio
        return asyncio.run(self.generate_travel_guide(requirements))
