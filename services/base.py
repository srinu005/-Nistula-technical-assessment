from abc import ABC, abstractmethod
from models.schemas import UnifiedMessage, AIResult

class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, message: UnifiedMessage, context: str) -> AIResult:
        pass