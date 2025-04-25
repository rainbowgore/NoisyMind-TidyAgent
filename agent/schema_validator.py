from pydantic import BaseModel, ValidationError
import json

class LLMResponse(BaseModel):
    answer: str
    confidence: float

def validate_response(response: str):
    try:
        parsed = json.loads(response)
        validated = LLMResponse(**parsed)
        return True, parsed
    except (ValidationError, json.JSONDecodeError):
        return False, None
