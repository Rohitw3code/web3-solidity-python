from web3 import Web3
import json

# Connect to Ganache or Sepolia
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Load ABI
with open("abi.json") as f:
    abi = json.load(f)

contract_address = "0xa3855A364597cc42efaa82e4021DeB5AAF922A0c"
contract = web3.eth.contract(address=contract_address, abi=abi)

sender_address = web3.eth.accounts[0]

# 1. Add a task
# task_to_add = "Write Python script"
# tx_hash = contract.functions.addTodo(task_to_add).transact({'from': sender_address})
# receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
# print(f"Task added. Transaction hash: {receipt.transactionHash.hex()}")


# Example: Read from the contract
# task, completed = contract.functions.getTodo(2).call()
# print(task, completed)

all_task = contract.functions.getAllTodo().call()
print(all_task)
