-- =====================================================================
-- Tricon "Data Engineering with CoCo" lab - admin pre-provisioning
-- Run once before the lab as ACCOUNTADMIN (review with Tricon's Snowflake admin).
-- Attendees write only to their own TRICON_DE.DBT_<INITIALS> schema.
-- =====================================================================
USE ROLE ACCOUNTADMIN;

-- 1. Sample data (TPC-H) used by the dbt project ------------------------
-- Skip if SNOWFLAKE_SAMPLE_DATA already exists (SHOW DATABASES LIKE 'SNOWFLAKE_SAMPLE_DATA').
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_SAMPLE_DATA FROM SHARE SFC_SAMPLES.SAMPLE_DATA;

-- 2. Attendee role, database, warehouse --------------------------------
CREATE ROLE IF NOT EXISTS TRICON_DE_ROLE COMMENT = 'Data Engineering with CoCo lab attendees';
GRANT ROLE TRICON_DE_ROLE TO ROLE SYSADMIN;

CREATE DATABASE IF NOT EXISTS TRICON_DE COMMENT = 'CoCo DE lab sandbox - TPC-H and synthetic data only';
GRANT USAGE, CREATE SCHEMA ON DATABASE TRICON_DE TO ROLE TRICON_DE_ROLE;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE_SAMPLE_DATA TO ROLE TRICON_DE_ROLE;

-- Multi-cluster needs Enterprise edition; drop MIN/MAX_CLUSTER_COUNT on Standard.
CREATE WAREHOUSE IF NOT EXISTS TRICON_DE_WH
  WAREHOUSE_SIZE = 'SMALL' MIN_CLUSTER_COUNT = 1 MAX_CLUSTER_COUNT = 3 SCALING_POLICY = 'STANDARD'
  AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE;
GRANT USAGE, OPERATE ON WAREHOUSE TRICON_DE_WH TO ROLE TRICON_DE_ROLE;

CREATE RESOURCE MONITOR IF NOT EXISTS TRICON_DE_MONITOR
  WITH CREDIT_QUOTA = 40 FREQUENCY = WEEKLY START_TIMESTAMP = IMMEDIATELY
  TRIGGERS ON 80 PERCENT DO NOTIFY ON 100 PERCENT DO SUSPEND;
ALTER WAREHOUSE TRICON_DE_WH SET RESOURCE_MONITOR = TRICON_DE_MONITOR;

-- Cortex Analyst (A4/A5) and CoCo.
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE TRICON_DE_ROLE;

-- Optional: publish the plugin to the Plugins Catalog (Module 4, Option A) creates a
-- CORTEX EXTENSION in each user's personal USER$ database; confirm Tricon allows this.

-- 3. Optional reviewer role for A3 (access review) and A6 (warehouses) --
-- Read-only, but SENSITIVE: exposes account-wide users, grants, login and query history.
-- Grant only to Snowflake admins / security owners, not to all attendees.
CREATE ROLE IF NOT EXISTS TRICON_DE_REVIEWER COMMENT = 'Read-only account metadata for access and warehouse reviews';
GRANT ROLE TRICON_DE_REVIEWER TO ROLE SECURITYADMIN;
GRANT DATABASE ROLE SNOWFLAKE.SECURITY_VIEWER   TO ROLE TRICON_DE_REVIEWER;  -- USERS, ROLES, GRANTS_*, LOGIN_HISTORY
GRANT DATABASE ROLE SNOWFLAKE.USAGE_VIEWER      TO ROLE TRICON_DE_REVIEWER;  -- WAREHOUSE_METERING/LOAD_HISTORY
GRANT DATABASE ROLE SNOWFLAKE.GOVERNANCE_VIEWER TO ROLE TRICON_DE_REVIEWER;  -- QUERY_HISTORY, QUERY_METERING_HISTORY
GRANT DATABASE ROLE SNOWFLAKE.OBJECT_VIEWER     TO ROLE TRICON_DE_REVIEWER;
GRANT USAGE ON WAREHOUSE TRICON_DE_WH TO ROLE TRICON_DE_REVIEWER;
GRANT MONITOR USAGE ON ACCOUNT TO ROLE TRICON_DE_REVIEWER;                     -- SHOW WAREHOUSES across the account
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE TRICON_DE_REVIEWER;
-- GRANT ROLE TRICON_DE_REVIEWER TO USER <ADMIN_USERNAME>;

-- 4. Optional email delivery for A4 (KPI report) -----------------------
-- Snowflake email integrations can only send to verified email addresses of users in this account.
-- CREATE NOTIFICATION INTEGRATION IF NOT EXISTS TRICON_DE_EMAIL_INT
--   TYPE = EMAIL ENABLED = TRUE ALLOWED_RECIPIENTS = ('<approved.person@triconresidential.com>');
-- GRANT USAGE ON INTEGRATION TRICON_DE_EMAIL_INT TO ROLE TRICON_DE_ROLE;

-- 5. Optional facilitator demo warehouse for A6 (Adaptive Warehouses) ---
-- Requires Enterprise edition and a supported region. Facilitator converts it live, then rolls back.
-- CREATE WAREHOUSE IF NOT EXISTS TRICON_DE_ADAPTIVE_DEMO_WH
--   WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE
--   RESOURCE_MONITOR = TRICON_DE_MONITOR;

-- 6. Attendees ---------------------------------------------------------
-- GRANT ROLE TRICON_DE_ROLE TO USER <USERNAME>;   -- repeat per attendee

-- Pre-flight as an attendee:
-- USE ROLE TRICON_DE_ROLE; USE WAREHOUSE TRICON_DE_WH;
-- SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS;          -- expect 1,500,000
-- CREATE SCHEMA TRICON_DE.DBT_TEST; DROP SCHEMA TRICON_DE.DBT_TEST;
