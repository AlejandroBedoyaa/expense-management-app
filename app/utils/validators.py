"""
Validation utilities for the expense management application.
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional

# TODO: Not in use yet
def validate_expense_data(data: Dict) -> Dict:
    """
    Validate expense data and return validation results.
    
    Args:
        data: Dictionary with expense data
        
    Returns:
        Dictionary with 'valid' boolean and 'errors' list
    """
    errors = []
    
    # Required fields
    required_fields = ['payment_concept', 'total']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Field '{field}' is required")
    
    # Validate payment_concept
    if 'payment_concept' in data and data['payment_concept']:
        if not isinstance(data['payment_concept'], str):
            errors.append("payment_concept must be a string")
        elif len(data['payment_concept'].strip()) < 2:
            errors.append("payment_concept must be at least 2 characters long")
        elif len(data['payment_concept']) > 100:
            errors.append("payment_concept cannot exceed 100 characters")
    
    # Validate amounts
    numeric_fields = ['total', 'subtotal', 'tax']
    for field in numeric_fields:
        if field in data and data[field] is not None:
            if not isinstance(data[field], (int, float)):
                errors.append(f"Field '{field}' must be a number")
            elif data[field] < 0:
                errors.append(f"Field '{field}' cannot be negative")
    
    # Validate category
    if 'category' in data and data['category']:
        if not isinstance(data['category'], str):
            errors.append("Category must be a string")
        elif len(data['category']) > 50:
            errors.append("Category cannot exceed 50 characters")
    
    # Validate note
    if 'note' in data and data['note']:
        if not isinstance(data['note'], str):
            errors.append("note must be a string")
        elif len(data['note']) > 500:
            errors.append("note cannot exceed 500 characters")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

# TODO: Not in use yet
def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# TODO: Not in use yet
def validate_date_string(date_str: str) -> bool:
    """Validate date string in common formats."""
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-m-%Y']
    
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    
    return False

def validate_image_file(filename: str, max_size_mb: int = 10) -> Dict:
    """
    Validate image file.
    
    Args:
        filename: Name of the file
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        Dictionary with validation results
    """
    errors = []
    
    if not filename:
        errors.append("Filename is required")
        return {'valid': False, 'errors': errors}
    
    # Check extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    if file_ext not in allowed_extensions:
        errors.append(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }