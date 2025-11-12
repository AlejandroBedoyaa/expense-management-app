"""
Helper utilities for the expense management application.
"""

import hashlib
import logging
import os
import re
import secrets
import difflib
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional, Union
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageEnhance
from app.config import Config

def generate_secure_filename(original_file_name: str) -> str:
    """Generate a secure file_name with timestamp."""
    file_name = secure_filename(original_file_name)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = secrets.token_hex(4)
    
    name, ext = os.path.splitext(file_name)
    return f"{timestamp}_{name}_{random_suffix}{ext}"

def format_currency(amount: Union[int, float], currency: str = '$') -> str:
    """Format amount as currency."""
    return f"{currency}{amount:,.2f}"

def format_tax(tax_rate: float = 16) -> str:
    """Format tax rate as percentage string."""
    return f"{tax_rate}%"

def clean_image(image_path: str) -> str:
    """Clean and preprocess the ticket image."""
    img = Image.open(image_path)
    img = img.convert('L')  # white and black
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # Intensify contrast
    img.save(image_path)
    return image_path
    

def parse_date(date_input: Union[str, date, datetime]) -> Optional[date]:
    """Parse various date formats to date object."""
    if isinstance(date_input, date):
        return date_input
    
    if isinstance(date_input, datetime):
        return date_input.date()
    
    if isinstance(date_input, str):
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_input, fmt).date()
            except ValueError:
                continue
    
    return None

def delete_file(file_path: str):
    """Helper to delete a temporary file."""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logging.info(f"Deleted temporary file: {file_path}")
    except Exception as e:
        if "No such file" in str(e):
            pass  # File already deleted
        else:
            raise e

def format_log_json(data: Dict[str, Any]) -> str:
    """Format dictionary as JSON string for logging."""
    import json
    return json.dumps(data, indent=2, default=str)


def extract_highest_amount(lines: List[str], patterns: List[str]) -> Optional[float]:
    """Extract the highest monetary amount from lines based on patterns."""
    amounts = []
    for line in lines:
        for pat in patterns:
            match = re.search(r'(?i)\b\d+[.,]\d{2}\b', line)
            if match:
                try:
                    amounts.append(float(match.group().replace(',', '.')))
                except ValueError:
                    continue
    return max(amounts) if amounts else None

def extract_amount_from_lines(lines: List[str], word: str, patterns: List[str]) -> Optional[str]:
    """Extract amount associated with a specific word from lines."""
    for line in lines:
        if re.search(rf'(?i){word}', line):
            for pat in patterns:
                match = re.search(pat, line)
                if match:
                    return match.group(1)
    return None

def fuzzy_store_matching(line, store_dict, threshold=0.8):
    """Find close matches in OCR line."""
    results = difflib.get_close_matches(line.upper(), store_dict.keys(), n=1, cutoff=threshold)
    if results:
        store = results[0]
        return store, store_dict[store]
    return None, None

def match_store(lines, store_keywords):
    """Match store keywords in OCR lines."""
    store_keywords = {k.strip(): v for k, v in store_keywords.items()}
    for line in lines[:5]:
        upper_line = line.upper().strip()
        for keyword in store_keywords:
            if keyword in upper_line:
                return keyword, store_keywords[keyword]
        # Fuzzy matching
        fuzzy_store, group = fuzzy_store_matching(upper_line, store_keywords)
        if fuzzy_store:
            return fuzzy_store, group
    return None, None

def get_upload_path(file: str) -> str:
    """Get full upload path for file."""
    upload_dir = os.path.join(os.getcwd(), Config.FILE_FOLDER)
    os.makedirs(upload_dir, exist_ok=True)
    return os.path.join(file)

# TODO: Not in use yet
def calculate_tax_from_total(total: float, tax_rate: float = 0.16) -> Dict[str, float]:
    """Calculate tax and subtotal from total amount."""
    subtotal = total / (1 + tax_rate)
    tax_amount = total - subtotal
    
    return {
        'subtotal': round(subtotal, 2),
        'tax_amount': round(tax_amount, 2),
        'tax_rate': tax_rate,
        'total': total
    }

# TODO: Not in use yet
def calculate_total_from_subtotal(subtotal: float, tax_rate: float = 0.16) -> Dict[str, float]:
    """Calculate total and tax from subtotal amount."""
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    return {
        'subtotal': subtotal,
        'tax_amount': round(tax_amount, 2),
        'tax_rate': tax_rate,
        'total': round(total, 2)
    }

