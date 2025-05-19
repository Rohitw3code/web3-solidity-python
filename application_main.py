import json
from web3 import Web3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connect to Ethereum node (e.g., Ganache)
WEB3_PROVIDER_URI = 'http://127.0.0.1:7545'  # Replace with your provider (e.g., Infura, Alchemy)
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

# Check connection
if not w3.is_connected():
    raise Exception("Failed to connect to Ethereum node")

# Contract details
CONTRACT_ADDRESS = '0x659fE789614b698Fe1bD1CEcc40133ccdc9B945d'  # Replace with actual contract address
OWNER_ADDRESS = '0x90b3dc5346C44DB2323d58E69bD82103661ea597'      # Replace with actual owner address
PRIVATE_KEY = '0x0e6e48e06fb892d8e0a24de1a9a7605baf858d6a59c55b18c4c0fd3c061707b3'         # Replace with actual private key

# Load contract ABI from file
try:
    with open('applications_abi.json', 'r') as abi_file:
        CONTRACT_ABI = json.load(abi_file)
except FileNotFoundError:
    logger.error("applications_abi.json not found")
    raise
except json.JSONDecodeError:
    logger.error("Invalid JSON in applications_abi.json")
    raise

# Initialize contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def send_transaction(function_call, from_address, private_key):
    """Helper function to build, sign, and send a transaction."""
    try:
        # Build transaction
        tx = function_call.build_transaction({
            'from': from_address,
            'nonce': w3.eth.get_transaction_count(from_address),
            'gas': 2000000,  # Adjust gas limit as needed
            'gasPrice': w3.to_wei('20', 'gwei'),  # Adjust gas price as needed
            'chainId': w3.eth.chain_id
        })

        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)

        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info(f"Transaction sent: {tx_hash.hex()}")

        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt['status'] == 1:
            logger.info("Transaction successful")
            return receipt
        else:
            logger.error("Transaction failed")
            raise Exception("Transaction failed")
    except Exception as e:
        logger.error(f"Error sending transaction: {str(e)}")
        raise

def create_application(username, email, resume_text, job_id, extracted_data):
    """Create a new application."""
    try:
        applied_at = datetime.utcnow().isoformat()  # Current timestamp in ISO format
        function_call = contract.functions.createApplication(
            username, email, resume_text, job_id, applied_at, extracted_data
        )
        receipt = send_transaction(function_call, OWNER_ADDRESS, PRIVATE_KEY)
        # Extract application ID from event logs
        logs = contract.events.ApplicationCreated().process_receipt(receipt)
        if logs:
            app_id = logs[0]['args']['id']
            logger.info(f"Application created with ID: {app_id}")
            return app_id
        else:
            raise Exception("No ApplicationCreated event found")
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise

def get_applications_by_job_id(job_id):
    """List all applications for a given job_id."""
    try:
        result = contract.functions.getApplicationsByJobId(job_id).call()
        (
            ids, usernames, emails, resume_texts, job_ids, applied_ats,
            extracted_datas, match_scores, selecteds, invitation_sents
        ) = result

        applications = []
        for i in range(len(ids)):
            app = {
                'id': ids[i],
                'username': usernames[i],
                'email': emails[i],
                'resume_text': resume_texts[i],
                'job_id': job_ids[i],
                'applied_at': applied_ats[i],
                'extracted_data': extracted_datas[i],
                'match_score': match_scores[i],
                'selected': selecteds[i],
                'invitation_sent': invitation_sents[i]
            }
            applications.append(app)

        logger.info(f"Retrieved {len(applications)} applications for job_id {job_id}")
        return applications
    except Exception as e:
        logger.error(f"Error retrieving applications for job_id {job_id}: {str(e)}")
        raise

def set_application_selected(app_id):
    """Set selected = true for an application."""
    try:
        function_call = contract.functions.setApplicationSelected(app_id)
        receipt = send_transaction(function_call, OWNER_ADDRESS, PRIVATE_KEY)
        logger.info(f"Application {app_id} marked as selected")
        return receipt
    except Exception as e:
        logger.error(f"Error setting application {app_id} as selected: {str(e)}")
        raise

def set_application_invitation_sent(app_id):
    """Set invitation_sent = true for an application."""
    try:
        function_call = contract.functions.setApplicationInvitationSent(app_id)
        receipt = send_transaction(function_call, OWNER_ADDRESS, PRIVATE_KEY)
        logger.info(f"Application {app_id} marked as invitation sent")
        return receipt
    except Exception as e:
        logger.error(f"Error setting application {app_id} invitation sent: {str(e)}")
        raise

def get_application(app_id):
    """Get details of a specific application by ID."""
    try:
        result = contract.functions.getApplication(app_id).call()
        app = {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'resume_text': result[3],
            'job_id': result[4],
            'applied_at': result[5],
            'extracted_data': result[6],
            'match_score': result[7],
            'selected': result[8],
            'invitation_sent': result[9]
        }
        logger.info(f"Retrieved application {app_id}")
        return app
    except Exception as e:
        logger.error(f"Error retrieving application {app_id}: {str(e)}")
        raise

def get_next_id():
    """Get the next available application ID."""
    try:
        next_id = contract.functions.getNextId().call()
        logger.info(f"Next available ID: {next_id}")
        return next_id
    except Exception as e:
        logger.error(f"Error retrieving next ID: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Example usage
        # Create a new application
        app_id = create_application(
            username="alice",
            email="alice@example.com",
            resume_text="Alice's resume...",
            job_id=1,
            extracted_data="{}"
        )

        # List applications for job_id=1
        apps = get_applications_by_job_id(1)
        for app in apps:
            print(json.dumps(app, indent=2))

        # Mark application as selected
        set_application_selected(app_id)

        # Mark application as invitation sent
        set_application_invitation_sent(app_id)

        # Get application details
        app = get_application(app_id)
        print(json.dumps(app, indent=2))

        # Get next available ID
        next_id = get_next_id()
        print(f"Next ID: {next_id}")

    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")