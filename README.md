# 💰 Expense Management Bot

Personal telegram bot to manage expenses, using OCR and API REST with Flask framework.

At the moment I need to find a hosting to show the example so, you later can test this project with this links

Telegram bot: https://t.me/DarthBalanceBot
Dashboard link: In progress.

This project it's to create a personal bot, you can download it and HOSTING BY YOURSELF.

## 📝 Description

- Send ticket photo to bot → automated extract data with OCR → Edit data → save in DB.
- Adicional commands to do manual actions.
- Include API REST to manage and analysis expenses.

**Características principales:**
- 📸 Tickets processing with OCR (PaddleOCR)
- 🤖 Interactive Telegram Bot
- 🔧 API REST to connect a dashboard
- 💾 Database MySQL with SQLAlchemy

## 🛠 Stack Tech

- **Flask** - Framework web
- **SQLAlchemy** - Database ORM
- **PaddleOCR** - Text extracting (only for Spanish language at the moment)
- **python-telegram-bot** - Async framework bot

## ⚡ Quick install

### Prerequisites
- Python 3.8+
- Telegram bot token ([@BotFather](https://t.me/BotFather))

### Config

1. **Clone and config enviroment:**
```bash
git clone https://github.com/AlejandroBedoyaa/expense-management-app
cd expense-management-app
python -m venv venv
# For Windows (Powershell or CMD) use
.\venv\Scripts\activate
# For Bash or Linux/Mac use:
source venv/Scripts/activate or source venv/bin/activate
pip install -r requirements.txt
```

2. **Config enviroment vars:**
Create file `.env` and add:
```env
FLASK_ENV=development
PORT=5000
HOST=127.0.0.1
JWT_SECRET_KEY=your_jwt_token
LOG_BOT_FILE=logs/bot.log
LOG_BOT_EXTERNAL_LIBS_FILE=logs/external_libs.log
FILE_FOLDER=files/tickets
MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
DATABASE_URL=mysql+pymysql://user:password@localhost:PORT/mydb
TELEGRAM_BOT_URL=url_tlegram_bot
TELEGRAM_BOT_NAME=BotName
TELEGRAM_BOT_TOKEN=your_token
DASHBOARD_URL=url_to_Front
TOKEN_EXPIRATION_MINUTES=minutes_to_expirate_token_signup
```

Or use copy and rename the `.env.example`.

3. **Init DB:**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🚀 Execute

**Terminal 1 - API Flask:**
```bash
python run.py
```

**Terminal 2 - Bot Telegram:**
```bash
python bot.py
```

## 🤖 Bot's commands

| Command | Description |
|---------|-------------|
| `/start` | Init bot |
| `/help` | Show help |
| `/edit <campo> <valor>` | Edit extracted data |
| `/save` | Save extracted data |
| Send photo | Process image |

## 🔗 API Endpoints

- TODO

## 📁 Structure

```
expense-management-app/
├── app/
│   ├── __init__.py          # Factory Flask
│   ├── config.py            # Config
│   ├── extensions.py        # DB extension
│   ├── api/                 # Endpoints REST
│   ├── json/                # Json files
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Services
│   └── utils/               # Utils
├── bot.py                   # Telegram bot
├── run.py                   # API Server
└── README.md                # This file
└── .env.example             # Enviroment example
└── requirements.txt         # Libs to install
└── .gitignore               
```

## TODO
1. Switch Paddle OCR to ChatGPT, more efficiente and less infraestructure server
2. Make a version with n8n

**¡Easy manage your expenses! 📱💳**
