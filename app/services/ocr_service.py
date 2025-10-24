import easyocr
import re
from typing import List, Dict, Optional
import os
from app.config import Config

class OCRService:
    """Service for extracting text and data from receipt images using EasyOCR."""
    
    def __init__(self, languages: List[str] = Config.OCR_LANGUAGES):
        """Initialize OCR service with specified languages."""
        self.reader = easyocr.Reader(languages)
        self.languages = languages
    
    def extract_text(self, image_path: str) -> str:
        """Extract raw text from image."""
        try:
            response = self.reader.readtext(image_path, detail=0, paragraph=True)
            return "\n".join(response)
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    def extract_receipt_data(self, image_path: str) -> Dict:
        """
        Extract structured data from receipt image.
        Returns dictionary with extracted information.
        """
        try:
            # Extract raw text
            raw_text = self.extract_text(image_path)
            
            # Parse the text to extract structured data
            receipt_data = self._parse_receipt_text(raw_text)
            receipt_data['raw_text'] = raw_text
            
            return receipt_data
            
        except Exception as e:
            raise Exception(f"Error processing receipt: {str(e)}")
    
    def _parse_receipt_text(self, text: str) -> Dict:
        """Parse raw OCR text to extract structured receipt information."""
        data = {
            'payment_concept': None,
            'total': None,
            'payment_date': None,
            # 'items': [],
            'tax': None
        }
        
        lines = text.split('\n')
        
        # Extract total amount (looking for patterns like $123.45, 123.45, TOTAL: 123.45)
        total_patterns = [
            r'(?:TOTAL M. N.|total|TOTAL|Total).*?(\d+[.,]\d{2})',
            r'\$\s*(\d+[.,]\d{2})',
            # r'(\d+[.,]\d{2})\s*(?:$|pesos|MXN)',
        ]
        
        for line in lines:
            for pattern in total_patterns:
                match = re.search(pattern, line)
                if match:
                    total_str = match.group(1).replace(',', '.')
                    try:
                        data['total'] = float(total_str)
                        break
                    except ValueError:
                        continue

        subtotal_patterns = [
            r'(?:subtotal|SUBTOTAL|Subtotal).*?(\d+[.,]\d{2})',
            r'\$\s*(\d+[.,]\d{2})',
            r'(\d+[.,]\d{2})\s*(?:$|pesos|MXN)',
        ]
        
        for line in lines:
            for pattern in subtotal_patterns:
                match = re.search(pattern, line)
                if match:
                    subtotal_str = match.group(1).replace(',', '.')
                    try:
                        data['subtotal'] = float(subtotal_str)
                        break
                    except ValueError:
                        continue
        
        # Extract date patterns (DD/MM/YYYY, DD-MM-YYYY, etc.)
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4})',
        ]
        
        for line in lines:
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    data['payment_date'] = match.group(1)
                    break

        # Extract payment_concept (usually the first few lines)
        if lines:
            # Take first non-empty line as potential payment_concept
            # for line in lines[:3]:
            #     line = line.strip()
            #     if line and len(line) > 2:
            #         data['payment_concept'] = line
            #         break
            for line in lines:
                # Busca línea sin números y con más de 8 caracteres, preferentemente mayúsculas
                if line.isupper() and not any(char.isdigit() for char in line) and len(line.strip()) > 8:
                    data['payment_concept'] = line.strip()
                    break
            # Si no encuentra, regresa la primera línea significativa
            for line in lines:
                if len(line.strip()) > 5 and not any(char.isdigit() for char in line):
                    data['payment_concept'] = line.strip()
                    break
        
        # Extract tax/IVA information
        tax_patterns = [
            r'(?:IVA|Iva|iva|Tax|tax).*?(\d+[.,]\d{2})',
            r'(\d+[.,]\d{2}).*?(?:IVA|Tax)',
        ]
        
        for line in lines:
            for pattern in tax_patterns:
                match = re.search(pattern, line)
                if match:
                    tax_str = match.group(1).replace(',', '.')
                    try:
                        data['tax'] = float(tax_str)
                        break
                    except ValueError:
                        continue
        
        return data
    
    def validate_image(self, image_path: str) -> bool:
        """Validate if the image file exists and is readable."""
        if not os.path.exists(image_path):
            return False
        
        # Check if file is an image
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        file_ext = os.path.splitext(image_path)[1].lower()
        
        return file_ext in valid_extensions


# Create default OCR service instance
ocr_service = OCRService()