import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from api.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bank_account_info = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("ReceiptItem", back_populates="session", cascade="all, delete-orphan")

class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="items")
    claims = relationship("Claim", back_populates="item", cascade="all, delete-orphan")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String, ForeignKey("receipt_items.id"), nullable=False)
    user_name = Column(String, nullable=False)
    amount_claimed = Column(Float, nullable=False)  # Could be fraction or fixed value.
    payment_file_path = Column(String, nullable=True) # Path to the uploaded confirmation file

    # Relationships
    item = relationship("ReceiptItem", back_populates="claims")
