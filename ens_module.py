import os
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
from eth_utils import keccak
import ens_abi
from hexbytes import HexBytes

global web3
global resolver_contract
global account
global private_key
global name_wrapper_contract

# Parent domain and subdomain details
parent_domain = "txgpt.eth"
# ENS Resolver contract address for Sepolia (testnet)
resolver_address = '0x8FADE66B79cC9f707aB26799354482EB93a5B7dD'
# ENS Registry contract address for Sepolia (testnet)
name_wrapper_address = '0x0635513f179D50A207757E05759CbD106d7dFcE8'

def namehash(name):
    """Generates the ENS namehash for a given domain."""
    node = b'\x00' * 32
    if name:
        labels = name.split('.')
        for label in reversed(labels):
            labelhash = keccak(text=label)
            node = keccak(node + labelhash)
    return HexBytes(node)

parent_node = namehash(parent_domain).hex()

def init():
    global web3
    global resolver_contract
    global account
    global private_key
    global name_wrapper_contract
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
    name_wrapper_contract = web3.eth.contract(address=name_wrapper_address, abi=ens_abi.ens_name_wrapper_abi)

# Create the subdomain
def set_text_record(subdomain: str, key: str, value: str):
    subdomain_label_hash = keccak(text=str(subdomain))
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
    transaction = name_wrapper_contract.functions.setSubnodeRecord(
        parent_node,
        str(subdomain),  # label of the subdomain
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
