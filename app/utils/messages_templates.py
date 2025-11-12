"""
Message templates for the Expense Management Bot.
"""

import os
from app.utils.helpers import format_tax, format_currency

def welcome_message(telegram_user_name: str) -> str:
    message = f"🤖 <b>Welcome {telegram_user_name}, to the Expense Management Bot</b>"

    return message

def help_message() -> str:
    message = """
    📸 <b>Send a photo of your receipt</b>
    I will automatically extract the relevant information.

    📋 <b>Bot Commands:</b>
    /edit - Edit the data: /edit &lt;field&gt; &lt;value&gt;
    /save - Confirm and save the last processed expense
    /list - List your saved expenses
    /expense - Add a new expense manually: /expense &lt;payment_concept&gt; &lt;category&gt; &lt;amount&gt; &lt;payment_date&gt; &lt;note&gt (Optional);
    /income - Add a new income entry: /income &lt;source&gt; &lt;amount&gt; &lt;income_date&gt; (Optional) &lt;description&gt; (Optional)
    /incomes - List your income entries
    /balance - Show your current balance
    /summary - Show a summary of your expenses and incomes
    /link-account - Link your Telegram account with the web app
    /help - Show this help

    <b>How does it work?</b>
    1. Take a clear photo of your receipt
    2. Send it to the bot
    3. The bot will automatically extract the data
    4. It will be saved in your personal database

    💡 <b>Tip</b>: Make sure the photo is clear and well-lit for best results.
    """
    return message

def expense_message(data: dict) -> str:
    message = f"<b>payment_concept</b>: {data['payment_concept'].capitalize()}\n"
    message += f"<b>category</b>: {data['category'].capitalize()}\n"
    if data.get('note'):
        message += f"<b>note</b>: {data['note']}\n"
    else:
        message += f"<b>note</b>: --\n"
    message += f"<b>payment_date</b>: {data['payment_date']}\n"
    message += f"<b>subtotal</b>: {format_currency(data['subtotal'])}\n"
    message += f"<b>tax</b>: {format_tax(data['tax'])}\n"
    message += f"<b>total</b>: {format_currency(data['total'])}\n"

    return message

def edit_message() -> str:
    message = "Do you want to edit any details?\n"
    message += f"Send <b>/edit</b> &lt;field&gt; &lt;value&gt;\n"
    message += f"Send <b>/save</b> to confirm the data\n"

    return message

def income_command(data: dict) -> str:
    """Handle /income command."""
    message = f"<b>source</b>: {data.source.capitalize()}\n"
    message += f"<b>amount</b>: {format_currency(data.amount)}\n"
    message += f"<b>income_date</b>: {data.income_date.strftime('%d/%m/%Y')}\n"

    if data.description:
        message += f"<b>description</b>: {data.description}\n"
    else:
        message += f"<b>description</b>: --\n"

    message += f"<b>created_at</b>: {data.created_at.strftime('%d/%m/%Y %H:%M:%S')}\n"

    return message

def income_help_message() -> str:
    """Help message for /income command."""
    message = """
    📥 <b>Add a new income entry</b>
    Use the command format:
    /income &lt;source&gt; &lt;amount&gt; &lt;income_date&gt; (Optional) &lt;description&gt; (Optional)

    <b>Parameters:</b>
    - <b>source</b>: Source of the income (e.g., Salary, Freelance)
    - <b>amount</b>: Amount received
    - <b>income_date</b>: (Optional) Date of income (day of month for monthly, day of week for weekly/biweekly)
    - <b>description</b>: (Optional) Description of the income

    <b>Example:</b>
    /income Salary 1500 15-11 "June Salary"
    """
    return message

def balance_message(data: dict) -> str:
    """Generate balance summary message."""
    month_names = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    message = f"📊 <b>Balance Summary for {month_names[data['month']]} {data['year']}</b>\n\n"
    message += f"📥 <b>Total Incomes:</b> {format_currency(data['total_incomes'])}\n"
    message += f"📤 <b>Total Expenses:</b> {format_currency(data['total_expenses'])}\n"
    message += "─" * 30 + "\n"
    message += f"🔄 <b>Net Balance:</b> {format_currency(data['balance'])}\n"

    balance = data['balance']
    if balance >= 0:
        message += f"✅ <b>Balance:</b> ${balance:,.2f}\n"
        message += f"📊 <b>Save:</b> {data['balance_percentage']:.1f}%"
    else:
        message += f"⚠️ <b>Balance:</b> -${abs(balance):,.2f}\n"
        message += f"📊 <b>Deficit:</b> {abs(data['balance_percentage']):.1f}%"

    return message

def summary_message(summary: dict, data: dict) -> str:
    """Generate financial summary message."""
    month_names = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    message = f"📊 <b>Financial Summary for {month_names[data['month']]} {data['year']}</b>\n\n"
    message += f"📈 Ingresos: ${data['total_incomes']:,.2f}\n"
    message += f"📉 Gastos: ${data['total_expenses']:,.2f}\n"

    balance = data['balance']
    if balance >= 0:
        message += f"✅ Balance: ${balance:,.2f}\n\n"
    else:
        message += f"⚠️ Balance: -${abs(balance):,.2f}\n\n"
    
    # Top categorías de gasto
    if summary['top_categories']:
        message += "<b>🏆 Top Gastos por Categoría:</b>\n"
        for category, summary_data in summary['top_categories']:
            percentage = (summary_data['total'] / data['total_expenses'] * 100) if data['total_expenses'] > 0 else 0
            message += f"  • {category.capitalize()}: ${summary_data['total']:,.2f} ({percentage:.1f}%)\n"
    

    return message

def link_account_message(token: str) -> str:
    TOKEN_EXPIRATION_MINUTES = int(os.getenv('TOKEN_EXPIRATION_MINUTES', 15))
    link_url = f"{os.getenv('DASHBOARD_URL')}/link-account?token={token}"
    message = f"🔗 Use the following link to link your account:\n\n{link_url}"
    message += "\n\nAlternatively, you can use the token below in the dashboard:"
    message += f"\n\n<b>Token:</b> <code>{token}</code>"
    message += f"\n\nThis link will expire in {TOKEN_EXPIRATION_MINUTES} minutes."

    return message

def handle_message() -> str:
    """Handle /help command."""
    message = """
    📝 I can only process receipt images or valid commands.\n\n
    📸 Please send a photo of your receipt or command, so I can assist you.\n
    💡 Use /help to see all available commands.
    """
    return message