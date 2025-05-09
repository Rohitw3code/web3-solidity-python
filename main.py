from web3 import Web3
import json

# Initialize web3 connection
def init_web3():
    web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    if not web3.is_connected():
        raise Exception("❌ Failed to connect to Ethereum node")
    
    # Load ABI from file
    with open("jobs_abi.json") as f:
        abi = json.load(f)

    # Contract address (deployed on Ganache or testnet)
    contract_address = "0xc012765F308C1F852C105b2ee1c7F683A6ef01e0"  # Replace if different
    contract = web3.eth.contract(address=contract_address, abi=abi)
    return web3, contract

# Connect to web3 and contract
web3, contract = init_web3()

# Use the first Ganache account as sender
# sender addrss from ganache
# Ganache account: 0x90b3dc5346C44DB2323d58E69bD82103661ea597
sender_address = "0x90b3dc5346C44DB2323d58E69bD82103661ea597" #web3.eth.accounts[0]
owner_address = contract.functions.owner().call()

print(f"Connected to blockchain")
print(f"Contract owner: {owner_address}")
print(f"Sender address: {sender_address}")

# Check ownership before restricted actions
def require_owner():
    if sender_address.lower() != owner_address.lower():
        raise PermissionError("Only the contract owner can perform this action")

# Add a new job to the blockchain
def add_job(title, description, threshold, max_candidates, summary):
    require_owner()
    tx_hash = contract.functions.addJob(
        title, description, threshold, max_candidates, summary
    ).transact({'from': sender_address})
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Job added. Tx Hash: {receipt.transactionHash.hex()}")

# Update a job summary
def update_job_summary(job_id, new_summary):
    require_owner()
    tx_hash = contract.functions.updateJobSummary(
        job_id, new_summary
    ).transact({'from': sender_address})
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Job summary updated. Tx Hash: {receipt.transactionHash.hex()}")

# List all jobs
def list_jobs():
    jobs = contract.functions.getAllJobs().call()
    print(f"\nJob Listings ({len(jobs)} jobs):")
    for job in jobs:
        print(f"ID: {job[0]} | Title: {job[1]} | Summary: {job[6]}")
    return jobs

# Example usage
if __name__ == "__main__":
    # Add a new job (uncomment to run)
    add_job(
        title="AI Engineer",
        description="Work with LLMs, Python, and Flask",
        threshold=80,
        max_candidates=5,
        summary="LLM integration and deployment expert"
    )

    # View jobs
    list_jobs()

    # Update a job summary (e.g., job ID 0)
    update_job_summary(job_id=1, new_summary="Updated summary for AI Engineer")

    # Confirm update
    list_jobs()
