import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/webhook/message"

TEST_CASES = [
    {
        "name": "Scenario 1: High Confidence Availability",
        "payload": {
            "source": "whatsapp",
            "guest_name": "Rahul Sharma",
            "message": "Is the villa available from April 20 to 24? What is the rate for 2 adults?",
            "timestamp": "2026-05-05T10:30:00Z",
            "booking_ref": "NIS-2024-0891",
            "property_id": "villa-b1"
        }
    },
    {
        "name": "Scenario 2: General Enquiry (WiFi)",
        "payload": {
            "source": "airbnb",
            "guest_name": "Jessica",
            "message": "Hey! What is the WiFi password again?",
            "timestamp": "2026-05-05T11:00:00Z",
            "property_id": "villa-b1"
        }
    },
    {
        "name": "Scenario 3: Complaint (AC Failure)",
        "payload": {
            "source": "booking_com",
            "guest_name": "Amit",
            "message": "The AC is making a loud noise and not cooling. This is very annoying.",
            "timestamp": "2026-05-05T12:00:00Z",
            "property_id": "villa-b1"
        }
    }
]

async def run_tests():
    async with httpx.AsyncClient() as client:
        for case in TEST_CASES:
            print(f"\n--- Running: {case['name']} ---")
            try:
                response = await client.post(BASE_URL, json=case['payload'], timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    print(f"Query Type: {data['query_type']}")
                    print(f"Action:     {data['action']}")
                    print(f"Score:      {data['confidence_score']}")
                    print(f"Reply:      {data['drafted_reply']}")
                else:
                    print(f"FAILED: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_tests())