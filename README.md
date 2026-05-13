#  Nistula-technical-assessment

Hi! This is my submission for the Nistula Backend System. I built a system that takes messages from guests (like on WhatsApp or Airbnb), uses AI to draft a reply based on our villa's rules, and saves everything into a database so we don't lose track of the conversation.
# Tech Stack

    FastAPI: Used for the web server and webhook.

    Claude 3.5 Sonnet: The AI "brain" that drafts the replies.

    PostgreSQL: Where I’m storing guest profiles and chat history.

    Docker: So you can run everything without installing stuff on your computer.

# How to Run the Project

I've containerized everything to make it easy to start.

    Clone the repo to your local machine.

    Create a .env file in the root folder and add your API key:
    code Text

    ANTHROPIC_API_KEY=your_key_here
    CLAUDE_MODEL=claude-sonnet-4-20250514
    DATABASE_URL=postgresql+asyncpg://nistula_user:nistula_password@db:5432/nistula_db

    Start Docker:
    code Bash

    docker-compose up --build

    Test it: You can use the tests/live_test.py script I wrote to send some example messages to the server!
    code Bash

    python tests/live_test.py

# My Confidence Scoring Logic

One of the main requirements was to decide when the AI should send a message automatically and when a human needs to step in. Here is how I set up the logic in the MessageOrchestrator:
1. The AI Score

When I send the guest's message to Claude, I ask it to provide a confidence_score between 0.0 and 1.0. This is based on how well the "Property Context" (the villa info) answers the guest's specific question.
2. The Action Rules

I created three levels for the action field based on that score:

    auto_send (Score > 0.85): If the AI is very sure and the answer is clearly in our villa info, it’s safe to send.

    agent_review (Score 0.60 - 0.85): If the AI is a bit unsure or the question is tricky, we save the draft but wait for a human to check it.

    escalate (Score < 0.60): If the AI is confused, we don't send anything and flag it for urgent human help.

3. The "Safety First" Override (Complaints)

I added a special rule for complaints. Even if the AI is 100% confident it has a good apology, any message classified as a "complaint" is automatically set to escalate. I don't think it's a good idea to let an AI handle an unhappy guest without a human knowing about it!
# Database Structure

I set up a few tables in Postgres to keep things organized:

    guests: One record for every unique guest.

    conversations: Groups messages together.

    messages: Stores the actual text, the AI's score, and whether the message was auto-sent or escalated.

# Testing

I included a test suite in the tests/ folder.

    Run docker-compose exec api python -m pytest to see the logic tests.

    These tests check that complaints are escalated properly and that the unified schema is working correctly.
