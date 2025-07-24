-- Set REPLICA IDENTITY FULL on tables to ensure full row data is included in WAL
-- This is important for CDC to properly detect which columns have changed

-- For the device_events table (adjust for your specific tables)
ALTER TABLE public.device_events REPLICA IDENTITY FULL;

-- For other tables you want to track changes on
-- ALTER TABLE public.your_table_name REPLICA IDENTITY FULL;

-- To check the current REPLICA IDENTITY setting for tables
SELECT relname AS table_name, 
       CASE relreplident
         WHEN 'd' THEN 'DEFAULT'
         WHEN 'n' THEN 'NOTHING'
         WHEN 'f' THEN 'FULL'
         WHEN 'i' THEN 'INDEX'
       END AS replica_identity
FROM pg_class
WHERE relkind = 'r' -- Only regular tables
  AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
ORDER BY relname;
