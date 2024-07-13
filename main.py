from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler, \
    ContextTypes
from dotenv import load_dotenv
import gpt_module
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    filters,
)
import json
from dotenv import load_dotenv
import os
from circle.web3 import developer_controlled_wallets
from circle.web3 import utils
import time
import asyncio


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
import uuid
from circle.web3 import utils, developer_controlled_wallets
import base64
from ens.auto import ns
from web3 import HTTPProvider
from ens import ENS
import requests
import ens_module


import base64
import codecs

# Installed by `pip install pycryptodome`
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256

# Start command handler

CREATE_WALLET_URL = "https://api.circle.com/v1/w3s/developer/wallets"

provider = HTTPProvider("https://ethereum-sepolia-rpc.publicnode.com")
ns = ENS(provider)

global gpt_client
global circle_client
global circle_wallet_set_id


def lookup_wallet_uuid(tg_user_id: str, chain: str) -> str:
    print(f"getting wallet uuid for {tg_user_id}")
    return ns.get_text(f"{tg_user_id}.txgpt.eth", "uid")


def add_wallet_to_ens(tg_user_id: str, wallet_uuid: str):
    print(f"setting wallet uuid for {tg_user_id} to {wallet_uuid} on ENS")
    return "2fd61b7b-b24b-541c-b373-55a90eaa008d"


