"""
Preprocess the user message with LLM and return the response in a JSON format

Main difficulty is prompt engineering. Example of promp:

Prompt: "Here are some functions and their arguments that we are able to use. 
- get_balance(address: str) -> float: Returns the balance of the given address.
- send_transaction(sender: str, receiver: str, amount: float) -> str: Sends the given amount from the sender to the receiver and returns the transaction hash.
- get_transaction_status(tx_hash: str) -> str: Returns the status of the given transaction hash.
- get_gas_price() -> float: Returns the current gas price.

The user is asking the following: {user_message}. Return the response in the following JSON format:
{
    "function_called": the function that the user is asking about. If not found, return None in this field
    "arg 1": the first argument of the function. If not found, return None in this field
    "arg 2": the second argument of the function. If not found, return None in this field
    etc.
}
"""