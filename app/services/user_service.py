import logging
import json
import os
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
        username = update.message.from_user.username

        user = User.query.filter_by(telegram_id=telegram_id).first()
        if user:
            logging.info(f"User found: {telegram_id} - {username}")
            return user

        user = User(
            telegram_id=telegram_id,
            username=username
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

        logging.info(f"New user created: {telegram_id} - {username}")
        return user

    @staticmethod
    def get_user_by_telegram_id(telegram_id: str) -> User:
        """Retrieve a user by their Telegram ID."""
        return User.query.filter_by(telegram_id=telegram_id).first()

user_service = UserService()