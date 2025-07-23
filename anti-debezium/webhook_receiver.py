from flask import Flask, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    app.logger.info(f"Received webhook POST: {data}")
    print(f"Received webhook POST: {data}")
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
