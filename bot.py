from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import json

keys = json.load(open('api_keys.json'))
TELEGRAM_TOKEN = keys["txgpt_token"]

# Start command handler


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am TxGPT Bot, your friendly AI assistant designed to make blockchain transactions easy and accessible!')

# Help command handler


async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('You can use the following commands:\n/start - to start the bot\n/help - to get help')

# Natural Message Handler

async def handle_natural_language_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    # Preprocess the user message with LLM and return the response in a JSON format
    await update.message.reply_text(f'You said: {user_message}')


# Main function to start the bot


def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers for the /start and /help commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language_message))

    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()