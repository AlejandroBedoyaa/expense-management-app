"""
StoreCategory model for storing store and category mappings.
"""
import uuid
from app.extensions import db
from datetime import datetime, date
from sqlalchemy import Column, DateTime, String, Date, ForeignKey
from sqlalchemy.orm import relationship

class StoreCategory(db.Model):
    
    __tablename__ = 'store_categories'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.today())
    updated_at = Column(DateTime, default=datetime.today(), onupdate=datetime.today())

    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="store_categories")
    
    def __repr__(self):
        return f'<StoreCategory {self.store_name}: {self.category}>'
    
    def to_dict(self):
        """Convert store category to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'store_name': self.store_name,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create store category from dictionary."""
        return cls(
            store_name=data.get('store_name'),
            category=data.get('category'),
            created_at=data.get('created_at', datetime.today()),
            updated_at=data.get('updated_at', datetime.today()),
            
            user_id=data.get('user_id')
        )