# 🤖 Expense Management Telegram Bot

An intelligent expense tracking system that uses **OCR technology** to automatically process receipt images via Telegram bot and provides a complete **REST API** for expense management.

## 📋 Overview

This project combines a **Telegram bot interface** with a **Flask REST API** to create a comprehensive expense management solution. Users can photograph receipts, send them to the bot, and the system automatically extracts expense data using advanced OCR processing. The application features a professional Flask architecture with services, models, and API endpoints.

## ✨ Key Features

### 🤖 **Telegram Bot**
- � **Smart Receipt Processing**: Upload photos → Automatic OCR extraction
- ✏️ **Interactive Editing**: Edit extracted data before saving (`/edit` command)
- 💾 **Save Expenses**: Confirm and save to database (`/save` command)
- 📊 **Quick Commands**: `/start`, `/help`, `/edit`, `/save`

### 🔧 **REST API**
- 📋 **CRUD Operations**: Complete expense management via API
- � **Receipt Upload**: `POST /api/expenses/upload-receipt`
- � **Statistics**: `GET /api/expenses/statistics`
- 🔍 **Filtering**: Filter by category, date ranges
- 📊 **JSON Responses**: Structured data for integrations

### 🧠 **OCR Intelligence**
- 🏪 **Merchant Detection**: Automatic store/restaurant name extraction
- � **Amount Recognition**: Total, subtotal, and tax extraction
- 📅 **Date Parsing**: Multiple date format support
- 🏷️ **Smart Categorization**: Automatic expense categorization

## 🛠 Technology Stack

- **Backend**: Flask (Factory Pattern)
- **Database**: SQLAlchemy with migrations support
- **OCR Engine**: EasyOCR (Spanish & English)
- **Bot Framework**: python-telegram-bot (async)
- **Image Processing**: Pillow
- **Architecture**: Services, Models, Blueprints, Utilities

## 📦 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Virtual environment recommended

### Installation

1. **Clone and setup**

   ```bash
   git clone <repository-url>
   cd expense-management-app
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**

   Create `.env` file:

   ```env
   FLASK_ENV=development
   SECRET_KEY=your-super-secret-key-here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   DATABASE_URL=sqlite:///expenses.db
   ```

4. **Initialize database**

   ```bash
   python init_db.py
   ```

### Running the Application

1. **Start Flask API** (Terminal 1)

   ```bash
   python run.py
   ```

2. **Start Telegram Bot** (Terminal 2)

   ```bash
   python bot.py
   ```

## 🤖 Bot Usage

### Available Commands

- **`/start`** - Welcome message and setup
- **`/help`** - Show all available commands  
- **`/edit <field> <value>`** - Edit extracted data
- **`/save`** - Save expense to database

### Workflow

1. 📸 **Send receipt photo** to bot
2. 🔍 **Review extracted data** (merchant, total, date)  
3. ✏️ **Edit if needed**: `/edit total 25.50`
4. 💾 **Save**: `/save` to confirm and store

## � REST API Endpoints

### Expense Management

- **`GET /api/expenses`** - List all expenses (with filtering)
- **`GET /api/expenses/{id}`** - Get specific expense
- **`POST /api/expenses`** - Create new expense
- **`PUT /api/expenses/{id}`** - Update expense
- **`DELETE /api/expenses/{id}`** - Delete expense

### Receipt Processing

- **`POST /api/expenses/upload-receipt`** - Upload & process receipt image
- **`GET /api/expenses/statistics`** - Get expense analytics

### Example API Usage

```bash
# Upload receipt for processing
curl -X POST -F "file=@receipt.jpg" http://localhost:5000/api/expenses/upload-receipt

# Get expense statistics  
curl http://localhost:5000/api/expenses/statistics
```

## 🏗️ Project Architecture

```
expense-management-app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Multi-environment config
│   ├── extensions.py        # SQLAlchemy, Flask-Migrate
│   ├── api/                 # REST API blueprints
│   │   └── expenses.py      # Expense endpoints
│   ├── models/              # SQLAlchemy models
│   │   └── expense.py       # Expense model
│   ├── services/            # Business logic
│   │   ├── ocr_service.py   # OCR processing
│   │   └── expense_service.py # Expense operations
│   └── utils/               # Helpers & validators
├── uploads/receipts/        # Receipt image storage
├── bot.py                   # Telegram bot (refactored)
├── run.py                   # Flask app entry point
└── init_db.py              # Database initialization
```

## 📊 Database Schema

**Expense Model:**
- `payment_concept` - Merchant/store name
- `note` - Additional description  
- `category` - Expense category
- `subtotal` - Amount before tax
- `tax` - Tax amount/rate
- `total` - Final amount
- `file_path` - Receipt image path
- `payment_date` - Transaction date
- `created_date` - Record creation date

## 📈 Future Enhancements

- [ ] Receipt data validation and editing
- [ ] Expense analytics and reporting
- [ ] Multi-currency support
- [ ] Integration with accounting software
- [ ] Monthly/yearly expense summaries
- [ ] Budget tracking and alerts
- [ ] Export functionality (CSV, PDF)
- [ ] Multiple receipt formats support
- [ ] AI-powered expense categorization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Provide sample images (with sensitive information removed)

## 🙏 Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for excellent OCR capabilities
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the robust Telegram bot framework
- [Flask](https://flask.palletsprojects.com/) for the lightweight web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for database management

---

**Note**: Remember to keep your bot token secure and never commit it to version control. Always use environment variables for sensitive configuration.