# TODO: Not in use yet
def escape_markdown(text):
    for c in ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
        text = text.replace(c, f'\\{c}')
    return text

# TODO: Not in use yet
def clean_ocr_text(text: str) -> str:
    """Clean OCR text by removing extra whitespace and invalid characters."""
    import re
    
    # Remove multiple whitespaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.,;:!?\-$€£¥₹]', '', text)
    
    # Strip leading/trailing whitespace
    return text.strip()

# TODO: Not in use yet
def extract_phone_numbers(text: str) -> list:
    """Extract phone numbers from text."""
    import re
    
    # Pattern for various phone number formats
    phone_pattern = r'(\+?\d{1,4}[\s\-\.]?\(?\d{1,4}\)?[\s\-\.]?\d{1,4}[\s\-\.]?\d{1,9})'
    matches = re.findall(phone_pattern, text)
    
    # Filter out numbers that are too short or too long
    valid_phones = [phone for phone in matches if 7 <= len(re.sub(r'\D', '', phone)) <= 15]
    
    return valid_phones

# TODO: Not in use yet
def extract_emails(text: str) -> list:
    """Extract email addresses from text."""
    import re
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

# TODO: Not in use yet
def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive data in dictionary for logging."""
    sensitive_keys = ['password', 'token', 'secret', 'key', 'api_key']
    masked_data = data.copy()
    
    for key, value in masked_data.items():
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            if isinstance(value, str) and len(value) > 4:
                masked_data[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
            else:
                masked_data[key] = '***'
    
    return masked_data

# TODO: Not in use yet
def create_response(success: bool = True, data: Any = None, message: str = None, 
                    error: str = None, status_code: int = 200) -> tuple:
    """Create standardized API response."""
    response = {
        'success': success,
        'timestamp': utc_now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if error:
        response['error'] = error
    
    return response, status_code

def utc_now() -> datetime:
    """
    Get current UTC datetime with timezone awareness.
    
    Returns:
        Timezone-aware datetime object in UTC
    """
    return datetime.now(timezone.utc)

def utc_timestamp() -> str:
    """
    Get current UTC timestamp as ISO string.
    
    Returns:
        ISO format timestamp string
    """
    return utc_now().isoformat()

def hash_password(password: str) -> str:
    """
    Hash a password using Werkzeug's secure password hashing.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    return generate_password_hash(
        password, 
        method='pbkdf2:sha256',
        salt_length=16
    )

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        password_hash: Stored password hash
        
    Returns:
        True if password matches hash, False otherwise
    """
    if not password or not password_hash:
        return False
    
    return check_password_hash(password_hash, password)

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Length of token in bytes (default: 32)
        
    Returns:
        URL-safe base64 encoded token
    """
    return secrets.token_urlsafe(length)

def generate_vinculation_token() -> str:
    """
    Generate a secure token for account vinculation/linking.
    
    Returns:
        6-character alphanumeric token (uppercase)
    """
    # Generate a 6-character token using secrets for cryptographic security
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(secrets.choice(alphabet) for _ in range(6))

def hash_telegram_id(telegram_id: str) -> str:
    """
    Create a hash of Telegram ID for privacy/security.
    
    Args:
        telegram_id: Telegram user ID as string
        
    Returns:
        SHA256 hash of the Telegram ID
    """
    return hashlib.sha256(telegram_id.encode()).hexdigest()

def to_datetime(value):
    """Convert string or datetime to timezone-aware UTC datetime."""
    if isinstance(value, datetime):
        # Si ya es datetime pero es naive, asumimos que es UTC
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, str):
        try:
            # Si el string viene en formato iso (ej: '2023-11-11T20:13:57.856980')
            dt = datetime.fromisoformat(value)
            # Si es naive, asumimos que es UTC
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            # Si falla, puedes usar otra estrategia de parseo aquí, por ejemplo:
            try:
                # formato típico de SQL: '2023-11-11 20:13:57'
                dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                # Asumimos que es UTC
                return dt.replace(tzinfo=timezone.utc)
            except Exception:
                pass
        # Si no se puede convertir, regresa None o lanza error:
        return None
    # Si es None u otro tipo
    return None
