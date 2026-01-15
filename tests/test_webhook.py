import unittest
import json
import hmac
import hashlib
from fastapi.testclient import TestClient
from app.main import app
from app.storage import Base, engine
from app.config import get_settings

client = TestClient(app)

class TestWebhook(unittest.TestCase):
    def setUp(self):
        # Reset DB before each test
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # 1. Dynamically load the secret (No hardcoding)
        # This picks up "mysecretkey" from your .env file
        self.secret = get_settings().WEBHOOK_SECRET
        
        if not self.secret:
            raise ValueError("WEBHOOK_SECRET is missing from .env configuration")

    def test_valid_insert(self):
        payload = {
            "message_id": "m1", "from": "+911", "to": "+141", 
            "ts": "2025-01-01T10:00:00Z", "text": "Hi"
        }
        
        # FIX: Serialize ONCE to ensure exact match between signature and request
        payload_bytes = json.dumps(payload).encode('utf-8')
        
        # Sign the bytes
        sig = hmac.new(self.secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
        
        # Send the EXACT bytes using content=... (instead of json=...)
        response = client.post(
            "/webhook", 
            content=payload_bytes, 
            headers={"Content-Type": "application/json", "X-Signature": sig}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_duplicate_idempotency(self):
        payload = {
            "message_id": "m1", "from": "+911", "to": "+141", 
            "ts": "2025-01-01T10:00:00Z", "text": "Hi"
        }
        
        payload_bytes = json.dumps(payload).encode('utf-8')
        sig = hmac.new(self.secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
        
        # First call
        resp1 = client.post(
            "/webhook", 
            content=payload_bytes, 
            headers={"Content-Type": "application/json", "X-Signature": sig}
        )
        self.assertEqual(resp1.status_code, 200)
        
        # Second call
        resp2 = client.post(
            "/webhook", 
            content=payload_bytes, 
            headers={"Content-Type": "application/json", "X-Signature": sig}
        )
        self.assertEqual(resp2.status_code, 200)

    def test_invalid_signature(self):
        payload = {"message_id": "m2", "from": "+911", "to": "+141", "ts": "Z", "text": "Hacker"}
        # We can let this one fail naturally
        response = client.post("/webhook", json=payload, headers={"X-Signature": "fake123"})
        self.assertEqual(response.status_code, 401)