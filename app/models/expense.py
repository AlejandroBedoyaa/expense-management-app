"""
Expense model for storing expense records.
"""
from app.extensions import db
from datetime import date
from sqlalchemy import Column, Integer, Float, String, Date

class Expense(db.Model):
    
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    payment_concept = Column(String(100), nullable=True)
    note = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=16)  # Tax/IVA percentage
    total = Column(Float, nullable=True)
    file_path = Column(String(255), nullable=True)  # Path to receipt image
    payment_date = Column(Date, default=date.today)
    created_at = Column(Date, default=date.today)
    
    def __repr__(self):
        return f'<Expense {self.payment_concept}: ${self.total}>'
    
    def to_dict(self):
        """Convert expense to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'payment_concept': self.payment_concept,
            'note': self.note,
            'category': self.category,
            'subtotal': self.subtotal,
            'tax': self.tax,
            'total': self.total,
            'file_path': self.file_path,
            'payment_date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create expense from dictionary."""
        return cls(
            payment_concept=data.get('payment_concept'),
            note=data.get('note'),
            category=data.get('category'),
            subtotal=data.get('subtotal', 0.0),
            tax=data.get('tax', 16),
            total=data.get('total'),
            file_path=data.get('file_path'),
            payment_date=data.get('payment_date', date.today()),
            created_at=data.get('created_at', date.today()),
        )