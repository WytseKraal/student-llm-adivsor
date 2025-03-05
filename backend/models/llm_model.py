from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    role: str
    content: str

class LLMRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    
class TokenUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: TokenUsage
    id: str