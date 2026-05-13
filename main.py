from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Internal Imports
from models.schemas import WebhookPayload, FinalResponse
from services.ai_service import ClaudeProvider
from services.orchestrator import MessageOrchestrator
from database.db_manager import get_db
from database.repository import MessagingRepository

app = FastAPI(title="Nistula Guest API - AI-Powered Messaging")

# --- Dependency Injection Factory ---

async def get_orchestrator(db: AsyncSession = Depends(get_db)):
    """
    This factory assembles our system's components for every request.
    It follows the Dependency Inversion Principle.
    """
    # 1. Create the Data Access Layer (Repository)
    repo = MessagingRepository(db)
    
    # 2. Create the AI Provider
    ai_provider = ClaudeProvider()
    
    # 3. Inject both into the Orchestrator
    return MessageOrchestrator(ai_provider, repo)


# --- Endpoints ---

@app.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Checks if both the API and the Database are alive.
    """
    from sqlalchemy import text
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "online", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database": str(e)}


@app.post("/webhook/message", response_model=FinalResponse)
async def handle_webhook(
    payload: WebhookPayload,
    orchestrator: MessageOrchestrator = Depends(get_orchestrator)
):
    """
    The main entry point for inbound guest messages.
    Everything from normalization to AI drafting and DB persistence
    is handled by the orchestrator.
    """
    try:
        # The orchestrator now handles both AI and DB saving
        return await orchestrator.process(payload)
    except Exception as e:
        # Senior Tip: Log the actual error to your console, 
        # but don't leak stack traces to the guest.
        print(f"CRITICAL ERROR in Webhook: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing your message."
        )