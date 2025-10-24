"""
OCR service for extracting text and data from receipt images using PaddleOCR.
"""
import logging
import os
import re
from typing import List, Dict, Optional
from app.config import Config
from app.utils.helpers import extract_highest_amount, extract_amount_from_lines, match_store
from app.services.story_category_service import StoreCategoryService
from paddleocr import PaddleOCR

class OCRService:
    """Service for extracting text and data from receipt images using PaddleOCR."""
    
    def __init__(self, languages: List[str] = Config.OCR_LANGUAGES):
        """Initialize OCR service with specified languages."""
        ocr = PaddleOCR(use_angle_cls=True, lang='es')
        self.reader = ocr
        # self.languages = languages
    
    def extract_text(self, image_path: str) -> str:
        """Extract raw text from image."""
        try:
            # Read image
            response = self.reader.ocr(image_path)

            # Extract only plain text from OCR response
            # texts = [line[1][0] for line in response[0]]
            texts = response[0]['rec_texts']
            logging.info(f"OCR response: {texts}")
            return "\n".join(texts)
        except Exception as e:
            raise Exception(f"{str(e)}")
    
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
            # receipt_data['raw_text'] = raw_text
            # logging.info(f"Extracted receipt data: {receipt_data}")
            return receipt_data
            
        except Exception as e:
            raise Exception(f"{str(e)}")

    def _parse_receipt_text(self, text: str) -> Dict:
        """Parse raw OCR text to extract structured receipt information."""
        data = {
            'payment_concept': None,
            'category': None,
            'total': None,
            'subtotal': None,
            'payment_date': None,
            # 'items': [],
            # 'tax': None
        }
        
        lines = text.split('\n')
        
        # Extract total amount (looking for patterns like $123.45, 123.45, TOTAL: 123.45)
        total_patterns = [
            r'(?i)TOTAL\s*M\.?N\.?\s*\$?\s*[^\d]*?(\d+[.,]\d{2})',                # "TOTAL M.N. $" varias formas
            r'(?i)\$\s*(\d+[.,]\d{2})',                                           # "$ 101.00"
            r'(?i)(\d+[.,]\d{2})\s*(?:$|pesos|MXN|m\.n\.|mn)',                    # "101.00 pesos", "101.00 MXN", etc
            r'(?i)TOTAL\s*:\s*\$\s*(\d+[.,]\d{2})',                               # "TOTAL: $ 101.00"
            r'(?i)TOTAL\s*\$\s*(\d+[.,]\d{2})',                                   # "TOTAL $ 101.00"
        ]

        highest_total = extract_highest_amount(lines, total_patterns)
        if highest_total is not None:
            data['total'] = highest_total

        total = extract_amount_from_lines(lines, 'total', total_patterns)
        if total is not None:
            try:
                data['total'] = float(total.replace(',', '.'))
            except ValueError:
                pass

        subtotal_patterns = [
            r'(?i)SUBTOTAL\s*M\.?N\.?\s*\$?\s*[^\d]*?(\d+[.,]\d{2})',                # "TOTAL M.N. $" varias formas
            r'(?i)\$\s*(\d+[.,]\d{2})',                                              # "$ 101.00"
            r'(?i)(\d+[.,]\d{2})\s*(?:$|pesos|MXN|m\.n\.|mn)',                       # "101.00 pesos", "101.00 MXN", etc
            r'(?i)SUBTOTAL\s*:\s*\$\s*(\d+[.,]\d{2})',                               # "TOTAL: $ 101.00"
            r'(?i)SUBTOTAL\s*\$\s*(\d+[.,]\d{2})',                                   # "TOTAL $ 101.00"
        ]
        
        subtotal = extract_amount_from_lines(lines, 'subtotal', subtotal_patterns)
        if subtotal is not None:
            try:
                data['subtotal'] = float(subtotal.replace(',', '.'))
            except ValueError:
                pass
        
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

        store_categories = StoreCategoryService.get_all_store_categories()
        store_categories_dict = {category.store_name: category.category for category in store_categories}
        store_keyword, category = match_store(lines, store_categories_dict)
        
        if store_keyword and category:
            data['payment_concept'] = store_keyword
            data['category'] = category
        else:
            # Extract payment_concept (usually the first few lines)
            if lines:
                # Take first non-empty line as potential payment_concept
                for line in lines[:5]:
                    line = line.strip()
                    if line and len(line) > 2:
                        data['payment_concept'] = line
                        break
        
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