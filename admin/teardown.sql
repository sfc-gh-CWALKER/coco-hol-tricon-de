-- Tricon "Data Engineering with CoCo" lab - teardown. Run as ACCOUNTADMIN after the hackathon week.
USE ROLE ACCOUNTADMIN;
DROP DATABASE IF EXISTS TRICON_DE;                  -- all attendee DBT_<INITIALS> schemas, semantic views, policies
DROP WAREHOUSE IF EXISTS TRICON_DE_WH;
DROP WAREHOUSE IF EXISTS TRICON_DE_ADAPTIVE_DEMO_WH;
DROP RESOURCE MONITOR IF EXISTS TRICON_DE_MONITOR;
DROP INTEGRATION IF EXISTS TRICON_DE_EMAIL_INT;
DROP ROLE IF EXISTS TRICON_DE_REVIEWER;
DROP ROLE IF EXISTS TRICON_DE_ROLE;
-- Keep SNOWFLAKE_SAMPLE_DATA unless it was created only for this lab.
-- Published plugins live in each user's USER$<NAME>.SKILL_SHARING schema; remove them from CoCo Desktop if no longer wanted.
