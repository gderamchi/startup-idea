"""
AI Service for Feedback Parsing
Blackbox AI integration for parsing creative feedback
"""
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI

from app.core.config import settings
from app.core.logging_config import logger

# Configure OpenAI client to use Blackbox API endpoint
client = OpenAI(
    api_key=settings.BLACKBOX_API_KEY,
    base_url="https://api.blackbox.ai/v1"  # Blackbox API endpoint
)

FEEDBACK_PARSING_PROMPT = """
You are an expert at analyzing creative feedback and extracting actionable tasks.

Given the following client feedback, please:
1. Extract specific, actionable tasks
2. Determine the sentiment (positive, neutral, negative)
3. Assign a priority level (low, medium, high, urgent)
4. Provide a clear summary

Feedback: {feedback_text}

Respond in JSON format:
{{
  "summary": "Brief summary of the feedback",
  "sentiment": "positive|neutral|negative",
  "priority": "low|medium|high|urgent",
  "action_items": [
    {{
      "description": "Specific actionable task",
      "priority": 0-3
    }}
  ],
  "key_points": ["point 1", "point 2"]
}}
"""

async def parse_feedback(feedback_text: str) -> Dict[str, Any]:
    """
    Parse feedback using OpenAI GPT-4
    
    Args:
        feedback_text: Raw feedback text from client
        
    Returns:
        Parsed feedback with action items, sentiment, and priority
    """
    try:
        logger.info("Parsing feedback with AI", extra={"text_length": len(feedback_text)})
        
        # Use Blackbox AI model endpoint
        # Format: /chat/completions/blackboxai/openai/gpt-4o
        response = client.chat.completions.create(
            model="blackboxai-pro",  # Blackbox AI model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes creative feedback."},
                {"role": "user", "content": FEEDBACK_PARSING_PROMPT.format(feedback_text=feedback_text)}
            ],
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.info("Successfully parsed feedback", extra={"action_items": len(result.get("action_items", []))})
        
        return result
        
    except Exception as e:
        logger.error(f"Error parsing feedback: {str(e)}", exc_info=True)
        raise

def extract_action_items(parsed_feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract action items from parsed feedback"""
    return parsed_feedback.get("action_items", [])

def get_sentiment(parsed_feedback: Dict[str, Any]) -> str:
    """Get sentiment from parsed feedback"""
    return parsed_feedback.get("sentiment", "neutral")

def get_priority(parsed_feedback: Dict[str, Any]) -> str:
    """Get priority from parsed feedback"""
    return parsed_feedback.get("priority", "medium")
