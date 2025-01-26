from flask import Flask, render_template, request, jsonify
from blockchain import Blockchain
import logging
import os

# Initialize the Flask app and blockchain
app = Flask(__name__)
blockchain = Blockchain()

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    """
    Render the main page for the Transparent Voting System.
    """
    return render_template('index.html')

@app.route('/add_vote', methods=['POST'])
def add_vote():
    """
    Add a vote to the blockchain.
    """
    voter_id = request.form.get('voter_id')
    candidate = request.form.get('candidate')

    # Basic input validation
    if not voter_id or not candidate:
        return jsonify({"success": False, "message": "Voter ID and Candidate are required."}), 400

    if len(voter_id.strip()) == 0 or len(candidate.strip()) == 0:
        return jsonify({"success": False, "message": "Voter ID and Candidate cannot be empty."}), 400

    try:
        vote_data = f"Vote: {voter_id} -> {candidate}"
        blockchain.add_block(vote_data)
        logging.info(f"Vote added: {vote_data}")
        return jsonify({"success": True, "message": "Vote added successfully!"})
    except Exception as e:
        logging.error(f"Error adding vote: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

@app.route('/view_chain', methods=['GET'])
def view_chain():
    """
    View the entire blockchain.
    """
    try:
        chain_data = [
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "data": block.data,
                "hash": block.hash,
                "previous_hash": block.previous_hash,
            }
            for block in blockchain.chain
        ]
        logging.info("Blockchain retrieved successfully.")
        return jsonify({"chain": chain_data})
    except Exception as e:
        logging.error(f"Error retrieving blockchain: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

@app.route('/validate', methods=['GET'])
def validate():
    """
    Validate the integrity of the blockchain.
    """
    try:
        is_valid = blockchain.is_chain_valid()
        message = "Blockchain is valid." if is_valid else "Blockchain has been tampered with!"
        logging.info("Blockchain validation result: " + message)
        return jsonify({"success": is_valid, "message": message})
    except Exception as e:
        logging.error(f"Error validating blockchain: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Use environment variables for port and debug mode
    PORT = int(os.getenv('PORT', 5001))
    DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']

    app.run(debug=DEBUG, port=PORT)
from flask import Flask, render_template, request, jsonify
from blockchain import Blockchain
from voter import VoterRegistry
import logging
import os

# Initialize Flask app, blockchain, and voter registry
app = Flask(__name__)
blockchain = Blockchain()
voter_registry = VoterRegistry()

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    """Render the main page for the Transparent Voting System."""
    return render_template('index.html')

@app.route('/register_voter', methods=['POST'])
def register_voter():
    """Register a new voter."""
    voter_id = request.form.get('voter_id')
    name = request.form.get('name')
    age = int(request.form.get('age', 0))

    if not voter_id or not name or age <= 0:
        return jsonify({"success": False, "message": "Invalid voter details."}), 400

    result = voter_registry.register_voter(voter_id, name, age)
    return jsonify(result)

@app.route('/add_vote', methods=['POST'])
def add_vote():
    """Add a vote to the blockchain."""
    voter_id = request.form.get('voter_id')
    candidate = request.form.get('candidate')

    if not voter_id or not candidate:
        return jsonify({"success": False, "message": "Voter ID and Candidate are required."}), 400

    auth_result = voter_registry.authenticate_voter(voter_id)
    if not auth_result['success']:
        return jsonify(auth_result), 403

    try:
        # Creating the vote data string
        vote_data = f"Vote: {voter_id} -> {candidate}"

        # Adding the vote data to the blockchain as a new block
        blockchain.add_block(vote_data)

        # Mark the voter as having voted
        voter_registry.mark_voted(voter_id)

        # Log the success and return the response
        logging.info(f"Vote added: {vote_data}")
        return jsonify({"success": True, "message": "Vote added successfully!"})
    except Exception as e:
        # Log any error that occurs
        logging.error(f"Error adding vote: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

@app.route('/view_chain', methods=['GET'])
def view_chain():
    """View the entire blockchain."""
    try:
        chain_data = [
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "data": block.data,
                "hash": block.hash,
                "previous_hash": block.previous_hash,
            }
            for block in blockchain.chain
        ]
        logging.info("Blockchain retrieved successfully.")
        return jsonify({"chain": chain_data})
    except Exception as e:
        logging.error(f"Error retrieving blockchain: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

@app.route('/validate', methods=['GET'])
def validate():
    """Validate the integrity of the blockchain."""
    try:
        is_valid = blockchain.is_chain_valid()
        message = "Blockchain is valid." if is_valid else "Blockchain has been tampered with!"
        logging.info("Blockchain validation result: " + message)
        return jsonify({"success": is_valid, "message": message})
    except Exception as e:
        logging.error(f"Error validating blockchain: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Use environment variables for port and debug mode
    PORT = int(os.getenv('PORT', 5001))
    DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']

    # Load blockchain and voter registry if files exist
    blockchain.load_from_file()
    voter_registry.load_registry()

    # Run the Flask app
    app.run(debug=DEBUG, port=PORT)
