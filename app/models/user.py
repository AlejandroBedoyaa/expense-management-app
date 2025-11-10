from app.extensions import db
import uuid
from datetime import date
from sqlalchemy import Column, DateTime, String, Date
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(String(32), unique=True, nullable=False)
    username = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=date.today)
    updated_at = Column(DateTime, default=date.today, onupdate=date.today)

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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }