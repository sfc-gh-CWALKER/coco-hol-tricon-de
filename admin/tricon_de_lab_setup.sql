-- =====================================================================================
--  TRICON "DATA ENGINEERING WITH CoCo" LAB - ONE-SHOT SETUP            (tested end to end)
--
--  HOW TO RUN: Snowsight > Projects > Worksheets > + SQL Worksheet, paste this file,
--              edit SECTION 0 only, then "Run All" (Cmd/Ctrl + Shift + Enter).
--              Or let CoCo Desktop run it for you - see admin/ADMIN_GUIDE.md, "Option B".
--
--  WHAT IT CREATES (new, temporary objects only - every one labelled "TEMPORARY - Tricon CoCo DE lab"):
--    TRICON_DE_ROLE     role attendees use in CoCo Desktop
--    TRICON_DE_WH       Small warehouse, auto-suspends after 60 s idle
--    TRICON_DE_MONITOR  hard stop at 40 credits/week on TRICON_DE_WH only
--    TRICON_DE          database with one personal schema per attendee: TRICON_DE.DBT_<INITIALS>
--
--  WHAT IT NEVER DOES: alter or drop any existing user, role, warehouse, database or grant;
--    change account parameters, network policies or authentication; create passwords or tokens;
--    give access to any Tricon data (attendees only see Snowflake's TPC-H sample + synthetic data).
--
--  SAFE TO RE-RUN (e.g. to add attendees). REMOVE EVERYTHING: admin/99_teardown.sql
--
--  IF A SAFETY CHECK FAILS the script stops with an error that reads like:
--      Numeric value 'STOP: <reason>' is not recognized
--  Read <reason>, fix it, and press Run All again. Nothing after the check has run.
-- =====================================================================================

-- -------------------------------------------------------------------------------------
-- 0. ATTENDEES  >>> THE ONLY PART YOU EDIT <<<
--    One line per person: {"user": "<Snowflake user name>", "initials": "<2-4 letters>"}
--    User name = NAME column in Snowsight > Admin > Users & Roles > Users (not the email).
--    Initials must be unique. Include yourself so you can test. Keep the commas between lines.
-- -------------------------------------------------------------------------------------
SET ATTENDEES = '[
  {"user": "JSMITH", "initials": "JS"},
  {"user": "APATEL", "initials": "AP"}
]';

-- -------------------------------------------------------------------------------------
-- 1. LAB WAREHOUSE FIRST (the safety checks below need a running warehouse)
--    If TRICON_DE_WH already exists this does nothing; check 2a then confirms it is ours.
-- -------------------------------------------------------------------------------------
USE ROLE SYSADMIN;
CREATE WAREHOUSE IF NOT EXISTS TRICON_DE_WH
  WAREHOUSE_SIZE = 'SMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE
  COMMENT = 'TEMPORARY - Tricon CoCo DE lab compute. Remove with admin/99_teardown.sql';
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE TRICON_DE_WH;

-- -------------------------------------------------------------------------------------
-- 2. SAFETY CHECKS (each stops the script if something is wrong)
-- -------------------------------------------------------------------------------------
-- 2a. Never reuse an existing TRICON_DE* object this lab did not create; CoCo Desktop prerequisite.
DECLARE
  problems STRING DEFAULT '';
  rs RESULTSET;
