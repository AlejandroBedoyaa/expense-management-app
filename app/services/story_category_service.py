"""
Service layer for managing store categories.
"""
from app.models.store_category import StoreCategory
from app.extensions import db
from typing import List, Dict, Optional
import os
from datetime import date
from app.config import Config

from app.utils.helpers import parse_date

class StoreCategoryService:
    """Service for managing store categories."""
    
    @staticmethod
    def create_store_category(data: Dict) -> StoreCategory:
        """Create a new store category record."""
        store_category = StoreCategory.from_dict(data)
        db.session.add(store_category)
        db.session.commit()
        return store_category
    
    @staticmethod
    def get_store_category_by_id(category_id: int) -> Optional[StoreCategory]:
        """Get store category by ID."""
        return StoreCategory.query.get(category_id)
    
    @staticmethod
    def get_all_store_categories() -> List[StoreCategory]:
        """Get all store categories."""
        return StoreCategory.query.order_by(StoreCategory.store_name.asc()).all()
    
    @staticmethod
    def update_store_category(category_id: int, data: Dict) -> Optional[StoreCategory]:
        """Update an existing store category."""
        store_category = StoreCategory.query.get(category_id)
        if not store_category:
            return None
        
        for key, value in data.items():
            if hasattr(store_category, key):
                setattr(store_category, key, value)
        
        db.session.commit()
        return store_category
    
store_category_service = StoreCategoryService()