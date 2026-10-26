-- =====================================================================
-- TEARDOWN - remove everything the lab created. Run after hackathon week.
-- Drops ONLY objects named TRICON_DE*. Safe to run even if some optional objects were never created.
-- =====================================================================
USE ROLE ACCOUNTADMIN;

-- Review first: what will be removed
SHOW DATABASES         LIKE 'TRICON\\_DE';
SHOW WAREHOUSES        LIKE 'TRICON\\_DE\\_%';
SHOW ROLES             LIKE 'TRICON\\_DE\\_%';
SHOW RESOURCE MONITORS LIKE 'TRICON\\_DE\\_%';
SHOW INTEGRATIONS      LIKE 'TRICON\\_DE\\_%';
-- Only the exact names below are dropped; similarly named objects (e.g. TRICON_DEMO) are never touched.

DROP DATABASE         IF EXISTS TRICON_DE;     -- all attendee DBT_<INITIALS> schemas, tables, semantic views, policies
DROP WAREHOUSE        IF EXISTS TRICON_DE_WH;
DROP WAREHOUSE        IF EXISTS TRICON_DE_ADAPTIVE_DEMO_WH;
DROP RESOURCE MONITOR IF EXISTS TRICON_DE_MONITOR;
DROP INTEGRATION      IF EXISTS TRICON_DE_EMAIL_INT;
DROP ROLE             IF EXISTS TRICON_DE_REVIEWER;   -- also removes it from any users
DROP ROLE             IF EXISTS TRICON_DE_ROLE;       -- also removes it from all attendees

-- SNOWFLAKE_SAMPLE_DATA: keep it (it is Snowflake's standard sample share). Only if it was created for this lab:
-- DROP DATABASE IF EXISTS SNOWFLAKE_SAMPLE_DATA;

-- If you set per-user CoCo Desktop credit limits in 04_attendees.sql, unset them:
-- ALTER USER "<USERNAME_1>" UNSET CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER;
