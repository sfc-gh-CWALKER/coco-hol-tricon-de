-- =====================================================================
-- STEP 4 of 5 - GIVE ATTENDEES ACCESS
-- Adds ONE extra role to each attendee. Does not change their default role, default warehouse,
-- password, MFA, or any existing grant.
-- =====================================================================
USE ROLE SECURITYADMIN;

-- One line per attendee (use the Snowflake LOGIN/user name; double-quote names with special characters).
GRANT ROLE TRICON_DE_ROLE TO USER "<USERNAME_1>";
-- GRANT ROLE TRICON_DE_ROLE TO USER "<USERNAME_2>";
-- GRANT ROLE TRICON_DE_ROLE TO USER "<USERNAME_3>";

-- Check who has it:
SHOW GRANTS OF ROLE TRICON_DE_ROLE;

-- If CoCo Desktop is blocked by a daily credit limit of 0 (01_preflight step 1d), allow attendees individually:
-- USE ROLE ACCOUNTADMIN;
-- ALTER USER "<USERNAME_1>" SET CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER = 20;
