#!/usr/bin/env python3
"""
Entry point for the Expense Management Flask application.
"""

import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask application using factory pattern
app = create_app()

if __name__ == '__main__':
    # Configuration for development
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')

    print(f"🚀 Starting Expense Management App...")
    print(f"📡 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🌐 Running on: http://{host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )