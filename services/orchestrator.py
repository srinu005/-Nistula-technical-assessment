from models.enums import ActionType, QueryType
from models.schemas import WebhookPayload, UnifiedMessage, FinalResponse
from .base import LLMProvider
from core.constants import PROPERTY_CONTEXT

class MessageOrchestrator:
    def __init__(self, ai_provider: LLMProvider):
        self.ai_provider = ai_provider

    async def process(self, payload: WebhookPayload) -> FinalResponse:
        # 1. Normalize
        unified = UnifiedMessage(
            source=payload.source,
            guest_name=payload.guest_name,
            message_text=payload.message,
            timestamp=payload.timestamp,
            booking_ref=payload.booking_ref,
            property_id=payload.property_id
        )

        # 2. Call AI
        ai_output = await self.ai_provider.generate_response(unified, PROPERTY_CONTEXT)

        # 3. Business Rules for Action
        action = self._determine_action(ai_output)

        return FinalResponse(
            message_id=unified.message_id,
            query_type=ai_output.query_type,
            drafted_reply=ai_output.drafted_reply,
            confidence_score=ai_output.confidence_score,
            action=action
        )

    def _determine_action(self, ai_output) -> ActionType:
        # Guardrail: Complaints are always escalated
        if ai_output.query_type == QueryType.COMPLAINT:
            return ActionType.ESCALATE
        
        # Score-based routing
        if ai_output.confidence_score >= 0.85:
            return ActionType.AUTO_SEND
        if ai_output.confidence_score >= 0.60:
            return ActionType.AGENT_REVIEW
        
        return ActionType.ESCALATE