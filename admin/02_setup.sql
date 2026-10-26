-- =====================================================================
-- STEP 2 of 5 - CREATE THE LAB ENVIRONMENT
-- Creates ONLY new objects named TRICON_DE*. Does not alter existing users, roles,
-- warehouses, databases, network policies, or account parameters.
-- Safe to re-run. Remove everything with 99_teardown.sql.
-- =====================================================================

-- 2a. Sample data (skip if 01_preflight step 1c returned a row) -------
USE ROLE ACCOUNTADMIN;
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_SAMPLE_DATA FROM SHARE SFC_SAMPLES.SAMPLE_DATA;

-- 2b. Lab role (created by USERADMIN, the standard role-management role)
USE ROLE USERADMIN;
CREATE ROLE IF NOT EXISTS TRICON_DE_ROLE
  COMMENT = 'TEMPORARY - Tricon CoCo DE lab attendees. Remove with admin/99_teardown.sql';
GRANT ROLE TRICON_DE_ROLE TO ROLE SYSADMIN;          -- standard practice: custom roles roll up to SYSADMIN

-- 2c. Lab database + warehouse (owned by SYSADMIN, not by the lab role)
USE ROLE SYSADMIN;
CREATE DATABASE IF NOT EXISTS TRICON_DE
  DATA_RETENTION_TIME_IN_DAYS = 1
  COMMENT = 'TEMPORARY - Tricon CoCo DE lab sandbox. TPC-H sample + synthetic data only. Remove with admin/99_teardown.sql';
GRANT USAGE, CREATE SCHEMA ON DATABASE TRICON_DE TO ROLE TRICON_DE_ROLE;   -- attendees create and own DBT_<INITIALS>

-- Enterprise edition (multi-cluster for ~20 concurrent attendees):
CREATE WAREHOUSE IF NOT EXISTS TRICON_DE_WH
  WAREHOUSE_SIZE = 'SMALL' MIN_CLUSTER_COUNT = 1 MAX_CLUSTER_COUNT = 3 SCALING_POLICY = 'STANDARD'
  AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE
  COMMENT = 'TEMPORARY - Tricon CoCo DE lab compute. Remove with admin/99_teardown.sql';
-- Standard edition: use this instead of the statement above.
-- CREATE WAREHOUSE IF NOT EXISTS TRICON_DE_WH WAREHOUSE_SIZE = 'SMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE
--   INITIALLY_SUSPENDED = TRUE COMMENT = 'TEMPORARY - Tricon CoCo DE lab compute. Remove with admin/99_teardown.sql';
GRANT USAGE, OPERATE ON WAREHOUSE TRICON_DE_WH TO ROLE TRICON_DE_ROLE;      -- use only; cannot resize

-- 2d. Cost guardrail: hard stop at 40 credits per week on the lab warehouse only
USE ROLE ACCOUNTADMIN;
CREATE RESOURCE MONITOR IF NOT EXISTS TRICON_DE_MONITOR
  WITH CREDIT_QUOTA = 40 FREQUENCY = WEEKLY START_TIMESTAMP = IMMEDIATELY
  TRIGGERS ON 80 PERCENT DO NOTIFY
           ON 100 PERCENT DO SUSPEND;
ALTER WAREHOUSE TRICON_DE_WH SET RESOURCE_MONITOR = TRICON_DE_MONITOR;

-- 2e. Read access to sample data and Cortex (CoCo Desktop, Cortex Analyst)
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE_SAMPLE_DATA TO ROLE TRICON_DE_ROLE;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE TRICON_DE_ROLE;

-- Done. Next: 03_optional.sql (only if needed), then 04_attendees.sql.
