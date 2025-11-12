"""
Income Service Module
"""
from sympy import limit
from app.models.income import Income
from app.extensions import db
from typing import List, Dict, Optional
import os
from datetime import date
from app.config import Config

class IncomeService:

    @staticmethod
    def create_income(data: Dict) -> Income:
        """Create a new income record."""
        income = Income.from_dict(data)
        db.session.add(income)
        db.session.commit()
        return income
    
    @staticmethod
    def get_incomes_by_user_id(user_id: str, limit: int = None) -> List[Income]:
        """Get incomes by user ID."""
        query = Income.query.filter_by(user_id=user_id).order_by(Income.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_all_incomes(limit: int = None) -> List[Income]:
        """Get all incomes."""
        query = Income.query.order_by(Income.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def update_income(income_id: str, data: Dict) -> Optional[Income]:
        """Update an existing income."""
        income = Income.query.get(income_id)
        if not income:
            return None
        
        for key, value in data.items():
            if hasattr(income, key):
                setattr(income, key, value)
        
        db.session.commit()
        return income
    
income_service = IncomeService()