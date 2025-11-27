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
    
    @staticmethod
    def delete_income(income_id: str) -> bool:
        """Delete an existing income."""
        income = Income.query.get(income_id)
        if not income:
            return False
        db.session.delete(income)
        db.session.commit()
        return True
    
    @staticmethod
    def get_monthly_incomes(user_id: str) -> Dict:
        """Get total income amount for current month with comparison to previous month."""
        # Month names
        month_names = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
        
        today = date.today()
        current_month = today.month
        current_year = today.year
        
        # Calculate current month date range
        current_start_date = date(current_year, current_month, 1)
        if current_month == 12:
            current_end_date = date(current_year + 1, 1, 1)
        else:
            current_end_date = date(current_year, current_month + 1, 1)

        # Get current month incomes
        current_monthly_incomes = Income.query.filter(
            Income.user_id == user_id,
            Income.income_date >= current_start_date,
            Income.income_date < current_end_date
        ).all()
        
        current_total = sum(income.amount for income in current_monthly_incomes)
        
        # Calculate previous month date range
        if current_month == 1:
            previous_month = 12
            previous_year = current_year - 1
        else:
            previous_month = current_month - 1
            previous_year = current_year
            
        previous_start_date = date(previous_year, previous_month, 1)
        if previous_month == 12:
            previous_end_date = date(previous_year + 1, 1, 1)
        else:
            previous_end_date = date(previous_year, previous_month + 1, 1)
        
        # Get previous month incomes
        previous_monthly_incomes = Income.query.filter(
            Income.user_id == user_id,
            Income.income_date >= previous_start_date,
            Income.income_date < previous_end_date
        ).all()
        
        previous_total = sum(income.amount for income in previous_monthly_incomes)
        
        # Calculate percentage change
        if previous_total > 0:
            percentage_change = ((current_total - previous_total) / previous_total) * 100
        else:
            percentage_change = 0.0 if current_total == 0 else 100.0
        
        return {
            'month': month_names.get(current_month, ''),
            'year': current_year,
            'total_incomes': round(current_total, 2),
            'previous_month_total': round(previous_total, 2),
            'percentage_change': round(percentage_change, 2),
            'improvement': percentage_change > 0  # True if income increased
        }
    
income_service = IncomeService()