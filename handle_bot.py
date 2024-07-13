import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('TXGPT_TOKEN')

# In-memory storage for shared contacts
user_contacts = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Please share a contact from your profile.')

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    contact = update.message.contact
    user_id = update.message.from_user.id
    
    # Store the shared contact
    if user_id not in user_contacts:
        user_contacts[user_id] = []
    user_contacts[user_id].append({
        'phone_number': contact.phone_number,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'user_id': contact.user_id
    })
    
    await update.message.reply_text(f"Contact received: {contact.first_name} {contact.last_name} (Phone: {contact.phone_number}).")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    application.run_polling()

if __name__ == '__main__':
    main()
