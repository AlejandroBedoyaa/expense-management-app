"""
Service layer for managing expenses and processing tickets.
"""
from app.models.expense import Expense
from app.extensions import db
from app.services.ocr_service import ocr_service
from typing import List, Dict, Optional
import os
from datetime import date
from app.config import Config

from app.utils.helpers import parse_date

class ExpenseService:
    """Service for managing expenses and processing tickets."""
    
    @staticmethod
    def create_expense(data: Dict) -> Expense:
        """Create a new expense record."""
        expense = Expense.from_dict(data)
        db.session.add(expense)
        db.session.commit()
        return expense
    
    @staticmethod
    def get_expense_by_id(expense_id: str) -> Optional[Expense]:
        """Get expense by ID."""
        return Expense.query.get(expense_id)
    
    @staticmethod
    def get_all_expenses(user_id: str = None, limit: int = 10) -> List[Expense]:
        """Get all expenses for a user, optionally limited."""
        query = Expense.query.filter_by(user_id=user_id).order_by(Expense.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_expenses_by_category(category: str) -> List[Expense]:
        """Get expenses filtered by category."""
        return Expense.query.filter_by(category=category).order_by(Expense.created_at.desc()).all()
    
    @staticmethod
    def get_expenses_by_date_range(start_date: date, end_date: date) -> List[Expense]:
        """Get expenses within a date range."""
        return Expense.query.filter(
            Expense.created_at.between(start_date, end_date)
        ).order_by(Expense.created_at.desc()).all()
    
    @staticmethod
    def update_expense(expense_id: str, data: Dict) -> Optional[Expense]:
        """Update an existing expense."""
        expense = Expense.query.get(expense_id)
        if not expense:
            return None
        
        for key, value in data.items():
            if hasattr(expense, key):
                setattr(expense, key, value)
        
        db.session.commit()
        return expense
    
    @staticmethod
    def delete_expense(expense_id: str) -> bool:
        """Delete an expense by ID."""
        expense = Expense.query.get(expense_id)
        if not expense:
            return False
        
        # Delete associated ticket file if exists
        if expense.file_name and os.path.exists(expense.file_name):
            try:
                os.remove(expense.file_name)
            except OSError:
                pass  # File deletion failed, but continue with DB deletion
        
        db.session.delete(expense)
        db.session.commit()
        return True
    
    @staticmethod
    def process_ticket_image(user_id: str, image_path: str, save_image: bool = True) -> Dict:
        """
        Process ticket image using OCR and return extracted data.
        
        Args:
            user_id: ID of the user
            image_path: Path to the ticket image
            save_image: Whether to save the image to files directory
            
        Returns:
            Dictionary with extracted expense data
        """
        try:
            
            # Extract data using OCR
            ticket_data = ocr_service.extract_ticket_data(image_path)

            # Prepare expense data
            expense_data = {
                'payment_concept': ticket_data.get('payment_concept').upper() or 'ticket',
                'subtotal': ticket_data.get('subtotal') or 0.0,
                'category': (ticket_data.get('category') or 'uncategorized').lower(),
                'tax': ticket_data.get('tax') or 16,
                'total': ticket_data.get('total') or 0.0,
                'payment_date': parse_date(ticket_data.get('payment_date') or date.today()),
                'user_id': user_id
            }

            # Save image if requested
            if save_image:
                saved_path = ExpenseService._save_ticket_image(user_id, image_path)
                expense_data['file_name'] = saved_path

            # Add raw OCR data for reference
            # expense_data['ocr_data'] = ticket_data
            
            return expense_data
            
        except Exception as e:
            raise Exception(f"{str(e)}")
    
    @staticmethod
    def _save_ticket_image(user_id: str, image_path: str) -> str:
        """Save ticket image to files directory."""
        import shutil
        from app.utils.helpers import generate_secure_filename
        # Create files directory if it doesn't exist
        file_dir = Config.FILE_FOLDER
        os.makedirs(file_dir, exist_ok=True)

        # Generate secure file_name with timestamp
        file_name = generate_secure_filename(os.path.basename(image_path))
        destination_dir = os.path.join(Config.FILE_FOLDER, user_id)
        os.makedirs(destination_dir, exist_ok=True)
        destination_path = os.path.join(destination_dir, file_name)

        # Copy file to files directory
        shutil.copy2(image_path, destination_path)
        
        return file_name
    
    @staticmethod
    def get_expense_statistics() -> Dict:
        """Get expense statistics."""
        expenses = Expense.query.all()
        
        if not expenses:
            return {
                'total_expenses': 0,
                'total_amount': 0.0,
                'categories': {},
                'monthly_totals': {}
            }
        
        total_amount = sum(expense.total for expense in expenses)
        
        # Group by categories
        categories = {}
        for expense in expenses:
            category = expense.category or 'uncategorized'
            if category not in categories:
                categories[category] = {'count': 0, 'total': 0.0}
            categories[category]['count'] += 1
            categories[category]['total'] += expense.total
        
        # Group by month
        monthly_totals = {}
        for expense in expenses:
            if expense.created_at:
                month_key = expense.created_at.strftime('%Y-%m')
                if month_key not in monthly_totals:
                    monthly_totals[month_key] = 0.0
                monthly_totals[month_key] += expense.total
        
        return {
            'total_expenses': len(expenses),
            'total_amount': total_amount,
            'categories': categories,
            'monthly_totals': monthly_totals
        }


# Create service instance
expense_service = ExpenseService()