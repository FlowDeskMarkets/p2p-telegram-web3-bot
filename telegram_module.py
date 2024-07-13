from telegram import Update, ReplyKeyboardMarkup,  KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, ContextTypes, ConversationHandler
import json
from dotenv import load_dotenv
import gpt_module
import os
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)


# Define states for the conversation
ASK_CONTACT = 1

user_data = {}

async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name or ""
    username = update.message.from_user.username
    user_data[user_id] = {'username': username, 'first_name': first_name, 'last_name': last_name}
    await update.message.reply_text('Hello! I am TxGPT Bot, your friendly AI assistant designed to make blockchain transactions easy and accessible!')
    print(f"User ID: {user_id} - First Name: {first_name} - Last Name: {last_name} - Username: {username}")
    return ConversationHandler.END

# Help command handler

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('You can use the following commands:\n/start - to start the bot\n/help - to get help')

async def ask_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact_button = KeyboardButton(text="Share Contact", request_contact=True)
    custom_keyboard = [[contact_button]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    await update.message.reply_text('Please share a contact.', reply_markup=reply_markup)
    return ASK_CONTACT

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact = update.message.contact
    user_data[contact.user_id] = {
        'phone_number': contact.phone_number,
        'first_name': contact.first_name,
        'last_name': contact.last_name or "",
    }
    await update.message.reply_text(f'Contact received: {contact.first_name} {contact.last_name} (ID: {contact.user_id}).')
    return ConversationHandler.END


# Natural Message Handler

async def handle_natural_language_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    # Preprocess the user message with LLM and return the response in a JSON format
    await update.message.reply_text(f'You said: {user_message}')



# Main function to start the bot


def main():
    load_dotenv()
    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.environ['TXGPT_TOKEN']).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('share_contact', ask_contact)],
        states={
            ASK_CONTACT: [MessageHandler(filters.CONTACT, handle_contact)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add handlers for the /start and /help commands
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language_message))

    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()
