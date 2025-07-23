import os
import requests
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webhook_trigger")

WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:5001/webhook')  # Default or configurable

def trigger_webhook(payload, url=None, timeout=5):
    """
    Send a POST request to the configured webhook URL with the given payload.
    Args:
        payload (dict): The data to send in the POST request.
        url (str, optional): Override the default webhook URL.
        timeout (int, optional): Request timeout in seconds.
    Returns:
        bool: True if webhook was triggered successfully, False otherwise.
    """
    target_url = url or WEBHOOK_URL
    try:
        response = requests.post(target_url, json=payload, timeout=timeout)
        response.raise_for_status()
        logger.info(f"Webhook triggered successfully: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Webhook trigger failed: {e}")
        return False

if __name__ == "__main__":
    # Example usage for manual testing
    import sys
    import json
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
    else:
        data = {"test": "webhook"}
    trigger_webhook(data)
