from fastapi import FastAPI, Depends, HTTPException
from models.schemas import WebhookPayload, FinalResponse
from services.ai_service import ClaudeProvider
from services.orchestrator import MessageOrchestrator

app = FastAPI(title="Nistula Guest API")

# Dependency Injection
def get_orchestrator():
    return MessageOrchestrator(ClaudeProvider())

@app.get("/")
def health_check():
    return {"status": "online", "system": "Nistula Messaging"}

@app.post("/webhook/message", response_model=FinalResponse)
async def handle_webhook(
    payload: WebhookPayload,
    orchestrator: MessageOrchestrator = Depends(get_orchestrator)
):
    try:
        return await orchestrator.process(payload)
    except Exception as e:
        # Graceful error handling for the guest
        raise HTTPException(status_code=500, detail=str(e))