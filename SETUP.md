# 🚀 Setup Instructions - Expense Management Bot

Complete setup guide for the Flask + Telegram Bot expense management system.

## 📋 Prerequisites

- **Python 3.8+** installed
- **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
- **Git** (optional, for cloning)

## 🔧 Step-by-Step Installation

### 1. Environment Setup

```bash
# Clone repository (if from Git)
git clone <your-repo-url>
cd expense-management-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate          # Windows PowerShell
# source venv/bin/activate     # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file in project root:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-random-key-here
DATABASE_URL=sqlite:///expenses.db

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather

# Optional
DEBUG=True
HOST=127.0.0.1
PORT=5000
```

### 4. Database Initialization

```bash
python init_db.py
```

### 5. Run the Applications

**Terminal 1 - Flask API Server:**

```bash
python run.py
```

**Terminal 2 - Telegram Bot:**

```bash
python bot.py
```

## ✅ Verification

After running both applications, verify everything works:

1. **Flask API** - Visit: http://localhost:5000/api/expenses
2. **Telegram Bot** - Send `/start` to your bot
3. **Test Upload** - Send a receipt photo to bot

## 🤖 Bot Commands Reference

| Command | Description | Usage |
|---------|-------------|-------|
| `/start` | Initialize bot and show welcome | `/start` |
| `/help` | Display available commands | `/help` |
| `/edit` | Edit extracted receipt data | `/edit total 25.50` |
| `/save` | Save expense to database | `/save` |
| Photo | Process receipt automatically | Send image |

## 🔗 API Endpoints Reference

### Expenses

- **`GET /api/expenses`** - List all expenses
  - Query params: `?category=food&limit=10`
- **`GET /api/expenses/{id}`** - Get specific expense
- **`POST /api/expenses`** - Create expense manually
- **`PUT /api/expenses/{id}`** - Update existing expense
- **`DELETE /api/expenses/{id}`** - Delete expense

### Receipt Processing

- **`POST /api/expenses/upload-receipt`** - Upload receipt image
- **`GET /api/expenses/statistics`** - Get expense analytics

### Example API Call

```bash
# Test receipt upload via API
curl -X POST \
  -F "file=@path/to/receipt.jpg" \
  http://localhost:5000/api/expenses/upload-receipt
```

## 🏗️ Project Architecture

The application follows **Flask best practices** with:

- **Factory Pattern** (`app/__init__.py`)
- **Blueprints** for API organization (`app/api/`)
- **Services Layer** for business logic (`app/services/`)
- **Models** with SQLAlchemy (`app/models/`)
- **Utilities** for reusable code (`app/utils/`)
- **Multi-environment** configuration (`app/config.py`)

## 🎯 Key Features Implemented

### ✨ **Architecture Improvements**

- **Factory Pattern** - Configurable Flask app creation
- **Blueprint Organization** - Modular API structure
- **Service Layer** - Separated business logic
- **Model Enhancement** - Rich SQLAlchemy models with serialization
- **Utility Functions** - Reusable validators and helpers

### 🤖 **Bot Enhancements**

- **Interactive Workflow** - Extract → Edit → Save process
- **Smart OCR** - Merchant detection, amount parsing, date extraction
- **Error Handling** - Graceful failure management
- **Temporary Storage** - Edit before saving capability

### 🔧 **Technical Features**

- **Multi-Environment Config** - Development/Production settings
- **Database Migrations** - Schema version control ready
- **API Documentation** - RESTful endpoints
- **Image Processing** - OCR with EasyOCR
- **Async Bot Handling** - Non-blocking Telegram operations

## 🚨 Troubleshooting

### Common Issues

**Bot not responding:**

```bash
# Check token configuration
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Token:', os.getenv('TELEGRAM_BOT_TOKEN'))"
```

**Database errors:**

```bash
# Reinitialize database
python init_db.py
```

**Import errors:**

```bash
# Verify virtual environment
pip list | grep Flask
```

### Logs

Both applications log to console. Check for:
- Token validation errors
- Database connection issues  
- OCR processing failures
- File upload problems

## 🔮 Next Steps

- [ ] Add user authentication
- [ ] Implement expense categories
- [ ] Add expense analytics dashboard
- [ ] Create web interface
- [ ] Add export functionality (PDF, CSV)
- [ ] Implement budget tracking
- [ ] Add recurring expense support

## 📞 Support

If you encounter issues:

1. Check the console logs for errors
2. Verify `.env` configuration
3. Ensure virtual environment is activated
4. Test with sample receipt images

---

**Happy expense tracking! 📊💰**