from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/welcome', methods=['GET'])
def welcome():
    """
    Returns a welcome message and logs the request metadata.
    """
    logger.info(f"Request received: {request.method} {request.path}")
    return jsonify({'message': 'Welcome to the LLM Text Miner API!'})

if __name__ == '__main__':
    app.run(debug=True)
