#!/usr/bin/env python3
"""
Seed script for store categories in the Expense Management App.
Populates the database with predefined store categories.

Command to run:
    python -m seed.seed_store_categories
"""

import logging
import os
from dotenv import load_dotenv
from app.models import StoreCategory
from app import create_app
from app.extensions import db
from sqlalchemy.exc import IntegrityError

load_dotenv()
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

SEED_CATEGORIES = [
    {'store_name': 'RECEIPT', 'category': 'uncategorized'}, # Default category
    # Your custom store categories
    {'store_name': 'OXXO', 'category': 'conveniencia'},
    {'store_name': 'CHEDRAUI', 'category': 'supermercado'},
    {'store_name': 'SORIAN', 'category': 'supermercado'},
    {'store_name': 'SORIANA', 'category': 'supermercado'},
    {'store_name': 'WALMART', 'category': 'supermercado'},
    {'store_name': 'SEVEN ELEVEN', 'category': 'conveniencia'},
    {'store_name': 'FARMACIAS DEL AHORRO', 'category': 'farmacia'},
    {'store_name': 'FARMACIA GUADALAJARA', 'category': 'farmacia'},
    {'store_name': 'STARBUCKS', 'category': 'restaurante'},
    {'store_name': 'VIPS', 'category': 'restaurante'},
    {'store_name': 'SANBORNS', 'category': 'restaurante'},
    {'store_name': 'BURGER KING', 'category': 'restaurante'},
    {'store_name': 'AMAZON', 'category': 'compras en línea'},
    {'store_name': 'MERCADO LIBRE', 'category': 'compras en línea'},
    {'store_name': 'AT&T', 'category': 'internet'},
    {'store_name': 'CFE', 'category': 'servicios'},
    {'store_name': 'COMISION FEDERAL DE ELECTRICIDAD', 'category': 'servicios'},
    {'store_name': 'TOTALPLAY', 'category': 'internet'},
]

def seed_store_categories():
    app = create_app(FLASK_ENV)
    with app.app_context():
        for record in SEED_CATEGORIES:
            exists = StoreCategory.query.filter_by(store_name=record["store_name"]).first()
            if not exists:
                obj = StoreCategory(**record)
                db.session.add(obj)
        try:
            db.session.commit()
            logging.info("Store categories seeded.")
        except IntegrityError:
            db.session.rollback()
            logging.warning("Some categories already exist. Skipped duplicates.")
        finally:
            db.session.close()

if __name__ == '__main__':
    seed_store_categories()
