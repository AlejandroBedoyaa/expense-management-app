"""
Income model for storing income records.
"""
import uuid
from app.extensions import db
from datetime import date
from sqlalchemy import Boolean, Column, Float, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

class Income(db.Model):
    __tablename__ = "incomes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    income_day = Column(Integer, nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_type = Column(String(20), nullable=True, default=None)
    description = Column(String(500), nullable=True, default=None)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="incomes")

    def __repr__(self):
        return f"<Income {self.source}: ${self.amount}>"
    
    def to_dict(self):
        """Convert income to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "source": self.source,
            "amount": self.amount,
            "income_day": self.income_day,
            "is_recurring": self.is_recurring,
            "recurrence_type": self.recurrence_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create income from dictionary."""
        return cls(
            source=data.get("source"),
            amount=data.get("amount"),
            income_day=data.get("income_day"),
            is_recurring=data.get("is_recurring", False),
            recurrence_type=data.get("recurrence_type", None),
            description=data.get("description", None),
            created_at=data.get("created_at", date.today()),
            updated_at=data.get("updated_at", date.today()),
            user_id=data.get("user_id"),
        )
