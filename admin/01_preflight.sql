-- =====================================================================
-- STEP 1 of 5 - PRE-FLIGHT CHECKS (read-only, changes nothing)
-- Tricon "Data Engineering with CoCo" lab
-- Run each statement in a Snowsight SQL worksheet as ACCOUNTADMIN and compare with "EXPECT".
-- =====================================================================
USE ROLE ACCOUNTADMIN;

-- 1a. Where am I? Record these values for the attendee instructions.
SELECT CURRENT_ACCOUNT() AS account_locator, CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME() AS account_identifier,
       CURRENT_REGION() AS region, CURRENT_USER() AS me;
-- EXPECT: account_identifier is what attendees enter in CoCo Desktop and ~/.dbt/profiles.yml.

-- 1b. NAME COLLISIONS - the lab only creates objects whose names start with TRICON_DE.
-- (Exact-name checks; '\\_' escapes the underscore so e.g. an existing TRICON_DEMO is not a false alarm.)
SHOW ROLES             LIKE 'TRICON\\_DE\\_%';    -- TRICON_DE_ROLE, TRICON_DE_REVIEWER
SHOW WAREHOUSES        LIKE 'TRICON\\_DE\\_%';    -- TRICON_DE_WH, TRICON_DE_ADAPTIVE_DEMO_WH
SHOW DATABASES         LIKE 'TRICON\\_DE';        -- TRICON_DE
SHOW RESOURCE MONITORS LIKE 'TRICON\\_DE\\_%';    -- TRICON_DE_MONITOR
SHOW INTEGRATIONS      LIKE 'TRICON\\_DE\\_%';    -- TRICON_DE_EMAIL_INT
-- EXPECT: all five return 0 rows. If ANY row comes back, STOP and contact the lab facilitator.
--         (Setup uses IF NOT EXISTS and would otherwise grant to a pre-existing object.)

-- 1c. Sample data used by the dbt project.
SHOW DATABASES LIKE 'SNOWFLAKE_SAMPLE_DATA';
-- EXPECT: 1 row  -> skip step 2a in 02_setup.sql.
--         0 rows -> keep step 2a (it mounts Snowflake's free, read-only sample-data share).

-- 1d. CoCo Desktop prerequisites (https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop)
SHOW PARAMETERS LIKE 'CORTEX_ENABLED_CROSS_REGION' IN ACCOUNT;
-- EXPECT: a value other than DISABLED (e.g. ANY_REGION, AWS_US). CoCo Desktop requires cross-region inference.
--         If DISABLED: decide with your security team. This lab does NOT change account parameters.

SHOW PARAMETERS LIKE 'CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER' IN ACCOUNT;
-- EXPECT: -1 (no limit) or a positive number. If 0, Desktop is blocked account-wide; set a positive value per attendee (see ADMIN_GUIDE.md).

SHOW GRANTS OF DATABASE ROLE SNOWFLAKE.CORTEX_USER;
-- INFO: if PUBLIC is listed, everyone already has Cortex access. Setup also grants it to the lab role either way.

-- 1e. Edition (Enterprise+ needed for SYSTEM$CLASSIFY in module A2, multi-cluster warehouses, Adaptive Warehouses).
--     Check in Snowsight: Admin > Accounts (or ask your Snowflake account team).
--     Standard edition: in 02_setup.sql use the single-cluster warehouse line and skip module A2.
