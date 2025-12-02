"""
Service layer for balance and financial calculations.
"""
from app.models.income import Income
from app.models.expense import Expense
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)


class BalanceService:
    
    def get_monthly_balance(self, user_id, month=None, year=None):
        """
        Calculate balance for a specific month.
        Balance = Total Incomes - Total Expenses
        """
        try:
            if not month or not year:
                today = date.today()
                month = today.month
                year = today.year
            
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            
            total_incomes = Income.query.filter(
                Income.user_id == user_id,
                Income.income_date >= start_date,
                Income.income_date < end_date
            ).with_entities(Income.amount).all()
            
            income_sum = sum(income.amount for income in total_incomes)
            
            total_expenses = Expense.query.filter(
                Expense.user_id == user_id,
                Expense.payment_date >= start_date,
                Expense.payment_date < end_date
            ).with_entities(Expense.total).all()
            
            expense_sum = sum(expense.total for expense in total_expenses)
            
            balance = income_sum - expense_sum
            
            return {
                'month': month,
                'year': year,
                'total_incomes': income_sum,
                'total_expenses': expense_sum,
                'balance': balance,
                'balance_percentage': (balance / income_sum * 100) if income_sum > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating monthly balance: {str(e)}")
            raise
    
    def get_total_balance(self, user_id):
        """
        Calculate total balance (all time).
        """
        try:
            total_incomes = Income.query.filter_by(user_id=user_id)\
                .with_entities(Income.amount).all()
            income_sum = sum(income.amount for income in total_incomes)
            
            total_expenses = Expense.query.filter_by(user_id=user_id)\
                .with_entities(Expense.total).all()
            expense_sum = sum(expense.total for expense in total_expenses)
            
            balance = income_sum - expense_sum
            
            return {
                'total_balance': balance
            }
            
        except Exception as e:
            logger.error(f"Error calculating total balance: {str(e)}")
            raise
    
    def get_category_expenses(self, user_id, month=None, year=None):
        """Get expenses grouped by category for a specific month."""
        try:
            if not month or not year:
                today = date.today()
                month = today.month
                year = today.year
            
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            
            expenses = Expense.query.filter(
                Expense.user_id == user_id,
                Expense.payment_date >= start_date,
                Expense.payment_date < end_date
            ).all()
            
            categories = {}
            for expense in expenses:
                category = expense.category or 'uncategorized'
                if category not in categories:
                    categories[category] = {
                        'total': 0,
                        'count': 0
                    }
                categories[category]['total'] += expense.total
                categories[category]['count'] += 1
            
            return categories
            
        except Exception as e:
            logger.error(f"Error getting category expenses: {str(e)}")
            raise
    
    def get_financial_summary(self, user_id):
        """Get comprehensive financial summary for current month."""
        try:
            current = self.get_monthly_balance(user_id)
            categories = self.get_category_expenses(user_id)
            
            sorted_categories = sorted(
                categories.items(), 
                key=lambda x: x[1]['total'], 
                reverse=True
            )
            
            return {
                'balance': current,
                'top_categories': sorted_categories[:5],  # Top 5 categorías
                'all_categories': sorted_categories
            }
            
        except Exception as e:
            logger.error(f"Error getting financial summary: {str(e)}")
            raise
    
    def get_daily_balance_chart(self, user_id):
        """Get daily income and expense data for chart visualization (last 3 months)."""
        try:
            from dateutil.relativedelta import relativedelta
            
            # Calculate date range: 3 months ago to today
            end_date = date.today()
            start_date = end_date - relativedelta(months=3)
            
            # Get all incomes for the period
            incomes = Income.query.filter(
                Income.user_id == user_id,
                Income.income_date >= start_date,
                Income.income_date <= end_date
            ).all()
            
            # Get all expenses for the period
            expenses = Expense.query.filter(
                Expense.user_id == user_id,
                Expense.payment_date >= start_date,
                Expense.payment_date <= end_date
            ).all()
            
            # Create dictionary to aggregate by date
            daily_data = {}
            
            # Aggregate incomes by date
            for income in incomes:
                date_key = income.income_date.strftime('%Y-%m-%d')
                if date_key not in daily_data:
                    daily_data[date_key] = {'income': 0.0, 'expense': 0.0}
                daily_data[date_key]['income'] += income.amount
            
            # Aggregate expenses by date
            for expense in expenses:
                date_key = expense.payment_date.strftime('%Y-%m-%d')
                if date_key not in daily_data:
                    daily_data[date_key] = {'income': 0.0, 'expense': 0.0}
                daily_data[date_key]['expense'] += expense.total
            
            # Convert to list format sorted by date
            chart_data = [
                {
                    'date': date_str,
                    'income': round(values['income'], 2),
                    'expense': round(values['expense'], 2)
                }
                for date_str, values in sorted(daily_data.items())
            ]
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error getting daily balance chart: {str(e)}")
            raise


# Singleton instance
balance_service = BalanceService()
