-- Drop existing slot if needed (be careful, this will lose unconsumed changes)
-- SELECT pg_drop_replication_slot('cdc_slot');

-- Create a new replication slot with wal2json plugin
SELECT * FROM pg_create_logical_replication_slot('anti_debezium_slot', 'wal2json');

-- Check existing replication slots
SELECT * FROM pg_replication_slots;
