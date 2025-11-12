from app.extensions import db
import uuid
from datetime import datetime, date
from sqlalchemy import Column, DateTime, String, Float, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(String(32), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=True)
    password = Column(String(256), nullable=True)
    vinculation_token = Column(String(64), nullable=True)
    vinculation_token_created = Column(DateTime, nullable=True)
    is_linked = Column(Boolean, default=False)
    accumulated_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.today())
    updated_at = Column(DateTime, default=datetime.today(), onupdate=datetime.today())

    expenses = relationship("Expense", back_populates="user")
    store_categories = relationship("StoreCategory", back_populates="user")
    incomes = relationship("Income", back_populates="user")
    budgets = relationship("Budget", back_populates="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.telegram_id}>'

    
    def to_dict(self):
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'email': self.email,
            'password': self.password,
            'vinculation_token': self.vinculation_token,
            'vinculation_token_created': self.vinculation_token_created.isoformat() if self.vinculation_token_created else None,
            'is_linked': self.is_linked,
            'accumulated_balance': self.accumulated_balance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            telegram_id=data.get('telegram_id'),
            email=data.get('email'),
            password=data.get('password'),
            vinculation_token=data.get('vinculation_token'),
            vinculation_token_created=data.get('vinculation_token_created'),
            is_linked=data.get('is_linked', False),
            accumulated_balance=data.get('accumulated_balance', 0.0),
            created_at=data.get('created_at', datetime.today()),
            updated_at=data.get('updated_at', datetime.today())
        )