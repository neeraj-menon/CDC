from flask import Flask, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/api/webhook/trigger', methods=['POST'])
def webhook():
    workflow_id = request.args.get('workflow_id')
    data = request.get_json(force=True)
    app.logger.info(f"Received webhook POST for workflow_id={workflow_id}: {data}")
    print(f"Received webhook POST for workflow_id={workflow_id}: {data}")
    return jsonify({'status': 'received', 'workflow_id': workflow_id}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
