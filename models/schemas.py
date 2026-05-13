import uuid
from typing import Optional
from pydantic import BaseModel, Field
from .enums import MessageSource, QueryType, ActionType

class WebhookPayload(BaseModel):
    source: MessageSource
    guest_name: str
    message: str
    timestamp: str
    booking_ref: Optional[str] = None
    property_id: str

class UnifiedMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: MessageSource
    guest_name: str
    message_text: str
    timestamp: str
    booking_ref: Optional[str]
    property_id: str

class AIResult(BaseModel):
    query_type: QueryType
    drafted_reply: str
    confidence_score: float

class FinalResponse(BaseModel):
    message_id: str
    query_type: QueryType
    drafted_reply: str
    confidence_score: float
    action: ActionType