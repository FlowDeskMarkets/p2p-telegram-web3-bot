from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler, \
    ContextTypes
import json
from dotenv import load_dotenv
import gpt_module
import os
from circle.web3 import developer_controlled_wallets
from circle.web3 import utils
import time

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

# Start command handler
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
    print(response)
    parsed_message = json.loads(response.choices[0].message.content)

    context.user_data['parsed_message'] = parsed_message

    if (parsed_message['transaction'] == 'transfer'):
        keyboard = [
            [InlineKeyboardButton("✅ Yes", callback_data='confirm_yes')],
            [InlineKeyboardButton("❌ No", callback_data='confirm_no')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Do you want to {parsed_message['transaction']} {parsed_message['amount']} {parsed_message['currency']} to {parsed_message['to']}?", reply_markup=reply_markup)

async def confirm_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    parsed_message = context.user_data['parsed_message']

    if query.data == 'confirm_yes':
        # print(parsed_message)
        await query.edit_message_text(text=f"Pending: Sending {parsed_message['amount']} {parsed_message['currency']} to {parsed_message['to']}", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Update", callback_data='update_status')]]
        ))
        await transfer(update, parsed_message)
    elif query.data == 'confirm_no':
        await query.edit_message_text(text='Transaction cancelled.')

async def transfer(update, parsed_message) -> None:
    client = utils.init_developer_controlled_wallets_client()

    # create an api instancex
    wallets_api_instance = developer_controlled_wallets.WalletsApi(client)

    # List the balance of the wallet
    wallet_id = "2fd61b7b-b24b-541c-b373-55a90eaa008d"
    try:
        response = wallets_api_instance.list_wallet_ballance(id=f"{wallet_id}")
        # print(response)
    except developer_controlled_wallets.ApiException as e:
        print("Exception when calling WalletsApi->list_wallet_balance: %s\n" % e)

    # Transfer a token
    token_id = "36b6931a-873a-56a8-8a27-b706b17104ee"
    client = utils.init_developer_controlled_wallets_client()
    tx_api_instance = developer_controlled_wallets.TransactionsApi(client)

    try:
        request = developer_controlled_wallets.CreateTransferTransactionForDeveloperRequest.from_dict({
            "walletId": f"{wallet_id}",
            "tokenId": f"{token_id}",
            "destinationAddress": '0x2d07023e0b177ac3bdcbab9deda6be829a9561aa',
            "amounts": [f"{parsed_message['amount']}"],
            "feeLevel": 'MEDIUM'
        })
        tx_response = tx_api_instance.create_developer_transaction_transfer(request)
        tx_status_response = tx_api_instance.list_transactions(wallet_ids=wallet_id).dict()
        status = 'PENDING'
        while tx_status_response['data']['transactions'][0]['state'].value not in ['FAILED', 'CONFIRMED', 'COMPLETE']:
            query = update.callback_query
            tx_status_response = tx_api_instance.list_transactions(wallet_ids=wallet_id).dict()
            if status != tx_status_response['data']['transactions'][0]['state'].value:
                if tx_status_response['data']['transactions'][0]['state'].value == 'PENDING':
                    await query.edit_message_text(text=f"{tx_status_response['data']['transactions'][0]['state'].value} ⏳")
                if tx_status_response['data']['transactions'][0]['state'].value == 'INITIATED':
                    await query.edit_message_text(text=f"{tx_status_response['data']['transactions'][0]['state'].value} 🔄")
                if tx_status_response['data']['transactions'][0]['state'].value == 'QUEUED':
                    await query.edit_message_text(text=f"{tx_status_response['data']['transactions'][0]['state'].value} 🔄")
                if tx_status_response['data']['transactions'][0]['state'].value == 'SENT':
                    await query.edit_message_text(text=f"{tx_status_response['data']['transactions'][0]['state'].value} ↗️")
                if tx_status_response['data']['transactions'][0]['state'].value == 'CONFIRMED':
                    await query.edit_message_text(text=f"{tx_status_response['data']['transactions'][0]['state'].value} ✅")
                if tx_status_response['data']['transactions'][0]['state'].value == 'FAILED':
                    await query.edit_message_text(text=f"{tx_status_response['data']['transactions'][0]['state'].value} ❌")
            time.sleep(0.1)
            status = tx_status_response['data']['transactions'][0]['state'].value
    except developer_controlled_wallets.ApiException as e:
        print("Exception when calling TransactionsApi->create_developer_transaction_transfer: %s\n" % e)

# Main function to start the bot
def main():
    load_dotenv()

    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.getenv('TXGPT_TOKEN')).build()

    # Add handlers for the /start and /help commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language_message))
    application.add_handler(CallbackQueryHandler(
        confirm_transaction, pattern='^confirm_'))
    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
