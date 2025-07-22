import pulsar

# Pulsar service URL (standalone Docker default)
PULSAR_SERVICE_URL = 'pulsar://localhost:6650'
# CDC topic - this is the actual topic where Debezium publishes the CDC events
CDC_TOPIC = 'persistent://public/default/rds-pg.public.users'

# Create Pulsar client
client = pulsar.Client(PULSAR_SERVICE_URL)

# Subscribe to the CDC topic
consumer = client.subscribe(CDC_TOPIC, subscription_name='cdc-python-consumer-new', initial_position=pulsar.InitialPosition.Latest)

print('Listening for CDC events on topic:', CDC_TOPIC)

try:
    while True:
        msg = consumer.receive(timeout_millis=100000)
        print('\n--- CDC Event ---')
        print('Message ID:', msg.message_id())
        print('Key:', msg.partition_key())
        print('Value:', msg.data().decode('utf-8'))
        consumer.acknowledge(msg)
except Exception as e:
    print('Stopped or error:', e)
finally:
    consumer.close()
    client.close()
