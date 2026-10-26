-- =====================================================================
-- VERIFY - run after tricon_de_lab_setup.sql (run as an attendee, or as the admin after granting yourself TRICON_DE_ROLE)
-- Creates and drops one throwaway schema. Every check should pass before lab day.
-- =====================================================================
USE ROLE TRICON_DE_ROLE;                  -- FAIL here = role not granted to you (add them to section 0 of tricon_de_lab_setup.sql and re-run it)
USE SECONDARY ROLES NONE;                 -- IMPORTANT for admins: test with ONLY the lab role's privileges
USE WAREHOUSE TRICON_DE_WH;               -- FAIL here = warehouse grant missing (tricon_de_lab_setup.sql section 3)

SELECT COUNT(*) AS orders FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS;
-- EXPECT 1500000                         -- FAIL = sample data / IMPORTED PRIVILEGES (tricon_de_lab_setup.sql section 3)

CREATE SCHEMA TRICON_DE.DBT_PREFLIGHT;    -- FAIL = CREATE SCHEMA grant missing (tricon_de_lab_setup.sql section 3)
CREATE TABLE TRICON_DE.DBT_PREFLIGHT.T AS SELECT 'jane.doe@example.com' AS EMAIL, '(555) 222-1234' AS PHONE;

SELECT AI_COMPLETE('claude-sonnet-4-5', 'Reply with the single word: ready') AS cortex_check;
-- EXPECT 'ready'. FAIL "unknown model" = pick any GA model from SHOW CORTEX BASE MODELS IN SCHEMA SNOWFLAKE.MODELS.
-- FAIL "not authorized" / region = Cortex access or cross-region inference (tricon_de_lab_setup.sql check 2a).

CALL SYSTEM$CLASSIFY('TRICON_DE.DBT_PREFLIGHT.T', NULL);
-- EXPECT a JSON result. FAIL "not supported" = Standard edition -> skip module A2.

DROP SCHEMA TRICON_DE.DBT_PREFLIGHT;      -- clean up

-- Negative checks: the lab role must NOT be able to do these. Each should return "Insufficient privileges".
ALTER WAREHOUSE TRICON_DE_WH SET WAREHOUSE_SIZE = 'LARGE';
CREATE DATABASE SHOULD_FAIL_TRICON;
-- If either SUCCEEDS, you still have secondary roles active - rerun USE SECONDARY ROLES NONE, and
-- if it was the ALTER, put it back: ALTER WAREHOUSE TRICON_DE_WH SET WAREHOUSE_SIZE = 'SMALL';

USE SECONDARY ROLES ALL;                  -- restore your normal session behaviour
