from fastapi import FastAPI, Depends
from core.config import settings
from models.schemas import WebhookPayload, FinalResponse
from services.ai_service import ClaudeProvider
from services.orchestrator import MessageOrchestrator

app = FastAPI(title="Nistula API")

# Dependency Injection setup
def get_orchestrator():
    # We can easily swap ClaudeProvider() for another provider here
    ai_provider = ClaudeProvider()
    return MessageOrchestrator(ai_provider)

@app.post("/webhook/message", response_model=FinalResponse)
async def handle_message(
    payload: WebhookPayload, 
    orchestrator: MessageOrchestrator = Depends(get_orchestrator)
):
    return orchestrator.process(payload)