BEGIN
  rs := (SHOW ROLES LIKE 'TRICON\\_DE\\_%');
  FOR r IN rs DO
    IF (NOT COALESCE(r."comment", '') ILIKE 'TEMPORARY - Tricon CoCo DE lab%') THEN
      problems := problems || 'existing role ' || r."name" || ' was not created by this lab; ';
    END IF;
  END FOR;
  rs := (SHOW WAREHOUSES LIKE 'TRICON\\_DE\\_%');
  FOR r IN rs DO
    IF (NOT COALESCE(r."comment", '') ILIKE 'TEMPORARY - Tricon CoCo DE lab%') THEN
      problems := problems || 'existing warehouse ' || r."name" || ' was not created by this lab; ';
    END IF;
  END FOR;
  rs := (SHOW DATABASES LIKE 'TRICON\\_DE');
  FOR r IN rs DO
    IF (NOT COALESCE(r."comment", '') ILIKE 'TEMPORARY - Tricon CoCo DE lab%') THEN
      problems := problems || 'existing database ' || r."name" || ' was not created by this lab; ';
    END IF;
  END FOR;
  rs := (SHOW PARAMETERS LIKE 'CORTEX_ENABLED_CROSS_REGION' IN ACCOUNT);
  FOR r IN rs DO
    IF (UPPER(r."value") = 'DISABLED') THEN
      problems := problems || 'CORTEX_ENABLED_CROSS_REGION is DISABLED - CoCo Desktop needs cross-region inference (see ADMIN_GUIDE.md); ';
    END IF;
  END FOR;
  IF (problems <> '') THEN
    EXECUTE IMMEDIATE 'SELECT TO_NUMBER(''STOP: ' || REPLACE(problems, '''', '') || 'contact the lab facilitator'')';
  END IF;
  RETURN 'OK: no conflicting objects; cross-region inference enabled';
END;

-- 2b. Validate the attendee list: initials 2-4 letters/digits, no duplicates, every user exists and is enabled.
DECLARE
  problems STRING;
  n INT;
  users_rs RESULTSET;
  enabled_users ARRAY DEFAULT ARRAY_CONSTRUCT();
  disabled_users ARRAY DEFAULT ARRAY_CONSTRUCT();
  enabled_json STRING;
  disabled_json STRING;
BEGIN
  users_rs := (SHOW USERS);
  FOR u IN users_rs DO
    IF (u."disabled" = 'true') THEN
      disabled_users := ARRAY_APPEND(disabled_users, UPPER(u."name"));
    ELSE
      enabled_users := ARRAY_APPEND(enabled_users, UPPER(u."name"));
    END IF;
  END FOR;
  enabled_json := TO_JSON(enabled_users);
  disabled_json := TO_JSON(disabled_users);
  SELECT LISTAGG(msg, ' | ') INTO :problems FROM (
    WITH a AS (
      SELECT TRIM(f.value:user::STRING) AS user_name, UPPER(TRIM(f.value:initials::STRING)) AS initials
      FROM TABLE(FLATTEN(INPUT => PARSE_JSON($ATTENDEES))) f
    )
    SELECT 'blank user or initials' AS msg FROM a WHERE COALESCE(user_name, '') = '' OR COALESCE(initials, '') = '' GROUP BY 1
    UNION ALL SELECT 'initials must be 2-4 letters/digits: ' || initials FROM a WHERE NOT REGEXP_LIKE(initials, '[A-Z0-9]{2,4}')
    UNION ALL SELECT 'duplicate initials: ' || initials FROM a GROUP BY initials HAVING COUNT(*) > 1
    UNION ALL SELECT 'duplicate user: ' || UPPER(user_name) FROM a GROUP BY UPPER(user_name) HAVING COUNT(*) > 1
    UNION ALL SELECT 'user is disabled: ' || user_name FROM a WHERE ARRAY_CONTAINS(UPPER(user_name)::VARIANT, PARSE_JSON(:disabled_json))
    UNION ALL SELECT 'user not found: ' || user_name FROM a
      WHERE NOT ARRAY_CONTAINS(UPPER(user_name)::VARIANT, PARSE_JSON(:enabled_json))
        AND NOT ARRAY_CONTAINS(UPPER(user_name)::VARIANT, PARSE_JSON(:disabled_json))
  );
  IF (COALESCE(problems, '') <> '') THEN
    EXECUTE IMMEDIATE 'SELECT TO_NUMBER(''STOP: fix the attendee list in section 0 - ' || REPLACE(problems, '''', '') || ''')';
  END IF;
  SELECT COUNT(*) INTO :n FROM TABLE(FLATTEN(INPUT => PARSE_JSON($ATTENDEES)));
  RETURN 'OK: attendee list valid (' || n || ' people)';
END;

-- -------------------------------------------------------------------------------------
-- 3. SHARED LAB OBJECTS
-- -------------------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_SAMPLE_DATA FROM SHARE SFC_SAMPLES.SAMPLE_DATA;  -- "already exists" is fine

USE ROLE USERADMIN;
CREATE ROLE IF NOT EXISTS TRICON_DE_ROLE
  COMMENT = 'TEMPORARY - Tricon CoCo DE lab attendees. Remove with admin/99_teardown.sql';
GRANT ROLE TRICON_DE_ROLE TO ROLE SYSADMIN;           -- standard practice: admins keep visibility

