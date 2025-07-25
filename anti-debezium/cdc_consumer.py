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
    password="Activi2025",
    host="cdc-device-db.c6nuwaa6scec.us-east-1.rds.amazonaws.com",
    port=5432,
    connection_factory=psycopg2.extras.LogicalReplicationConnection
)

# Start a logical replication cursor
cur = conn.cursor()

# Check if the replication slot exists
cur.execute("SELECT slot_name, plugin FROM pg_replication_slots WHERE slot_name = 'device_slot'")
slot = cur.fetchone()
if slot:
    print(f"Found replication slot: {slot[0]} with plugin: {slot[1]}")
else:
    print("Replication slot 'device_slot' not found!")
    print("Creating replication slot...")
    try:
        # Create replication slot with wal2json plugin
        cur.execute("SELECT * FROM pg_create_logical_replication_slot('device_slot', 'wal2json')")
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
        
        # Skip transaction control messages (BEGIN/COMMIT)
        if isinstance(data, dict) and data.get('action') in ('B', 'C'):
            print(f"Skipping transaction control message: {data.get('action')}")
            msg.cursor.send_feedback(flush_lsn=msg.data_start)
            return

        # Process only actual data changes
        print(f"Received WAL message: {json.dumps(data, indent=2)}")

        # Support both wal2json formats: with 'change' key (list) or flat dict
        changes = data.get('change') if isinstance(data, dict) and 'change' in data else [data]
        for change in changes:
            # Skip if it's a transaction control message in the change array
            if isinstance(change, dict) and change.get('action') in ('B', 'C'):
                continue
                
            print(f"Processing change: {json.dumps(change, indent=2)}")
            
            # For UPDATE operations, we need to infer changed columns by comparing identity with columns
            # In wal2json with REPLICA IDENTITY FULL, the identity section contains the old values
            changed_columns = []
            if change.get('action', '') == 'U':
                # Create dictionaries for old and new values
                identity_dict = {}
                columns_dict = {}
                
                # Extract old values from identity section
                for item in change.get('identity', []):
                    identity_dict[item['name']] = item['value']
                
                # Extract new values from columns section
                for item in change.get('columns', []):
                    columns_dict[item['name']] = item['value']
                
                # Compare old and new values to identify changes
                for col_name, new_val in columns_dict.items():
                    if col_name in identity_dict:
                        old_val = identity_dict[col_name]
                        # Convert values to strings for comparison to handle different types
                        str_old_val = str(old_val) if old_val is not None else 'None'
                        str_new_val = str(new_val) if new_val is not None else 'None'
                        
                        if str_old_val != str_new_val:
                            changed_columns.append({
                                'name': col_name,
                                'old_value': old_val,
                                'new_value': new_val
                            })
                
                # Add the changed columns to the change object
                change['changed_columns'] = changed_columns
                if changed_columns:
                    print(f"Detected {len(changed_columns)} changed columns: {', '.join([col['name'] for col in changed_columns])}")
                else:
                    print("No columns were changed in this update")
            
            try:
                producer.send(
                    content=json.dumps(change).encode('utf-8'),
                    properties={
                        'table': change.get('table', ''),
                        'operation': change.get('kind', change.get('action', '')),
                        'timestamp': str(time.time()),
                        'changed_columns': ','.join([col['name'] for col in changed_columns]) if changed_columns else ''
                    },
                    partition_key=change.get('table', 'default')
                )
                print(f"Sent to Pulsar: {change.get('table', 'unknown')} - {change.get('action', 'unknown')}")
                if changed_columns and change.get('action', '') == 'U':
                    print(f"Changed columns: {', '.join([col['name'] for col in changed_columns])}")
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
        slot_name='device_slot',
        options={
            'pretty-print': 1, 
            'include-lsn': 1, 
            'format-version': 2,
            'write-in-chunks': 0,
            'include-timestamp': 1
        },
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
