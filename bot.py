#!/usr/bin/env python3
"""
Telegram Bot for Expense Management
Handles receipt image processing and expense creation via Telegram.

Command to run:
    python bot.py
"""

from multiprocessing import context
from app.utils.logging_config import setup_logging
setup_logging()
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import sys
import tempfile
import asyncio
from datetime import date
from dotenv import load_dotenv

# Import from our refactored structure
from app import create_app
from app.services.expense_service import expense_service
from app.services.user_service import user_service
from app.services.income_service import income_service
from app.utils.helpers import delete_file, clean_image
from app.utils.validators import validate_image_file
from app.utils.messages_templates import (income_command, income_help_message, welcome_message, help_message, data_message, edit_message, handle_message)

# Load environment variables
load_dotenv()
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

# Create Flask app context for database operations
flask_app = create_app(FLASK_ENV)

# Get Telegram bot token from config
TOKEN = flask_app.config.get('TELEGRAM_BOT_TOKEN')

# Temporary storage for user expense data during editing
TEMP_EXPENSE = {}

class ExpenseBot:
    """Telegram bot for expense management."""
    
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup bot command and message handlers."""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("edit", self.edit_command))
        self.app.add_handler(CommandHandler("save", self.save_command))
        self.app.add_handler(CommandHandler("list", self.list_command))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(CommandHandler("income", self.income_command))
        self.app.add_handler(CommandHandler("incomes", self.incomes_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def reply_text(self, update: Update, text: str, parse_mode: str = 'HTML'):
        """Helper to send a reply message."""
        return await update.message.reply_text(text, parse_mode=parse_mode)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        telegram_user_name = update.effective_user.first_name or "there"
        message = welcome_message(telegram_user_name)
        message += help_message()
        await self.reply_text(update, message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        message = help_message()
        await self.reply_text(update, message)
    
    async def edit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user_id = update.effective_user.id
        args = context.args
        if telegram_user_id not in TEMP_EXPENSE:
            await self.reply_text(update, "Nothing to edit, first send a receipt photo.")
            return
        if len(args) < 2:
            await self.reply_text(update, "Invalid format. Use: /edit &lt;field&gt; &lt;value&gt;")
            return
        campo = args[0].lower()
        valor = " ".join(args[1:])
        if campo not in TEMP_EXPENSE[telegram_user_id]:
            await self.reply_text(update, f"Field '{campo}' does not exist or cannot be edited.")
            return
        # Try to convert the value if it's total/subtotal/tax
        try:
            if campo in ['total', 'subtotal', 'tax']:
                valor = float(valor)
        except Exception:
            pass

        # Update the temporary field
        TEMP_EXPENSE[telegram_user_id][campo] = valor
        expense_data = TEMP_EXPENSE[telegram_user_id]

        # Prepare response message
        message = data_message(expense_data)
        await self.reply_text(update, message)

        message = edit_message()
        await self.reply_text(update, message)

    async def save_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user_id = update.effective_user.id
        if telegram_user_id not in TEMP_EXPENSE:
            await self.reply_text(update, "Nothing to save, please upload a receipt first.")
            return

        expense_data = TEMP_EXPENSE.pop(telegram_user_id)  # Remove after saving to avoid duplication
        with flask_app.app_context():
            try:
                expense = expense_service.create_expense(expense_data)
                logging.info(f"Expense saved: ID {expense.id} for User {telegram_user_id} with data {expense_data}")
                await self.reply_text(update, f"✅ Expense saved successfully!\n\n")
            except Exception as e:
                logging.error(f"Error saving expense: {str(e)}")
                await self.reply_text(update, f"❌ Error saving expense: {str(e)}")

    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user_id = update.effective_user.id
        with flask_app.app_context():
            try:
                user = user_service.get_user_by_telegram_id(telegram_user_id)
                if not user:
                    await self.reply_text(update, "No expenses found.")
                    return
                expenses = expense_service.get_all_expenses(user_id=user.id)
                if not expenses:
                    await self.reply_text(update, "No expenses found.")
                    return
                
                message = "📋 <b>Your Expenses:</b>\n\n"
                for exp in expenses:
                    message += f"• ID: {exp.id}, Concept: {exp.payment_concept}, Total: ${exp.total:.2f}, Date: {exp.payment_date}\n"
                
                await self.reply_text(update, message)
            except Exception as e:
                logging.error(f"Error retrieving expenses: {str(e)}")
                await self.reply_text(update, f"❌ Error retrieving expenses: {str(e)}")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages - process receipt images."""
        await self.reply_text(update, "📸 Image received. Processing receipt... ⏳")


        try:
            
            # Download photo
            photo_file = await update.message.photo[-1].get_file()
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                await photo_file.download_to_drive(tmp_file.name)
                temp_path = tmp_file.name
                
            # Validate image
            validation = validate_image_file(os.path.basename(temp_path))

            if not validation['valid']:
                logging.warning(f"Invalid file uploaded: {validation['errors']}")
                await self.reply_text(update, f"❌ Invalid file: {', '.join(validation['errors'])}")
                delete_file(temp_path)
                return
            
            # Process receipt with Flask app context
            with flask_app.app_context():
                try:
                    # Get or create user
                    user = user_service.get_or_create_user(update)

                    # Clean and preprocess the receipt image
                    # temp_path = clean_image(temp_path)

                    # Extract data using OCR
                    expense_data = expense_service.process_receipt_image(user.id, temp_path)

                    # Clean up temporary file
                    delete_file(temp_path)

                    # Prepare response message
                    message = data_message(expense_data)
                    await self.reply_text(update, message)

                    telegram_user_id = update.effective_user.id
                    TEMP_EXPENSE[telegram_user_id] = expense_data

                    message = edit_message()
                    await self.reply_text(update, message)
                    
                except Exception as e:
                    delete_file(temp_path)
                    logging.error(f"Error processing receipt: {str(e)}")
                    await self.reply_text(update, f"❌ Error processing receipt: {str(e)}")
                    
        except Exception as e:
            logging.error(f"Error downloading image: {str(e)}")
            await self.reply_text(update, f"❌ Error downloading image: {str(e)}")

    async def income_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /income command."""
        telegram_user_id = update.effective_user.id
        args = context.args
        with flask_app.app_context():
            try:
                # Get or create user
                user = user_service.get_or_create_user(update)

                if not context.args or len(context.args) < 2:
                    await self.reply_text(update, "Invalid format.")
                    await self.reply_text(update, income_help_message())
                    return
                
                source = context.args[0]       
                try:
                    amount = float(context.args[1])
                except ValueError:
                    await self.reply_text(update, f"❌ The amount must be a valid number: {context.args[1]}")
                    logging.error(f"Invalid amount for income: {context.args[1]}")
                    return
                
                is_recurring = False
                recurrence_type = None
                income_day = None
                description = None

                args_list = list(context.args[2:])

                if '-r' in args_list:
                    is_recurring = True
                    r_index = args_list.index('-r')
                    
                    # Validate enough arguments for recurrence
                    if len(args_list) < r_index + 3:
                        await self.reply_text(update, "❌ Not enough arguments for recurring income.")
                        logging.error(f"Not enough arguments for recurring income: {args_list}")
                        return
                    
                    recurrence_type = args_list[r_index + 1].lower()
                    
                    # Validate recurrence type
                    valid_types = ['monthly', 'biweekly', 'weekly', 'daily']
                    if recurrence_type not in valid_types:
                        await self.reply_text(update, 
                            f"❌ Invalid recurrence type: `{recurrence_type}`\n\n"
                            f"Valid types: {', '.join(valid_types)}",
                        )
                        logging.error(f"Invalid recurrence type for income: {recurrence_type}")
                        return
                    
                    income_day_str = args_list[r_index + 2]
                    
                    # Validate income day(s)
                    try:
                        if ',' in income_day_str:
                            # Multiple days (for biweekly: 1,15)
                            income_day = int(income_day_str.split(',')[0])  # Keep the first one
                        else:
                            income_day = int(income_day_str)
                        
                        if income_day < 1 or income_day > 31:
                            await self.reply_text(update, "❌ The day must be between 1 and 31.")
                            logging.error(f"Invalid income day for income: {income_day}")
                            return
                            
                    except ValueError:
                        await self.reply_text(update, "❌ The day must be a valid number.")
                        logging.error(f"Invalid income day value: {income_day_str}")
                        return
                    
                    # Description is everything after
                    if len(args_list) > r_index + 3:
                        description = ' '.join(args_list[r_index + 3:])
                else:
                    # No recurrence, description is everything
                    description = ' '.join(args_list) if args_list else None
                
                # Create income
                income_data = {
                    'user_id': user.id,
                    'source': source,
                    'amount': amount,
                    'description': description,
                    'is_recurring': is_recurring,
                    'recurrence_type': recurrence_type,
                    'income_day': income_day
                }

                income = income_service.create_income(income_data)
                logging.info(f"Income saved for User {user.id} with data {income}")
                message = "✅ <b>Income Saved successfully!</b>\n\n"
                await self.reply_text(update, message)
                message = income_command(income)
                await self.reply_text(update, message)
            except Exception as e:
                logging.error(f"Error saving income: {str(e)}")
                await self.reply_text(update, f"❌ Error saving income: {str(e)}")

    async def incomes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /incomes command."""
        with flask_app.app_context():
            try:
                # Get or create user
                user = user_service.get_or_create_user(update)
                if not user:
                    await self.reply_text(update, "No incomes found.")
                    return
                
                incomes = income_service.get_incomes_by_user_id(user.id)
                if not incomes:
                    await self.reply_text(update, "No incomes found."   )
                    return

                message = "📋 <b>Your Incomes:</b>\n\n"
                await self.reply_text(update, message) 
                for inc in incomes:
                    message = income_command(inc) + "\n"
                    await self.reply_text(update, message)  
                
            except Exception as e:
                logging.error(f"Error retrieving incomes: {str(e)}")
                await self.reply_text(update, f"❌ Error retrieving incomes: {str(e)}")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages."""
        message = handle_message()
        await self.reply_text(update, message)
    
    def run(self):
        """Start the bot."""
        logging.info("Starting Expense Management Bot...")
        logging.info(f"Token {'configured' if self.token else 'not configured'}")
        self.app.run_polling()


def main():
    """Main function to run the bot."""
    if not TOKEN:
        logging.error("Error: Telegram token not found in environment variables")
        logging.info("Make sure to configure your token in the .env file")
        return
    
    # Create and run bot
    bot = ExpenseBot(TOKEN)
    bot.run()


if __name__ == '__main__':
    main()
