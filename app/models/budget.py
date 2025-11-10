"""
Budget model for managing user budgets in different categories.
"""

import uuid
from app.extensions import db
from datetime import date, datetime
from sqlalchemy import Column, DateTime, Float, String, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    category = Column(String(50), nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    budget_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.today())
    updated_at = Column(DateTime, default=datetime.today(), onupdate=datetime.today())

    user = relationship("User", back_populates="budgets")
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', 'month', 'year', name='unique_budget_per_category_month'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'month': self.month,
            'year': self.year,
            'budget_amount': self.budget_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get('user_id'),
            category=data.get('category'),
            month=data.get('month'),
            year=data.get('year'),
            budget_amount=data.get('budget_amount'),
            created_at=data.get('created_at', datetime.today()),
            updated_at=data.get('updated_at', datetime.today())
        )
