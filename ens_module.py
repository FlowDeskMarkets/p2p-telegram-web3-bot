import os
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
from eth_utils import keccak
import ens_abi


global web3
global resolver_contract
global account
global private_key
global registry_contract

# Parent domain and subdomain details
parent_domain = "txgpt.eth"
# ENS Resolver contract address for Sepolia (testnet)
resolver_address = '0x8FADE66B79cC9f707aB26799354482EB93a5B7dD'
# ENS Registry contract address for Sepolia (testnet)
registry_address = '0x0635513f179D50A207757E05759CbD106d7dFcE8'
parent_node = keccak(text=parent_domain)

def init():
    global web3
    global resolver_contract
    global account
    global private_key
    global registry_contract
    infura_url = "https://sepolia.infura.io/v3/" + os.environ['INFURA_TOKEN']
    web3 = Web3(Web3.HTTPProvider(infura_url))

    # For some testnets like Sepolia, you might need to use the POA middleware
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    # Check if connected
    if not web3.is_connected():
        raise Exception("Web3 is not connected")

    # Your wallet private key
    private_key = os.environ['PRIVATE_KEY']  # Or use directly if not using dotenv

    # Set up your account
    account = Account.from_key(private_key)
        
    # Create contract instance
    resolver_contract = web3.eth.contract(address=resolver_address, abi=ens_abi.resolver_abi)
    # Create contract instance
    registry_contract = web3.eth.contract(address=registry_address, abi=ens_abi.ens_registry_abi)

# Create the subdomain
def set_text_record(subdomain: str, key: str, value: str):
    subdomain_label_hash = keccak(text=subdomain)
    subdomain_node = Web3.solidity_keccak(['bytes32', 'bytes32'], [parent_node, subdomain_label_hash])

    transaction = resolver_contract.functions.setText(
        subdomain_node,  # node (namehash of the subdomain)
        key,
        value,
    ).build_transaction({
        'chainId': 11155111,  # Sepolia testnet chain ID
        'gas': 200000,
        'gasPrice': web3.to_wei('10', 'gwei'),
        'nonce': web3.eth.get_transaction_count(account.address),
    })

    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt

def create_subdomain(subdomain: str):
    print(parent_node)
    transaction = registry_contract.functions.setSubnodeRecord(
        parent_node,
        subdomain,  # label of the subdomain
        account.address,  # owner address of the new subdomain
        resolver_address,  # resolver address
        0,  # time-to-live
        0,  # fuses
        0  # expiry
    ).build_transaction({
        'chainId': 11155111,  # Sepolia testnet chain ID
        'gas': 2000000,
        'gasPrice': web3.to_wei('10', 'gwei'),
        'nonce': web3.eth.get_transaction_count(account.address),
    })

    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt
