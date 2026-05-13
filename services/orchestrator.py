from models.enums import ActionType, QueryType
from models.schemas import WebhookPayload, UnifiedMessage, FinalResponse
from .base import LLMProvider
from core.constants import PROPERTY_CONTEXT
from database.repository import MessagingRepository  # <--- New Import

class MessageOrchestrator:
    def __init__(self, ai_provider: LLMProvider, repo: MessagingRepository):
        # We now depend on BOTH an AI provider and a Data Repository
        self.ai_provider = ai_provider
        self.repo = repo

    async def process(self, payload: WebhookPayload) -> FinalResponse:
        # 1. Normalize (SRP)
        unified = UnifiedMessage(
            source=payload.source,
            guest_name=payload.guest_name,
            message_text=payload.message,
            timestamp=payload.timestamp,
            booking_ref=payload.booking_ref,
            property_id=payload.property_id
        )

        # 2. Database Identity Resolution (Part 2)
        # Find or create the guest and their current conversation thread
        conv_id = await self.repo.resolve_guest_and_conversation(unified)

        # 3. Save the Inbound Message (Part 2)
        # We store the guest's message before we even talk to the AI
        await self.repo.save_message(
            conv_id=conv_id,
            direction="inbound",
            content=unified.message_text,
            source=unified.source
        )

        # 4. Call AI for Draft (DIP)
        ai_output = await self.ai_provider.generate_response(unified, PROPERTY_CONTEXT)

        # 5. Business Rules for Action (Logic from Part 1)
        action = self._determine_action(ai_output)

        # 6. Save the AI's Outbound Draft (Part 2)
        # We store the draft, the score, and the category for auditing
        await self.repo.save_message(
            conv_id=conv_id,
            direction="outbound",
            content=ai_output.drafted_reply,
            source=unified.source,
            ai_data=ai_output,
            action=action
        )

        return FinalResponse(
            message_id=unified.message_id,
            query_type=ai_output.query_type,
            drafted_reply=ai_output.drafted_reply,
            confidence_score=ai_output.confidence_score,
            action=action
        )

    def _determine_action(self, ai_output) -> ActionType:
        """
        Pure business logic remains untouched (Open/Closed Principle).
        """
        if ai_output.query_type == QueryType.COMPLAINT:
            return ActionType.ESCALATE
        
        if ai_output.confidence_score >= 0.85:
            return ActionType.AUTO_SEND
        if ai_output.confidence_score >= 0.60:
            return ActionType.AGENT_REVIEW
        
        return ActionType.ESCALATE