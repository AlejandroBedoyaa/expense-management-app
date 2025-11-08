"""
Message templates for the Expense Management Bot.
"""

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
    /income - Add a new income entry: /income &lt;source&gt; &lt;amount&gt; &lt;description&gt; -r &lt;recurrence_type&gt; &lt;income_day&gt;
    /incomes - List your income entries
    /help - Show this help

    <b>How does it work?</b>
    1. Take a clear photo of your receipt
    2. Send it to the bot
    3. The bot will automatically extract the data
    4. It will be saved in your personal database

    💡 <b>Tip</b>: Make sure the photo is clear and well-lit for best results.
    """
    return message

def data_message(data: dict) -> str:
    message = "✅ <b>Ticket processed successfully!</b>\n\n"
    message += f"<b>payment_concept</b>: {data['payment_concept'].capitalize()}\n"
    message += f"<b>category</b>: {data['category'].capitalize()}\n"
    if data.get('note'):
        message += f"<b>note</b>: {data['note']}\n"
    else:
        message += f"<b>note</b>: --\n"
    message += f"<b>date</b>: {data['payment_date']}\n"
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
    message = f"<b>amount</b>: {format_currency(data.amount)}\n"
    message += f"<b>source</b>: {data.source.capitalize()}\n"
    message += f"<b>is_recurring</b>: {'Yes' if data.is_recurring else 'No'}\n"
    if data.is_recurring:
        message += f"<b>recurrence_type</b>: {data.recurrence_type.capitalize()}\n"
        message += f"<b>income_day</b>: {data.income_day}\n"

    if data.description:
        message += f"<b>description</b>: {data.description}\n"
    else:
        message += f"<b>description</b>: --\n"

    return message

def income_help_message() -> str:
    """Help message for /income command."""
    message = """
    📥 <b>Add a new income entry</b>
    Use the command format:
    /income &lt;source&gt; &lt;amount&gt; -r &lt;is_recurring&gt; &lt;type&gt; &lt;income_day&gt; &lt;description&gt;

    <b>Parameters:</b>
    - <b>source</b>: Source of the income (e.g., Salary, Freelance)
    - <b>amount</b>: Amount received
    - <b>recurrence_type</b>: (Optional) Type of income (e.g., monthly, biweekly, weekly, daily)
    - <b>income_day</b>: (Optional) Day of the month the income is received (1-31)
    - <b>description</b>: (Optional) Description of the income

    <b>Example:</b>
    /income Salary 1500 -r yes monthly 5 "June Salary"
    """
    return message

def handle_message() -> str:
    """Handle /help command."""
    message = """
    📝 I can only process receipt images or valid commands.\n\n
    📸 Please send a photo of your receipt or command, so I can assist you.\n
    💡 Use /help to see all available commands.
    """
    return message