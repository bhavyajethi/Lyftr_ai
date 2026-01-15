import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import Base, engine, SessionLocal
from app.models import Message

client = TestClient(app)

class TestMessages(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # Seed Data
        db = SessionLocal()
        msgs = [
            Message(message_id="m1", from_msisdn="+111", to_msisdn="+999", ts="2025-01-01T10:00:00Z", text="Apple", created_at="Z"),
            Message(message_id="m2", from_msisdn="+111", to_msisdn="+999", ts="2025-01-02T10:00:00Z", text="Banana", created_at="Z"),
            Message(message_id="m3", from_msisdn="+222", to_msisdn="+999", ts="2025-01-03T10:00:00Z", text="Cherry", created_at="Z")
        ]
        db.add_all(msgs)
        db.commit()
        db.close()

    def test_pagination(self):
        # limit=1
        resp = client.get("/messages", params={"limit": 1, "offset": 0})
        data = resp.json()
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["total"], 3)
        self.assertEqual(data["data"][0]["message_id"], "m1")

    def test_filter_from(self):
        # FIX: Use params dict to safely encode the '+' sign
        resp = client.get("/messages", params={"from": "+222"})
        data = resp.json()
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["message_id"], "m3")