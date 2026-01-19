"""
JSON Parsing Utilities

Helper functions for extracting and parsing JSON from LLM responses.
"""

import json
import re
from loguru import logger
from typing import Dict, Any

def extract_json_from_response(response: str) -> Dict[str, Any]:
    """
    Extract JSON from LLM response, handling markdown code blocks.
    
    Args:
        response: Raw LLM response that may contain JSON
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If no valid JSON could be extracted
    """
    # Try to extract JSON from markdown code blocks first
    json_patterns = [
        r'```json\s*\n?(.*?)\n?```',  # ```json ... ```
        r'```\s*\n?(.*?)\n?```',       # ``` ... ```
        r'(?s)\{.*\}',                 # Raw JSON object (multiline)
    ]
    
    for pattern in json_patterns:
        # re.DOTALL is implicitly handled by (?s) in the last pattern or explicit flags below
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches:
            try:
                # Clean up potential leading/trailing whitespace
                json_str = match.strip()
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue
    
    # Last resort: try parsing the entire response
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from response: {response[:500]}")
        raise ValueError(f"Could not extract valid JSON from LLM response: {e}")
