"""
Base Agent - Foundation for all AI agents with improved JSON parsing
"""
import json
import re
import os
from typing import Dict, Any, Optional
from anthropic import Anthropic


class BaseAgent:
    """Base class for all agents with LLM interaction capabilities"""

    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def execute(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with given input and return structured output"""
        try:
            # Convert input to JSON string for the prompt
            user_message = json.dumps(user_input, indent=2)

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Extract text from response
            response_text = response.content[0].text

            # Parse JSON from response
            result = self._parse_response(response_text)

            return result

        except Exception as e:
            return {
                "error": str(e),
                "agent": self.name,
                "raw_response": response_text if 'response_text' in locals() else None
            }

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response with multiple fallback strategies"""
        # Strategy 1: Try to find JSON in code blocks
        patterns = [
            r'```json\s*(\{.*?\})\s*```',  # ```json { } ```
            r'```\s*(\{.*?\})\s*```',       # ``` { } ```
            r'(\{[\s\S]*\})',                # Any { } block
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    clean_json = match.strip()
                    parsed = json.loads(clean_json)
                    # If it's a valid dict, return it
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue

        # Strategy 2: If response looks like raw JSON, try parsing it directly
        try:
            parsed = json.loads(response.strip())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        # Strategy 3: Return raw response with error
        return {
            "error": "Could not parse JSON from response",
            "raw_response": response
        }
