import psycopg2
import psycopg2.extras
import json
import time
import os

# Pulsar integration
import pulsar

# PostgreSQL Connection Settings
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres123",
    host="database-1.c5d2abh4bx8o.ap-south-1.rds.amazonaws.com",
    port=5432,
    connection_factory=psycopg2.extras.LogicalReplicationConnection
)

# Start a logical replication cursor
cur = conn.cursor()

# Check if the replication slot exists
cur.execute("SELECT slot_name, plugin FROM pg_replication_slots WHERE slot_name = 'anti_debezium_slot'")
slot = cur.fetchone()
if slot:
    print(f"Found replication slot: {slot[0]} with plugin: {slot[1]}")
else:
    print("Replication slot 'anti_debezium_slot' not found!")
    print("Creating replication slot...")
    try:
        cur.execute("SELECT * FROM pg_create_logical_replication_slot('anti_debezium_slot', 'wal2json')")
        print("Replication slot created successfully.")
    except Exception as e:
        print(f"Error creating replication slot: {e}")

# Create a new cursor for replication
cur.close()
cur = conn.cursor()

# Pulsar client setup
pulsar_client = pulsar.Client('pulsar://localhost:6650')

# Create a producer for CDC events
# Using a topic name that reflects the CDC nature of the data
producer = pulsar_client.create_producer(
    'persistent://public/default/postgres-cdc-events',
    # Add some producer configurations for reliability
    block_if_queue_full=True,
    batching_enabled=True,
    batching_max_publish_delay_ms=10
)

def consume_wal(msg):
    """Process WAL messages and send to Pulsar"""
    try:
        # Parse the WAL message
        data = json.loads(msg.payload)
        print(f"Received WAL message: {json.dumps(data, indent=2)}")

        # Support both wal2json formats: with 'change' key (list) or flat dict
        changes = data.get('change') if isinstance(data, dict) and 'change' in data else [data]
        for change in changes:
            print(f"Processing change: {json.dumps(change, indent=2)}")
            try:
                producer.send(
                    content=json.dumps(change).encode('utf-8'),
                    properties={
                        'table': change.get('table', ''),
                        'operation': change.get('kind', change.get('action', '')),
                        'timestamp': str(time.time())
                    },
                    partition_key=change.get('table', 'default')
                )
                print(f"Sent to Pulsar: {change.get('table', 'unknown')} - {change.get('kind', change.get('action', 'unknown'))}")
            except Exception as send_err:
                print(f"Error sending to Pulsar: {send_err}")

        # Acknowledge receipt to advance the replication slot
        msg.cursor.send_feedback(flush_lsn=msg.data_start)

    except Exception as e:
        print(f"Error processing message: {e}")

try:
    print("Starting CDC streaming...")
    
    # Start replication with wal2json options
    cur.start_replication(
        slot_name='anti_debezium_slot',
        options={'pretty-print': 1, 'include-lsn': 1, 'format-version': 2},
        decode=True
    )
    
    # Process replication messages
    while True:
        msg = cur.read_message()
        if msg:
            consume_wal(msg)
        else:
            print("No new changes. Waiting...")
            time.sleep(5)
            
except KeyboardInterrupt:
    print("Exiting CDC consumer.")
except Exception as e:
    print(f"Error in CDC streaming: {e}")
finally:
    print("Closing connections...")
    cur.close()
    conn.close()
    # Close Pulsar client
    pulsar_client.close()
