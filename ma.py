from web3 import Web3
import json

# Connect to Ganache or Sepolia
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Load ABI
with open("abi.json") as f:
    abi = json.load(f)

contract_address = "0xa3855A364597cc42efaa82e4021DeB5AAF922A0c"
contract = web3.eth.contract(address=contract_address, abi=abi)

# Example: Read from the contract
task, completed = contract.functions.getTodo(1).call()
print(task, completed)
