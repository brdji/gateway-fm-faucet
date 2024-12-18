from web3 import Web3

from gateway_faucet import settings


# API endpoint used to communicate with the blockchain
RPC_ENDPOINT = settings.BLOCKCHAIN_API_ENDPOINT

# Pre-funded wallet secret key
WALLET_PRIVATE_KEY = settings.WALLET_PRIVATE_KEY

# Amount of ETH to send to users (in ETH)
SEND_AMOUNT = 0.0001

# Minimum wallet balance to prevent errors (in ETH)
MIN_WALLET_BALANCE = 0.0005

# Web3 object and the account used to communicate with the blockchain
w3 = None
wallet_acc = None

import logging

logger = logging.getLogger(__name__)

# Initializes the blockchain/wallet; done on server startup
def init_wallet():
    logger.info("Initializing w3 wallet")
    global w3, wallet_acc
    w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))
    wallet_acc = w3.eth.account.from_key(WALLET_PRIVATE_KEY)


# Returns the balance of the wallet (in WEI)
def get_wallet_balance():
    balance = w3.eth.get_balance(wallet_acc.address)
    return balance


# Checks if the wallet has enough funds to execute a faucet fund request
def wallet_balance_check():
    balance = get_wallet_balance()
    if balance < w3.to_wei(MIN_WALLET_BALANCE, "ether"):
        return False
    return True


# Checks if the given address is a valid W3 address
def validate_address(address: str):
    if address is None:
        return False
    val = w3.is_address(address)
    return val


# Transfers fund from the pre-funded wallet to the given address; returns the transaction hash (ID)
def send_ETH(to_address) -> str:
    if to_address is None:
        raise "Invalid destination address"
    tx = {
        "type": "0x2",
        "nonce": w3.eth.get_transaction_count(wallet_acc.address),
        "from": wallet_acc.address,
        "to": to_address,
        "value": w3.to_wei(SEND_AMOUNT, "ether"),
        "maxFeePerGas": w3.to_wei("250", "gwei"),
        "maxPriorityFeePerGas": w3.to_wei("3", "gwei"),
        "chainId": 11155111,
    }
    gas = w3.eth.estimate_gas(tx)  # gas limit
    tx["gas"] = gas
    signed_tx = w3.eth.account.sign_transaction(tx, WALLET_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if tx_receipt["status"] == 1:
        return tx_hash.to_0x_hex()
    else:
        raise "There was an error transferring the ETH"
