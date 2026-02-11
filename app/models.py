import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import relationship

from app.db import Base


def generate_uuid():
    return str(uuid.uuid4())


class Slot(Base):
    __tablename__ = "slots"

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    code = Column(String(32), unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    current_item_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # item will be in database  only relationship is defined here, so we need to set cascade to delete items when slot is deleted
    items = relationship("Item",back_populates="slot",cascade="all, delete-orphan")



class Item(Base):
    __tablename__ = "items"

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    # system may allow negative price for promotional items, so we should not set price as unsigned
    price = Column(Integer, nullable=False)
    slot_id = Column(CHAR(36), ForeignKey("slots.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    __table_args__ = (CheckConstraint("price > 0", name="check_price_positive"),)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    slot = relationship("Slot", back_populates="items")