USE ROLE SYSADMIN;
CREATE DATABASE IF NOT EXISTS TRICON_DE
  DATA_RETENTION_TIME_IN_DAYS = 1
  COMMENT = 'TEMPORARY - Tricon CoCo DE lab sandbox. TPC-H sample + synthetic data only. Remove with admin/99_teardown.sql';
GRANT USAGE, CREATE SCHEMA ON DATABASE TRICON_DE TO ROLE TRICON_DE_ROLE;
GRANT USAGE, OPERATE ON WAREHOUSE TRICON_DE_WH TO ROLE TRICON_DE_ROLE;   -- use only; cannot resize

USE ROLE ACCOUNTADMIN;
CREATE RESOURCE MONITOR IF NOT EXISTS TRICON_DE_MONITOR
  WITH CREDIT_QUOTA = 40 FREQUENCY = WEEKLY START_TIMESTAMP = IMMEDIATELY
  TRIGGERS ON 80 PERCENT DO NOTIFY ON 100 PERCENT DO SUSPEND;
ALTER WAREHOUSE TRICON_DE_WH SET RESOURCE_MONITOR = TRICON_DE_MONITOR;

GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE_SAMPLE_DATA TO ROLE TRICON_DE_ROLE;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE TRICON_DE_ROLE;   -- required for CoCo Desktop + Cortex Analyst

-- -------------------------------------------------------------------------------------
-- 4. ONE PERSONAL AREA PER ATTENDEE: TRICON_DE.DBT_<INITIALS>
--    Adds the lab role to each person (their default role and warehouse are NOT changed)
--    and creates their schema, labelled with their name.
-- -------------------------------------------------------------------------------------
DECLARE
  c CURSOR FOR
    SELECT TRIM(f.value:user::STRING) AS user_name, UPPER(TRIM(f.value:initials::STRING)) AS initials
    FROM TABLE(FLATTEN(INPUT => PARSE_JSON($ATTENDEES))) f ORDER BY initials;
  report STRING DEFAULT '';
  users_rs RESULTSET;
  real_name STRING;
  sch STRING;
BEGIN
  FOR r IN c DO
    sch := 'TRICON_DE.DBT_' || r.initials;
    real_name := NULL;
    users_rs := (SHOW USERS);
    FOR u IN users_rs DO
      IF (UPPER(u."name") = UPPER(r.user_name)) THEN real_name := u."name"; END IF;
    END FOR;
    EXECUTE IMMEDIATE 'GRANT ROLE TRICON_DE_ROLE TO USER "' || REPLACE(real_name, '"', '""') || '"';
    EXECUTE IMMEDIATE 'CREATE SCHEMA IF NOT EXISTS ' || sch ||
      ' COMMENT = ''TEMPORARY - Tricon CoCo DE lab: personal area for ' || REPLACE(real_name, '''', '') || '''';
    EXECUTE IMMEDIATE 'GRANT OWNERSHIP ON SCHEMA ' || sch || ' TO ROLE TRICON_DE_ROLE COPY CURRENT GRANTS';
    report := report || real_name || ' -> ' || sch || ' READY; ';
  END FOR;
  RETURN report;
END;

-- -------------------------------------------------------------------------------------
-- 5. SUMMARY - send each attendee their row
-- -------------------------------------------------------------------------------------
SELECT TRIM(f.value:user::STRING)                                   AS attendee,
       UPPER(TRIM(f.value:initials::STRING))                        AS initials_for_lab_app,
       'TRICON_DE.DBT_' || UPPER(TRIM(f.value:initials::STRING))    AS personal_schema,
       'TRICON_DE_ROLE'                                             AS coco_desktop_role,
       'TRICON_DE_WH'                                               AS coco_desktop_warehouse,
       CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME() AS account_identifier,
       IFF(s.schema_name IS NOT NULL, 'READY', 'MISSING')           AS status
FROM TABLE(FLATTEN(INPUT => PARSE_JSON($ATTENDEES))) f
LEFT JOIN TRICON_DE.INFORMATION_SCHEMA.SCHEMATA s
  ON s.schema_name = 'DBT_' || UPPER(TRIM(f.value:initials::STRING))
ORDER BY 1;

-- EXPECT every row READY. Next: admin/05_verify.sql (2 minutes), then send attendees the lab link:
--   https://coco-hol-tricon-de-gejm3sg47ufychnq9jpkqg.streamlit.app/
-- Optional extras (reviewer role, email, Adaptive demo): admin/03_optional.sql
