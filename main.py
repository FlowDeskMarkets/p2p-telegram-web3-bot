
from dotenv import load_dotenv
import gpt_module
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import json
from dotenv import load_dotenv
import os
import uuid
from circle.web3 import utils, developer_controlled_wallets
import base64
from ens.auto import ns
# Start command handler

global gpt_client
global circle_client
global circle_wallet_set_id

def lookup_wallet_uuid(tg_user_id: str):
    print(f"getting wallet uuid for {tg_user_id}")
    return '2fd61b7b-b24b-541c-b373-55a90eaa008d'

async def start(update: Update, context: CallbackContext) -> None:
    global circle_wallet_set_id
    wallet_uuid = lookup_wallet_uuid(update.message.from_user.id)
    # if wallet_uuid is not None:
    #     await update.message.reply_text('Hello! I am TxGPT Bot, your account is already ready to use !')
    #     return
    
    wallet_client = developer_controlled_wallets.WalletsApi(circle_client)
    create_wallet_response = wallet_client.create_wallet(
        create_wallet_request=developer_controlled_wallets.CreateWalletRequest.from_dict(
            {        
                "accountType": 'SCA',
                "blockchains": ['MATIC-AMOY'],
                "walletSetId": circle_wallet_set_id,
            }
        )
    )
    print(create_wallet_response)
    await update.message.reply_text('Hello! I am TxGPT Bot, your friendly AI assistant designed to make blockchain transactions easy and accessible! Your account is already ready to use !') 

# Help command handler


async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('You can use the following commands:\n/start - to start the bot\n/help - to get help')

# Natural Message Handler

async def handle_natural_language_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = gpt_client.call_with_prompt(user_message)
    print(response.choices[0].message.content)
    # Preprocess the user message with LLM and return the response in a JSON format
    await update.message.reply_text(f'You said: {user_message}')


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
    
    application = Application.builder().token(os.environ['TXGPT_TOKEN']).build()

    # Add handlers for the /start and /help commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language_message))

    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()
