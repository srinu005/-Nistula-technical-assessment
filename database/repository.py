from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import UnifiedMessage, AIResult
from models.enums import ActionType

class MessagingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve_guest_and_conversation(self, data: UnifiedMessage):
        """
        Logic: 
        1. Check if guest exists by phone or channel ID.
        2. Create guest if not found.
        3. Link to/create an active conversation.
        """
        # Note: In a full app, we'd use SQLAlchemy ORM models. 
        # For Part 2, we use SQL to stay close to the schema you designed.
        
        # 1. Identity Resolution (Simplified)
        query = text("""
            INSERT INTO guests (full_name, external_identities)
            VALUES (:name, :ident)
            ON CONFLICT (full_name) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        guest_id = (await self.session.execute(query, {
            "name": data.guest_name,
            "ident": f'{{"{data.source}": "resolved"}}'
        })).scalar()

        # 2. Get/Create Conversation
        conv_query = text("""
            INSERT INTO conversations (guest_id, last_message_at)
            VALUES (:g_id, NOW())
            ON CONFLICT DO NOTHING
            RETURNING id
        """)
        conv_id = (await self.session.execute(conv_query, {"g_id": guest_id})).scalar()
        
        # Fallback if conversation already exists
        if not conv_id:
            conv_id = (await self.session.execute(
                text("SELECT id FROM conversations WHERE guest_id = :g_id LIMIT 1"), 
                {"g_id": guest_id}
            )).scalar()

        return conv_id

    async def save_message(self, conv_id: str, direction: str, content: str, source: str, ai_data: AIResult = None, action: str = None):
        """
        Saves both inbound guest messages and outbound AI drafts.
        """
        query = text("""
            INSERT INTO messages (
                conversation_id, direction, source, content, 
                query_type, ai_confidence_score, status
            ) VALUES (
                :c_id, :dir, :src, :content, 
                :q_type, :score, :status
            )
        """)
        
        status = "ai_drafted" if direction == "outbound" else None
        if action == "auto_send": status = "auto_sent"
        
        await self.session.execute(query, {
            "c_id": conv_id,
            "dir": direction,
            "src": source,
            "content": content,
            "q_type": ai_data.query_type if ai_data else None,
            "score": ai_data.confidence_score if ai_data else None,
            "status": status
        })
        await self.session.commit()