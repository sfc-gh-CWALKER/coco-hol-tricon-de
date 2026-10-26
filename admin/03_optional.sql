-- =====================================================================
-- STEP 3 of 5 - OPTIONAL EXTRAS (each block is independent; skip any or all)
-- =====================================================================

-- 3a. Reviewer role for modules A3 (access review) and A6 (warehouse right-sizing) ---------
-- Read-only, but SENSITIVE: sees account-wide users, grants, login history and ALL query text.
-- Grant only to Snowflake admins / security owners. Skipping it only skips A3 and A6 (facilitator demos them).
USE ROLE USERADMIN;
CREATE ROLE IF NOT EXISTS TRICON_DE_REVIEWER
  COMMENT = 'TEMPORARY - read-only account metadata for Tricon CoCo DE lab A3/A6. Remove with admin/99_teardown.sql';
GRANT ROLE TRICON_DE_REVIEWER TO ROLE SECURITYADMIN;
USE ROLE ACCOUNTADMIN;
GRANT DATABASE ROLE SNOWFLAKE.SECURITY_VIEWER   TO ROLE TRICON_DE_REVIEWER;  -- users, roles, grants, logins
GRANT DATABASE ROLE SNOWFLAKE.USAGE_VIEWER      TO ROLE TRICON_DE_REVIEWER;  -- warehouse metering / load history
GRANT DATABASE ROLE SNOWFLAKE.GOVERNANCE_VIEWER TO ROLE TRICON_DE_REVIEWER;  -- query history, query metering
GRANT DATABASE ROLE SNOWFLAKE.OBJECT_VIEWER     TO ROLE TRICON_DE_REVIEWER;  -- object metadata
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER       TO ROLE TRICON_DE_REVIEWER;
GRANT USAGE ON WAREHOUSE TRICON_DE_WH TO ROLE TRICON_DE_REVIEWER;
GRANT MONITOR USAGE ON ACCOUNT TO ROLE TRICON_DE_REVIEWER;                     -- SHOW WAREHOUSES / usage across the account
-- GRANT ROLE TRICON_DE_REVIEWER TO USER "<ADMIN_USERNAME>";

-- 3b. Email for module A4 (KPI report) ---------------------------------------------------
-- Can only send to the listed, verified email addresses of users in this account.
-- USE ROLE ACCOUNTADMIN;
-- CREATE NOTIFICATION INTEGRATION IF NOT EXISTS TRICON_DE_EMAIL_INT
--   TYPE = EMAIL ENABLED = TRUE ALLOWED_RECIPIENTS = ('first.last@triconresidential.com')
--   COMMENT = 'TEMPORARY - Tricon CoCo DE lab KPI email. Remove with admin/99_teardown.sql';
-- GRANT USAGE ON INTEGRATION TRICON_DE_EMAIL_INT TO ROLE TRICON_DE_ROLE;

-- 3c. Facilitator demo warehouse for module A6 (Adaptive Warehouses) ---------------------
-- Enterprise edition + supported region only. Never used for real workloads; facilitator converts and rolls back.
-- USE ROLE SYSADMIN;
-- CREATE WAREHOUSE IF NOT EXISTS TRICON_DE_ADAPTIVE_DEMO_WH
--   WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE
--   COMMENT = 'TEMPORARY - Tricon CoCo DE lab Adaptive demo. Remove with admin/99_teardown.sql';
-- USE ROLE ACCOUNTADMIN;
-- ALTER WAREHOUSE TRICON_DE_ADAPTIVE_DEMO_WH SET RESOURCE_MONITOR = TRICON_DE_MONITOR;
