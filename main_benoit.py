from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import json
from dotenv import load_dotenv
import gpt_module
import os
import time
from circle.web3 import developer_controlled_wallets
from circle.web3 import utils
import base64


# Token Mapping
TOKEN_MAPPING = {
    'MATIC': {
        'token_id': '0c8f8485-f74f-5e28-80f2-3cc4e80ef71c',
        'token_address': ''
        },
    'USDC': {
        'token_id': '36b6931a-873a-56a8-8a27-b706b17104ee',
        'token_address': '0x41e94eb019c0762f9bfcf9fb1e58725bfb0e7582'
    }
}

# Global variables
circle_transaction_params = {
        "walletId": 'ce714f5b-0d8e-4062-9454-61aa1154869b', # Wallet of the sender
        "tokenId": 'e4f549f9-a910-59b1-b5cd-8f972871f5db', # Token 
        "destinationAddress": '0xc90e058234d4b2db799d787a855ec68d801a53a3', # Address of the receiver
        "amounts": [1],
        "feeLevel": 'MEDIUM',
}


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am TxGPT Bot, your friendly AI assistant designed to make blockchain transactions easy and accessible!')

# Help command handler


async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('You can use the following commands:\n/start - to start the bot\n/help - to get help')

# Natural Message Handler


async def handle_natural_language_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    client = gpt_module.GptClient()
    response = client.call_with_prompt(user_message)
    parsed_message = json.loads(response.choices[0].message.content)
    print(response.choices[0].message)
    print(parsed_message)
    # Preprocess the user message with LLM and return the response in a JSON format
    # await update.message.reply_text(f'You said: {user_message}')

    keyboard = [
        [InlineKeyboardButton("✅ Yes", callback_data='confirm_yes')],
        [InlineKeyboardButton("❌ No", callback_data='confirm_no')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await transfer(None)

    await update.message.reply_text(f"Do you want to {parsed_message['transaction']} {parsed_message['amount']} {parsed_message['currency']} to {parsed_message['to']}?", reply_markup=reply_markup)

async def transfer(response) -> None:
    entity_secret_cyphertext = os.getenv('ENTITY_SECRET_CIPHERTEXT')
    key = os.getenv('CIRCLE_API_KEY')
    client = utils.init_developer_controlled_wallets_client(api_key=key, entity_secret=entity_secret_cyphertext)

    # create an api instance
    api_instance = developer_controlled_wallets.WalletsApi(client)

    # List the balance of the wallet
    wallet_id = "2fd61b7b-b24b-541c-b373-55a90eaa008d"
    try:
        response = api_instance.list_wallet_ballance(id=f"{wallet_id}")
        print(response)
    except developer_controlled_wallets.ApiException as e:
        print("Exception when calling WalletsApi->list_wallet_balance: %s\n" % e)

    # Transfer a token
    api_instance = developer_controlled_wallets.TransactionsApi(client)
    token_id = "36b6931a-873a-56a8-8a27-b706b17104ee"
    try:
        request = developer_controlled_wallets.CreateTransferTransactionForDeveloperRequest.from_dict({
            "walletId": f"{wallet_id}",
            "tokenId": f"{token_id}",
            "destinationAddress": '0x2d07023e0b177ac3bdcbab9deda6be829a9561aa',
            "amounts": ['0.1'],
            "feeLevel": 'MEDIUM'
        })
        response = api_instance.create_developer_transaction_transfer(request)
        print(response)
    except developer_controlled_wallets.ApiException as e:
        print("Exception when calling TransactionsApi->create_developer_transaction_transfer: %s\n" % e)


async def confirm_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'confirm_yes':
        await query.edit_message_text(text=f"Pending: Sending 1 ETH to vitalik", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Update", callback_data='update_status')]]
        ))
        # Simulate transaction initiation
        time.sleep(5)
    elif query.data == 'confirm_no':
        await query.edit_message_text(text='Transaction cancelled.')


# Main function to start the bot


def main():
    load_dotenv()
    # Create the Application and pass it your bot's token

    application = Application.builder().token(
        os.environ['TXGPT_TOKEN']).build()

    # Add handlers for the /start and /help commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_natural_language_message))
    application.add_handler(CallbackQueryHandler(
        confirm_transaction, pattern='^confirm_'))

    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()
