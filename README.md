TODO: Falta actualizar el README

# 💰 Expense Management Bot

Telegram bot para gestión automática de gastos usando OCR en recibos con API REST Flask.

## 📝 Descripción

Envía fotos de recibos al bot de Telegram → Extracción automática por OCR → Edita datos → Guarda en base de datos. Incluye API REST completa para gestión y análisis de gastos.

**Características principales:**
- 📸 Procesamiento OCR de recibos (PaddleOCR)
- 🤖 Bot de Telegram interactivo
- 🔧 API REST completa (operaciones CRUD)
- 💾 Base de datos MySQL con SQLAlchemy
- 📊 Análisis y estadísticas de gastos

## 🛠 Stack Tecnológico

- **Flask** - Framework web con patrón factory
- **SQLAlchemy** - ORM para base de datos
- **PaddleOCR** - Extracción de texto (Español)
- **python-telegram-bot** - Framework de bot asíncrono
- **Pillow/** - Procesamiento de imágenes

## ⚡ Instalación Rápida

### Prerrequisitos
- Python 3.8+
- Token de bot de Telegram ([@BotFather](https://t.me/BotFather))

### Configuración

1. **Clonar y configurar entorno:**
```bash
git clone <repo-url>
cd expense-management-app
python -m venv venv
# For Windows (Powershell or CMD) use
.\venv\Scripts\activate
# For Bash or Linux/Mac use:
source venv/Scripts/activate
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
Crear archivo `.env`:
```env
FLASK_ENV=development
PORT=5000
HOST=127.0.0.1
TELEGRAM_BOT_TOKEN=tu_token_de_telegram_aqui
DATABASE_URL=mysql+pymysql://user:password@localhost:PORT/mydb
LOG_BOT_FILE=logs/bot.log
LOG_BOT_EXTERNAL_LIBS_FILE=logs/external_libs.log
FILE_FOLDER=files/tickets
MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
```

3. **Inicializar base de datos:**
```bash
flask --app expenses_db init-db 
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🚀 Ejecución

**Terminal 1 - API Flask:**
```bash
python run.py
```

**Terminal 2 - Bot Telegram:**
```bash
python bot.py
```

## 🤖 Comandos del Bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Inicializar bot |
| `/help` | Mostrar ayuda |
| `/edit <campo> <valor>` | Editar datos extraídos |
| `/save` | Guardar gasto en BD |
| Enviar foto | Procesar recibo automáticamente |

## 🔗 API Endpoints

- `GET /api/expenses` - Listar gastos
- `POST /api/expenses` - Crear gasto
- `POST /api/expenses/upload-ticket` - Subir recibo
- `GET /api/expenses/statistics` - Obtener estadísticas

## 📁 Estructura del Proyecto

```
expense-management-app/
├── app/
│   ├── __init__.py          # Factory Flask
│   ├── config.py            # Configuración
│   ├── models/              # Modelos SQLAlchemy
│   ├── services/            # Lógica de negocio
│   ├── api/                 # Endpoints REST
│   └── utils/               # Utilidades
├── bot.py                   # Bot de Telegram
├── run.py                   # Servidor Flask
└── init_db.py              # Inicializar BD
```

## 🔧 Configuración

### Variables de Entorno Requeridas

- `TELEGRAM_BOT_TOKEN` - Token del bot (obligatorio)
- `SECRET_KEY` - Clave secreta de Flask
- `DATABASE_URL` - URL de base de datos
- `FLASK_ENV` - Entorno (development/production)

### Configuración Opcional

- `FILE_FOLDER` - Directorio para recibos (default: files/tickets)
- `MAX_CONTENT_LENGTH` - Tamaño máx. archivo (default: 16MB)

## 📊 Flujo de Trabajo

1. **Enviar foto** de recibo al bot
2. **OCR automático** extrae: concepto, total, fecha
3. **Revisar datos** extraídos
4. **Editar si necesario:** `/edit total 25.50`
5. **Confirmar:** `/save` para guardar en BD

## 🚨 Solución de Problemas

**Bot no responde:**
```bash
# Verificar token
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TELEGRAM_BOT_TOKEN'))"
```

**Error de BD:**
```bash
flask db init
```

## 📄 Licencia

MIT License

---

**¡Gestiona tus gastos fácilmente! 📱💳**
