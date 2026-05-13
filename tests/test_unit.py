import pytest
from unittest.mock import AsyncMock
from services.orchestrator import MessageOrchestrator
from models.schemas import WebhookPayload, AIResult
from models.enums import ActionType, QueryType

@pytest.mark.asyncio
async def test_complaint_always_escalates():
    # Setup: Create a mock AI provider that is highly confident but sees a complaint
    mock_ai = AsyncMock()
    mock_ai.generate_response.return_value = AIResult(
        query_type=QueryType.COMPLAINT,
        drafted_reply="I'm sorry your AC is broken.",
        confidence_score=0.99
    )
    
    orchestrator = MessageOrchestrator(mock_ai)
    payload = WebhookPayload(
        source="whatsapp",
        guest_name="Test Guest",
        message="The AC is broken!",
        timestamp="2026-05-05T10:30:00Z",
        property_id="villa-b1"
    )

    result = await orchestrator.process(payload)

    # Assert: Even with 0.99 confidence, a complaint must ESCALATE
    assert result.action == ActionType.ESCALATE
    assert result.query_type == QueryType.COMPLAINT

@pytest.mark.asyncio
async def test_low_confidence_escalates():
    mock_ai = AsyncMock()
    mock_ai.generate_response.return_value = AIResult(
        query_type=QueryType.GENERAL_ENQUIRY,
        drafted_reply="I am not sure...",
        confidence_score=0.30
    )
    
    orchestrator = MessageOrchestrator(mock_ai)
    payload = WebhookPayload(
        source="direct",
        guest_name="Confused Guest",
        message="Do you have a pet dragon?",
        timestamp="2026-05-05T10:30:00Z",
        property_id="villa-b1"
    )

    result = await orchestrator.process(payload)
    assert result.action == ActionType.ESCALATE