import pulsar
import json
import time
from webhook_trigger import trigger_webhook

PULSAR_SERVICE_URL = 'pulsar://localhost:6650'
TOPIC = 'persistent://public/default/postgres-cdc-events'  # Change to 'device-events' if needed
SUBSCRIPTION = 'webhook-sim-sub'


def main():
    client = pulsar.Client(PULSAR_SERVICE_URL)
    consumer = client.subscribe(TOPIC, subscription_name=SUBSCRIPTION, consumer_type=pulsar.ConsumerType.Shared)
    print(f"Subscribed to {TOPIC} as {SUBSCRIPTION}")
    try:
        while True:
            # msg = consumer.receive(timeout_millis=100000)
            msg = consumer.receive()

            try:
                payload = msg.data().decode('utf-8')
                print(f"Received message from Pulsar: {payload}")
                data = json.loads(payload)
                # Simulate Pulsar Function: trigger webhook per message
                webhook_success = trigger_webhook(data)
                if webhook_success:
                    print("Webhook triggered successfully.")
                else:
                    print("Webhook trigger failed.")
                consumer.acknowledge(msg)
            except Exception as e:
                print(f"Error processing message: {e}")
                consumer.negative_acknowledge(msg)
    except KeyboardInterrupt:
        print("Exiting simulation.")
    finally:
        consumer.close()
        client.close()

if __name__ == "__main__":
    main()
