import json
from anthropic import AsyncAnthropic
from .base import LLMProvider
from models.schemas import UnifiedMessage, AIResult
from core.config import settings

class ClaudeProvider(LLMProvider):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_response(self, message: UnifiedMessage, context: str) -> AIResult:
        system_prompt = f"""
        You are a guest relations manager for Nistula villas. 
        Context: {context}
        
        Strictly return ONLY JSON with:
        - query_type (choices: pre_sales_availability, pre_sales_pricing, post_sales_checkin, special_request, complaint, general_enquiry)
        - drafted_reply (polite, accurate based on context)
        - confidence_score (0.0 to 1.0 based on how well the context covers the query)
        """
        
        user_input = f"Guest: {message.guest_name}\nMessage: {message.message_text}"

        response = await self.client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}]
        )
        
        # Parse the JSON response from Claude
        try:
            raw_content = response.content[0].text
            data = json.loads(raw_content)
            return AIResult(**data)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # Fallback if AI fails to return valid JSON
            return AIResult(
                query_type="general_enquiry",
                drafted_reply="I apologize, but I'm having trouble processing that request. A human agent will be with you shortly.",
                confidence_score=0.0
            )