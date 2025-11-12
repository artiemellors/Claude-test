"""
Base Agent class for Block Smith PoC
"""
import os
from typing import Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class BaseAgent:
    """Base class for all agents"""

    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the LLM based on environment variable"""
        provider = os.getenv("AI_PROVIDER", "anthropic").lower()

        if provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            return ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=api_key,
                temperature=0.7
            )
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            return ChatOpenAI(
                model="gpt-4-turbo-preview",
                api_key=api_key,
                temperature=0.7
            )
        else:
            raise ValueError(f"Unknown AI provider: {provider}")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with given input.
        Override this method in subclasses for custom behavior.
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=self._format_input(input_data))
        ]

        response = self.llm.invoke(messages)
        return self._parse_response(response.content)

    def _format_input(self, input_data: Dict[str, Any]) -> str:
        """Format input data as a string for the LLM"""
        import json
        return f"Input:\n{json.dumps(input_data, indent=2)}"

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured data.
        Override in subclasses for custom parsing.
        """
        import json
        import re

        # Try to extract JSON from code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to parse the entire response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # If all else fails, return as raw text
            return {"raw_response": response}
