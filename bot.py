#!/usr/bin/env python3
"""
Telegram Bot for Expense Management
Handles ticket image processing and expense creation via Telegram.

Command to run:
    python bot.py
"""

from multiprocessing import context
from app.utils.logging_config import setup_logging
setup_logging()
import logging
from telegram import Update, User
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import sys
import tempfile
import asyncio
from datetime import date, datetime
from dotenv import load_dotenv
import uuid

# Import from our refactored structure
from app import create_app
from app.services.expense_service import expense_service
from app.services.user_service import user_service
from app.services.income_service import income_service
from app.services.balance_service import balance_service
from app.utils.helpers import delete_file, clean_image, parse_date, utc_now
from app.utils.validators import validate_image_file
from app.utils.messages_templates import (dashboard_message, expense_help_message, income_command, income_help_message, new_balance_message, welcome_message, help_message, expense_message,
                                        edit_message, handle_message, balance_message, summary_message, link_account_message)

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
        self.app.add_handler(CommandHandler("expenses", self.expenses_command))
        self.app.add_handler(CommandHandler("cancel", self.cancel_command))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(CommandHandler("expense", self.expense_command))
        self.app.add_handler(CommandHandler("help_expense", self.expense_help_command))
        self.app.add_handler(CommandHandler("income", self.income_command))
        self.app.add_handler(CommandHandler("help_income", self.income_help_command))
        self.app.add_handler(CommandHandler("incomes", self.incomes_command))
        self.app.add_handler(CommandHandler("balance", self.balance_command))
        self.app.add_handler(CommandHandler("summary", self.summary_command))
        self.app.add_handler(CommandHandler("link_account", self.link_account_command))
        self.app.add_handler(CommandHandler("dashboard", self.dashboard_command))
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
            await self.reply_text(update, "Nothing to edit, first send a ticket photo.")
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
        message = expense_message(expense_data)
        logging.info(f"Expense message edited for User {telegram_user_id}: {message}")
        await self.reply_text(update, message)

        message = edit_message()
        await self.reply_text(update, message)

    async def save_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user_id = update.effective_user.id
        if telegram_user_id not in TEMP_EXPENSE:
            await self.reply_text(update, "Nothing to save, please upload a ticket first.")
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

            try:
                # Update user's accumulated balance
                user = user_service.get_user_by_telegram_id(str(telegram_user_id))
                if user:
                    user_upd = user_service.update_accumulated_balance(user.id, -expense.total)
                    message = new_balance_message(user_upd.accumulated_balance)
                    logging.info(f"Updated accumulated balance for User {user.id}")
                    await self.reply_text(update, message)
            except Exception as e:
                logging.error(f"Error updating accumulated balance: {str(e)}")
                await self.reply_text(update, f"❌ Error updating user accumulated balance: {str(e)}")

    async def expenses_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                logging.info(f"Expenses for User {user.id}: {expenses}")
                for exp in expenses:
                    message += f"• Concept: {exp.payment_concept}, Total: ${exp.total:.2f}, Date: {exp.payment_date}\n"
                
                await self.reply_text(update, message)
            except Exception as e:
                logging.error(f"Error retrieving expenses: {str(e)}")
                await self.reply_text(update, f"❌ Error retrieving expenses: {str(e)}")

    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command to cancel ongoing expense entry."""
        telegram_user_id = update.effective_user.id
        if telegram_user_id in TEMP_EXPENSE:
            TEMP_EXPENSE.pop(telegram_user_id)
            await self.reply_text(update, "✅ Expense entry canceled.")
        else:
            await self.reply_text(update, "No ongoing expense entry to cancel.")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages - process ticket images."""
        await self.reply_text(update, "📸 Image received. Processing ticket... ⏳")

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
            
            # Process ticket with Flask app context
            with flask_app.app_context():
                try:
                    # Get or create user
                    user = user_service.get_or_create_user(update)

                    # Clean and preprocess the ticket image
                    # temp_path = clean_image(temp_path)

                    # Extract data using OCR
                    expense_data = expense_service.process_ticket_image(user.id, temp_path)

                    # Clean up temporary file
                    delete_file(temp_path)

                    # Prepare response message
                    message = "✅ <b>Ticket processed successfully!</b>\n\n"
                    await self.reply_text(update, message)
                    message = expense_message(expense_data)
                    await self.reply_text(update, message)

                    telegram_user_id = update.effective_user.id
                    TEMP_EXPENSE[telegram_user_id] = expense_data

                    message = edit_message()
                    await self.reply_text(update, message)
                    
                except Exception as e:
                    delete_file(temp_path)
                    logging.error(f"Error processing ticket: {str(e)}")
                    await self.reply_text(update, f"❌ Error processing ticket: {str(e)}")
                    
        except Exception as e:
            logging.error(f"Error downloading image: {str(e)}")
            await self.reply_text(update, f"❌ Error downloading image: {str(e)}")

    async def expense_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle manual expense entry."""

        with flask_app.app_context():
            try:
                # Get or create user
                user = user_service.get_or_create_user(update)

                args = context.args
                if not args or len(args) < 3:
                    await self.reply_text(update, "Invalid format.")
                    return
                
                payment_concept = args[0]
                try:
                    total = float(args[1])
                except ValueError:
                    await self.reply_text(update, f"❌ The total must be a valid number: {args[1]}")
                    logging.error(f"Invalid total for expense: {args[1]}")
                    return
                
                try:
                    # Validate format DD-MM (day-month)
                    day, month = map(int, args[2].split('-'))
                    current_year = date.today().year
                    payment_date = date(current_year, month, day)
                except ValueError:
                    await self.reply_text(update, f"❌ The date must be in DD-MM format: {args[2]}")
                    logging.error(f"Invalid date for expense: {args[2]}")
                    return
                
                category = args[3] if len(args) >= 4 else 'uncategorized'
                tax = 16.0
                subtotal = total / (tax / 100 + 1)
                # Prepare expense data
                expense_data = {
                    'user_id': user.id,
                    'payment_concept': payment_concept.upper(),
                    'total': total,
                    'payment_date': parse_date(payment_date or date.today()),
                    'category': category.lower(),
                    'tax': tax,
                    'subtotal': subtotal
                }
                
                # Prepare response message
                message = expense_message(expense_data)
                await self.reply_text(update, message)

                telegram_user_id = update.effective_user.id
                TEMP_EXPENSE[telegram_user_id] = expense_data

                message = edit_message()
                await self.reply_text(update, message)
                
            except Exception as e:
                logging.error(f"Error saving expense: {str(e)}")
                await self.reply_text(update, f"❌ Error saving expense: {str(e)}")

    async def expense_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help_expense command."""
        message = expense_help_message()
        await self.reply_text(update, message)

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
                
                income_date = date.today()
                description = None

                if len(args) >= 3:
                    income_date_str = args[2]
                    # Validate income date
                    try:
                        # Validate format DD-MM (day-month)
                        day, month = map(int, income_date_str.split('-'))
                        current_year = date.today().year
                        income_date = date(current_year, month, day)
                        if len(args) > 3:
                            description = ' '.join(args[3:])
                    except ValueError:
                        description = ' '.join(args[2:])

                elif len(args) == 2:
                    # No income date provided, use today's date
                    pass
                
                # Create income
                income_data = {
                    'user_id': user.id,
                    'source': source,
                    'amount': amount,
                    'description': description,
                    'income_date': income_date
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

            try:
                # Update user's accumulated balance
                user = user_service.get_user_by_telegram_id(str(telegram_user_id))
                if user:
                    user_upd = user_service.update_accumulated_balance(user.id, amount)
                    message = new_balance_message(user_upd.accumulated_balance)
                    logging.info(f"Updated accumulated balance for User {user.id}")
                    await self.reply_text(update, message)
            except Exception as e:
                logging.error(f"Error updating accumulated balance: {str(e)}")
                await self.reply_text(update, f"❌ Error updating user accumulated balance: {str(e)}")

    async def income_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help_income command."""
        message = income_help_message()
        await self.reply_text(update, message)

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
                logging.info(f"Incomes for User {user.id}: {incomes}")
                await self.reply_text(update, message) 
                for inc in incomes:
                    message = income_command(inc) + "\n"
                    await self.reply_text(update, message)  
                
            except Exception as e:
                logging.error(f"Error retrieving incomes: {str(e)}")
                await self.reply_text(update, f"❌ Error retrieving incomes: {str(e)}")

    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /balance command - Show current month balance
        """
        with flask_app.app_context():
            try:
                user = user_service.get_or_create_user(update)
                
                balance_data = balance_service.get_monthly_balance(user.id)

                message = balance_message(balance_data)
                logging.info(f"Balance for User {user.id}: {balance_data}")
                await self.reply_text(update, message)
                
            except Exception as e:
                logging.error(f"Error in balance_command: {str(e)}")
                await self.reply_text(update, "❌ Error to calculate balance.")

    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /resumen command - Show financial summary with categories
        """
        with flask_app.app_context():
            try:
                user = user_service.get_or_create_user(update)
                
                summary = balance_service.get_financial_summary(user.id)
                balance_data = summary['balance']

                message = summary_message(summary, balance_data)
                logging.info(f"Summary for User {user.id}: {summary}")
                await self.reply_text(update, message)                
            except Exception as e:
                logging.error(f"Error in summary_command: {str(e)}")
                await self.reply_text(update, "❌ Error to generate summary.")

    async def link_account_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /link command."""
        telegram_user_id = update.effective_user.id
        with flask_app.app_context():
            try:
                user = user_service.get_user_by_telegram_id(telegram_user_id)
                if not user:
                    message = "❌ You need to start using the bot first by sending a ticket image or creating an expense/income."
                    await self.reply_text(update, message)
                    return
                if user.is_linked:
                    message = "❌ Your account is already linked, use your existing account."
                    await self.reply_text(update, message)
                    return

                token = uuid.uuid4().hex
                user.vinculation_token = token
                user.vinculation_token_created = utc_now()
                user_service.update_user(user.id, {
                    "vinculation_token": user.vinculation_token,
                    "vinculation_token_created": user.vinculation_token_created
                })
                message = link_account_message(token)
                logging.info(f"Link token generated for User {user.id}: {token}")
                await self.reply_text(update, message)
            except Exception as e:
                logging.error(f"Error generating link token: {str(e)}")
                await self.reply_text(update, f"❌ Error generating link token: {str(e)}")

    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /dashboard command."""
        message = dashboard_message()
        await self.reply_text(update, message)

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
