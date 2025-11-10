"""
Income model for storing income records.
"""
import uuid
from app.extensions import db
from datetime import date, datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

class Income(db.Model):
    __tablename__ = "incomes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    income_date = Column(Date, default=date.today)
    description = Column(String(500), nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.today())
    updated_at = Column(DateTime, default=datetime.today(), onupdate=datetime.today())

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
            "income_date": self.income_date.isoformat() if self.income_date else None,
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
            income_date=data.get("income_date", date.today()),
            description=data.get("description", None),
            created_at=data.get("created_at", datetime.today()),
            updated_at=data.get("updated_at", datetime.today()),
            user_id=data.get("user_id"),
        )
