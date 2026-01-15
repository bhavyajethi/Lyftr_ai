import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import Base, engine, SessionLocal
from app.models import Message

client = TestClient(app)

class TestStats(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        # Add 2 messages from +111
        db.add(Message(message_id="a1", from_msisdn="+111", to_msisdn="+99", ts="2025-01-01T10:00:00Z", text="A", created_at="Z"))
        db.add(Message(message_id="a2", from_msisdn="+111", to_msisdn="+99", ts="2025-01-02T10:00:00Z", text="B", created_at="Z"))
        db.commit()
        db.close()

    def test_stats_counts(self):
        resp = client.get("/stats")
        data = resp.json()
        self.assertEqual(data["total_messages"], 2)
        self.assertEqual(data["senders_count"], 1)
        self.assertEqual(data["messages_per_sender"][0]["from"], "+111")
        self.assertEqual(data["messages_per_sender"][0]["count"], 2)