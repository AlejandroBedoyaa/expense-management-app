"""
StoreCategory model for storing store and category mappings.
"""
from app.extensions import db
from datetime import date
from sqlalchemy import Column, Integer, String, Date

class StoreCategory(db.Model):
    
    __tablename__ = 'store_categories'
    
    id = Column(Integer, primary_key=True)
    store_name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)
    created_at = Column(Date, default=date.today)
    
    def __repr__(self):
        return f'<StoreCategory {self.store_name}: {self.category}>'
    
    def to_dict(self):
        """Convert store category to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'store_name': self.store_name,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create store category from dictionary."""
        return cls(
            store_name=data.get('store_name'),
            category=data.get('category'),
            created_at=data.get('created_at', date.today()),
        )