async def start(update: Update, context: CallbackContext) -> None:
    welcome_message = (
            "👋 Hello! Welcome to TxGPT Bot!\n\n"
            "I’m here to help you with your blockchain transactions and keep you updated on their status. "
            "You can use me to send and receive cryptocurrency, check your balance, and more.\n\n"
            "Here's what I can do:\n"
            "🔹 *Send Crypto*: Easily send cryptocurrency to any address.\n"
            "🔹 *Receive Crypto*: Check your wallet for incoming transactions.\n"
            "🔹 *Transaction Status*: Get real-time updates on your transactions.\n\n"
            "🔹 *LLM Functions*: As you would ask any LLM, get information, and much more.\n\n"

            "You can talk to me like a human! Just type your message and I'll do my best to help you out. "
            
            "Let's make some transactions! 🚀"
        )

    tg_user_id = update.message.from_user.id
    wallet_uuid = lookup_wallet_uuid(tg_user_id, 'MATIC-AMOY')
    print(f"found wallet uuid for {tg_user_id} on MATIC-AMOY: {wallet_uuid}")
    if wallet_uuid is not None and len(wallet_uuid) != 0:
        await update.message.reply_text(
            welcome_message
        )
    else:
        await update.message.reply_text(
            welcome_message
        )

    # Send message with inline keyboard
    keyboard = [
        [InlineKeyboardButton("🤩 Yes", callback_data='create_wallets_yes')],
        [InlineKeyboardButton("😔 No", callback_data='create_wallets_no')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💼 Let's get you started with some wallets!\n\n"
        "Creating wallets will enable you to send and receive cryptocurrency seamlessly. "
        "Would you like to create wallets now?",
        reply_markup=reply_markup)
    
    # await update.message.reply_text(
    #     "Hello! I am TxGPT Bot, your friendly AI assistant designed to make blockchain transactions easy and accessible! Your account is already ready to use !"
    # )

# Callback query handler for wallet creation decision
async def handle_wallet_creation_decision(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    tg_user_id = query.from_user.id

    if query.data == 'create_wallets_yes':
        await query.edit_message_text(text="Great! Let's create some wallets for you. 🔨")
        await asyncio.sleep(10)  # Simulate a brief delay
        # Send friendly messages during the process
        await query.message.reply_text("Hang tight, we're setting up your wallets! 🚀")
        await asyncio.sleep(10)  # Simulate a brief delay
        await query.message.reply_text("💡 Did you know? The very first purchase made with Bitcoin was for two pizzas in 2010! A programmer named Laszlo Hanyecz paid 10,000 BTC for two Papa John's pizzas. 🍕")
        await asyncio.sleep(10)  # Simulate a brief delay
        await query.message.reply_text("Creating secure wallets for you... 🔒")

        # Wallet creation logic
        wallets = create_wallet(tg_user_id)
        ens_module.create_subdomain(tg_user_id)
        for (wallet_id, chain) in wallets:
            ens_module.set_text_record(tg_user_id, chain, wallet_id)
        
        await query.message.reply_text("Your wallets have been created successfully! ✅")
        
    elif query.data == 'create_wallets_no':
        await query.edit_message_text(text="No problem! You can create wallets anytime by sending me a message.")


def get_wallet(uid: str):
    wallet_client = developer_controlled_wallets.WalletsApi(circle_client)
    get_wallet_response = wallet_client.get_wallet(uid)
    print(uid)
    print(get_wallet_response)


def get_all_wallets():
    wallet_client = developer_controlled_wallets.WalletsApi(circle_client)
    get_wallets_response = wallet_client.get_wallets(page_size=50)
    print(len(get_wallets_response.data.wallets))


def create_cipher_text():
    public_key_string = utils.get_public_key()
    hex_encoded_entity_secret = os.environ["CIRCLE_ENTITY_SECRET"]
    entity_secret = bytes.fromhex(hex_encoded_entity_secret)

    if len(entity_secret) != 32:
        print("invalid entity secret")
        exit(1)

    public_key = RSA.importKey(public_key_string)

    # encrypt data by the public key
    cipher_rsa = PKCS1_OAEP.new(key=public_key, hashAlgo=SHA256)
    encrypted_data = cipher_rsa.encrypt(entity_secret)
    encrypted_data_base64 = base64.b64encode(encrypted_data)

    return encrypted_data_base64.decode("utf-8")


def create_wallet(tg_user_id: str):
    payload = {
        "idempotencyKey": str(uuid.uuid4()),
        "accountType": "SCA",
        "blockchains": [
            "MATIC-AMOY",
            "ETH-SEPOLIA",
        ],
        "count": 1,
        "entitySecretCiphertext": create_cipher_text(),
        "metadata": [{"name": f"{tg_user_id}", "refId": f"{tg_user_id}"}],
        "walletSetId": os.environ["CIRCLE_WALLET_SET_ID"],
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {os.environ['CIRCLE_WEB3_API_KEY']}",
    }

    response = requests.post(
        CREATE_WALLET_URL, json=payload, headers=headers, timeout=30
    )
    if response.status_code != 201:
        print(json.loads(response.text))

    return list(map(lambda x: (x["id"], x["blockchain"]), json.loads(response.text)["data"]["wallets"]))


async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "You can use the following commands:\n/start - to start the bot\n/help - to get help"
    )


async def handle_natural_language_message(
    update: Update, context: CallbackContext
) -> None:
    user_message = update.message.text
    response = gpt_client.call_with_prompt(user_message)
    parsed_message = json.loads(response.choices[0].message.content)
    # Preprocess the user message with LLM and return the response in a JSON format
    # await update.message.reply_text(f"You said: {user_message}")

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
                    state = tx_status_response['data']['transactions'][0]['state'].value
                    if state == 'PENDING':
                        await query.edit_message_text(text="Your transaction is pending. We're working on it! ⏳")
                    elif state == 'INITIATED':
                        await query.edit_message_text(text="Your transaction has been initiated. Hang tight! 🔄")
                    elif state == 'QUEUED':
                        await query.edit_message_text(text="Your transaction is queued and will be processed shortly. 🔄")
                    elif state == 'SENT':
                        await query.edit_message_text(text="Your transaction has been sent to the network. Almost there! ↗️")
                    elif state == 'CONFIRMED':
                        await query.edit_message_text(text="Success! Your transaction is confirmed. ✅")
                    elif state == 'FAILED':
                        await query.edit_message_text(text="Oops! Your transaction has failed. Please try again. ❌")

            time.sleep(0.1)
            status = tx_status_response['data']['transactions'][0]['state'].value
    except developer_controlled_wallets.ApiException as e:
        print("Exception when calling TransactionsApi->create_developer_transaction_transfer: %s\n" % e)

# Main function to start the bot
def main():
    load_dotenv()

    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.getenv('TXGPT_TOKEN')).build()
    global gpt_client
    global circle_client
    global circle_wallet_set_id
    circle_wallet_set_id = os.environ["CIRCLE_WALLET_SET_ID"]
    gpt_client = gpt_module.GptClient()
    circle_client = utils.init_developer_controlled_wallets_client()
    application = Application.builder().token(os.environ["TXGPT_TOKEN"]).build()
    ens_module.init()

    # Add handlers for the /start and /help commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language_message))
    application.add_handler(CallbackQueryHandler(
        confirm_transaction, pattern='^confirm_'))
    application.add_handler(CallbackQueryHandler(handle_wallet_creation_decision, pattern='^create_wallets_'))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
