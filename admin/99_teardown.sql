-- =====================================================================
-- TEARDOWN - remove everything the lab created. Run after hackathon week.
-- Snowsight worksheet as ACCOUNTADMIN, "Run All".
-- Drops ONLY objects with the exact lab names, and ONLY temporary lab users whose comment
-- starts with "TEMPORARY - Tricon CoCo DE lab". Existing (real) users are never dropped -
-- they simply lose the lab role when it is dropped.
-- =====================================================================
USE ROLE ACCOUNTADMIN;

-- 1. Temporary lab logins created with "NEW" (TRICON_DE_<INITIALS>)
DECLARE
  rs RESULTSET;
  dropped STRING DEFAULT '';
BEGIN
  rs := (SHOW USERS LIKE 'TRICON\\_DE\\_%');
  FOR u IN rs DO
    IF (COALESCE(u."comment", '') ILIKE 'TEMPORARY - Tricon CoCo DE lab%') THEN
      EXECUTE IMMEDIATE 'DROP USER IF EXISTS "' || REPLACE(u."name", '"', '""') || '"';
      dropped := dropped || u."name" || ' ';
    END IF;
  END FOR;
  RETURN 'Temporary lab users dropped: ' || IFF(dropped = '', '(none)', dropped);
END;

-- 2. Lab objects (exact names only; similarly named objects such as TRICON_DEMO are never touched)
DROP DATABASE         IF EXISTS TRICON_DE;     -- all personal DBT_<INITIALS> schemas, tables, semantic views, policies
DROP WAREHOUSE        IF EXISTS TRICON_DE_WH;
DROP WAREHOUSE        IF EXISTS TRICON_DE_ADAPTIVE_DEMO_WH;
DROP RESOURCE MONITOR IF EXISTS TRICON_DE_MONITOR;
DROP INTEGRATION      IF EXISTS TRICON_DE_EMAIL_INT;
DROP ROLE             IF EXISTS TRICON_DE_REVIEWER;   -- also removes it from any users
DROP ROLE             IF EXISTS TRICON_DE_ROLE;       -- also removes it from every attendee

-- 3. Confirm - every line below should return 0 rows
SHOW DATABASES         LIKE 'TRICON\\_DE';
SHOW WAREHOUSES        LIKE 'TRICON\\_DE\\_%';
SHOW ROLES             LIKE 'TRICON\\_DE\\_%';
SHOW RESOURCE MONITORS LIKE 'TRICON\\_DE\\_%';
SHOW USERS             LIKE 'TRICON\\_DE\\_%';

-- SNOWFLAKE_SAMPLE_DATA is kept (Snowflake's standard sample share). Only if it was created for this lab:
-- DROP DATABASE IF EXISTS SNOWFLAKE_SAMPLE_DATA;
