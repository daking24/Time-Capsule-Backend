from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base
import uuid

class Letter(Base):
    __tablename__ = "letters"

    id = Column(Integer, primary_key=True, index=True)
    # in a real app, use UUIDs. For simplicity/MVP, Integer auto-increment is fine
    # but let's try to be robust:
    # public_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    email = Column(String, index=True)
    content_text = Column(Text, nullable=True)
    
    media_url = Column(String, nullable=True)
    media_type = Column(String, default="text") # text, video, audio, image
    
    delivery_date = Column(DateTime)
    
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
