import logging
import json
import os
from typing import Dict
from app.models import User
from app.models.store_category import StoreCategory
from app.extensions import db

JSON_PATH = os.path.join('app', 'json/default_categories.json')

def load_default_categories():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        categories = json.load(f)
    return categories

class UserService:

    @staticmethod
    def get_or_create_user(update):
        """
        Get an object Telegram 'update' (you can adjust according to your on_message framework).
        Returns the User model (record in the database).
        """
        telegram_id = str(update.message.from_user.id)
        first_name = update.message.from_user.first_name or "there"

        user = User.query.filter_by(telegram_id=telegram_id).first()
        if user:
            logging.info(f"User found: {telegram_id} - {first_name=}")
            return user

        user = User(
            telegram_id=telegram_id,
        )
        db.session.add(user)
        db.session.flush()

        # Add default store categories for the new user
        DEFAULT_CATEGORIES = load_default_categories()
        for data in DEFAULT_CATEGORIES:
            obj = StoreCategory.from_dict(data)
            obj.user_id = user.id
            db.session.add(obj)

        db.session.commit()

        logging.info(f"New user created: {telegram_id} - {first_name}")
        return user
    
    @staticmethod
    def update_user(user_id: str, data: Dict) -> User:
        """Update an existing user."""
        user = User.query.get(user_id)
        if not user:
            return None
        
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_telegram_id(telegram_id: str) -> User:
        """Retrieve a user by their Telegram ID."""
        return User.query.filter_by(telegram_id=telegram_id).first()
    
    @staticmethod
    def get_user_by_token(token: str) -> User:
        """Retrieve a user by their token."""
        return User.query.filter_by(vinculation_token=token).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> User:
        """Retrieve a user by their email."""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def update_accumulated_balance(user_id: str, amount: float):
        """Update the accumulated balance for a user."""
        user = User.query.get(user_id)
        if user:
            user.accumulated_balance += amount
            db.session.commit()
        return user

user_service = UserService()