#!/usr/bin/env python3
"""
Database initialization script for the Expense Management App.
Creates database tables and initial configuration.
"""

import os
from app import create_app
from app.extensions import db

def init_database():
    """Initialize the database with tables."""
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        
        # Create all tables
        db.create_all()

        print("✅ Database initialized successfully!")
        print(f"📁 Database file: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    init_database()