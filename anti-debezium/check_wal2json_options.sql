-- Check the version and options supported by wal2json plugin
-- Run this on your PostgreSQL database to see what options are available

-- Check the installed logical decoding plugins
SELECT * FROM pg_available_extensions WHERE name LIKE '%wal%';

-- Check the version of wal2json (if available)
SELECT extversion FROM pg_extension WHERE extname = 'wal2json';

-- Check the replication slots
SELECT slot_name, plugin, slot_type, database, active, restart_lsn, confirmed_flush_lsn
FROM pg_replication_slots
WHERE plugin = 'wal2json';

-- Create a test slot to check available options (will be dropped immediately)
DO $$
BEGIN
    -- Try to create a test slot
    BEGIN
        PERFORM pg_create_logical_replication_slot('test_wal2json_options', 'wal2json');
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Could not create test slot: %', SQLERRM;
        RETURN;
    END;

    -- Output available options
    RAISE NOTICE 'Successfully created test slot. Check documentation for available options.';
    
    -- Drop the test slot
    PERFORM pg_drop_replication_slot('test_wal2json_options');
    RAISE NOTICE 'Test slot dropped.';
END;
$$;

-- Note: For RDS PostgreSQL, you may need to check AWS documentation for 
-- supported wal2json options as they might differ from standard PostgreSQL.
