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
import uuid
from circle.web3 import utils, developer_controlled_wallets
import base64
from ens.auto import ns
from web3 import HTTPProvider
from ens import ENS
import requests


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


def lookup_wallet_uuid(tg_user_id: str) -> str:
    print(f"getting wallet uuid for {tg_user_id}")
    return ns.get_text(f"{tg_user_id}.txgpt.eth", "uid")


def add_wallet_to_ens(tg_user_id: str, wallet_uuid: str):
    print(f"setting wallet uuid for {tg_user_id} to {wallet_uuid} on ENS")
    return "2fd61b7b-b24b-541c-b373-55a90eaa008d"


async def start(update: Update, context: CallbackContext) -> None:
    global circle_wallet_set_id
    tg_user_id = update.message.from_user.id
    wallet_uuid = lookup_wallet_uuid(tg_user_id)
    # if wallet_uuid is not None and len(wallet_uuid) != 0:
    #     await update.message.reply_text(
    #         "Hello! I am TxGPT Bot, your account is already ready to use !"
    #     )
    #     return

    wallet_uuid = create_wallet(tg_user_id)
    await update.message.reply_text(
        "Hello! I am TxGPT Bot, your friendly AI assistant designed to make blockchain transactions easy and accessible! Your account is already ready to use !"
    )


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

    return json.loads(response.text)["data"]["wallets"][0]["id"]


async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "You can use the following commands:\n/start - to start the bot\n/help - to get help"
    )


# Natural Message Handler


async def handle_natural_language_message(
    update: Update, context: CallbackContext
) -> None:
    user_message = update.message.text
    response = gpt_client.call_with_prompt(user_message)
    print(response.choices[0].message.content)
    # Preprocess the user message with LLM and return the response in a JSON format
    await update.message.reply_text(f"You said: {user_message}")


# Main function to start the bot


def main():
    load_dotenv()
    # Create the Application and pass it your bot's token
    global gpt_client
    global circle_client
    global circle_wallet_set_id
    circle_wallet_set_id = os.environ["CIRCLE_WALLET_SET_ID"]
    gpt_client = gpt_module.GptClient()
    circle_client = utils.init_developer_controlled_wallets_client()
    application = Application.builder().token(os.environ["TXGPT_TOKEN"]).build()

    # Add handlers for the /start and /help commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language_message)
    )

    # # Run the bot
    application.run_polling()


if __name__ == "__main__":
    main()
