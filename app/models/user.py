from app.extensions import db
import uuid
from datetime import datetime, date
from sqlalchemy import Column, DateTime, String, Float
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(String(32), unique=True, nullable=False)
    username = Column(String(128), nullable=True)
    accumulated_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.today())
    updated_at = Column(DateTime, default=datetime.today(), onupdate=datetime.today())

    expenses = relationship("Expense", back_populates="user")
    store_categories = relationship("StoreCategory", back_populates="user")
    incomes = relationship("Income", back_populates="user")
    budgets = relationship("Budget", back_populates="user")

    def __repr__(self):
        return f'<User {self.telegram_id}>'

    
    def to_dict(self):
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'accumulated_balance': self.accumulated_balance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            telegram_id=data.get('telegram_id'),
            username=data.get('username'),
            accumulated_balance=data.get('accumulated_balance', 0.0),
            created_at=data.get('created_at', datetime.today()),
            updated_at=data.get('updated_at', datetime.today())
        )