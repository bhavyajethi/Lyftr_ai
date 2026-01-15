# app/models.py
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"

    # Strict schema from assignment [cite: 190-201]
    message_id = Column(String, primary_key=True, index=True)
    from_msisdn = Column(String, nullable=False)
    to_msisdn = Column(String, nullable=False)
    ts = Column(String, nullable=False)  # ISO-8601 UTC string
    text = Column(Text, nullable=True)
    created_at = Column(String, nullable=False) # Server time