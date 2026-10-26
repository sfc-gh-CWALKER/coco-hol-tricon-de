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
--    TRICON_DE_<INI>    ONLY if you use "NEW" below: a temporary lab login that expires after 30 days
--
--  WHAT IT NEVER DOES: alter or drop any existing user, role, warehouse, database or grant;
--    change account parameters, network policies or authentication policies;
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
--    One line per person. "initials" (2-4 letters/digits, unique) names their area TRICON_DE.DBT_<INITIALS>.
--    "user" can be one of three things - mix them freely:
--
--    A) Their existing Snowflake user name   (RECOMMENDED - they log in exactly as they do today, e.g. SSO)
--         {"user": "JSMITH", "initials": "JS"}
--       Find it in Snowsight > Governance & security > Users & Roles > Users, NAME column (not the email).
--
--    B) "NEW" - the person has no Snowflake user. The script creates a temporary lab login TRICON_DE_<INITIALS>
--       (person type, lab role only - no secondary roles, starts with LAB_TEMP_PASSWORD below, must change it and set up MFA at first login,
--       expires in 30 days). The final result lists every username, password and login URL.
--         {"user": "NEW", "initials": "KL", "email": "kim.lee@triconresidential.com"}
--
--    C) A shared login - several people use the SAME user, each with their own area (their initials).
--       Use an existing shared user's name, or create one with "NEW" and point the others at it:
--         {"user": "NEW",           "initials": "LAB"},
--         {"user": "TRICON_DE_LAB", "initials": "MB"},
--         {"user": "TRICON_DE_LAB", "initials": "RT"}
--       Not recommended - see ADMIN_GUIDE.md "Choosing how attendees log in" for the trade-offs.
--
--    Include yourself so you can test. Keep the commas between lines.
-- -------------------------------------------------------------------------------------
SET ATTENDEES = '[
  {"user": "JSMITH", "initials": "JS"},
  {"user": "APATEL", "initials": "AP"}
]';

--    Starting password for every "NEW" lab login (option B/C). Easy to share, but each person is FORCED
--    to replace it (and set up MFA) the first time they sign in. Rules: at least 8 characters with an
--    uppercase letter, a lowercase letter and a number. Change it if your password policy is stricter.
SET LAB_TEMP_PASSWORD = 'TriconLab-2026';

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
  rs := (SHOW USERS LIKE 'TRICON\\_DE\\_%');
  FOR r IN rs DO
    IF (NOT COALESCE(r."comment", '') ILIKE 'TEMPORARY - Tricon CoCo DE lab%') THEN
      problems := problems || 'existing user ' || r."name" || ' was not created by this lab; ';
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

-- 2b. Validate the attendee list.
DECLARE
  problems STRING;
  n INT;
  users_rs RESULTSET;
  enabled_users ARRAY DEFAULT ARRAY_CONSTRUCT();
  disabled_users ARRAY DEFAULT ARRAY_CONSTRUCT();
  enabled_json STRING;
  disabled_json STRING;
  temp_pwd STRING;
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
      SELECT UPPER(TRIM(f.value:user::STRING)) AS user_name, UPPER(TRIM(f.value:initials::STRING)) AS initials,
             TRIM(f.value:email::STRING) AS email
      FROM TABLE(FLATTEN(INPUT => PARSE_JSON($ATTENDEES))) f
    ), new_logins AS (                 -- logins this run will create, so others may share them (option C)
      SELECT 'TRICON_DE_' || initials AS user_name FROM a WHERE user_name = 'NEW'
    )
    SELECT 'blank user or initials' AS msg FROM a WHERE COALESCE(user_name, '') = '' OR COALESCE(initials, '') = '' GROUP BY 1
    UNION ALL SELECT 'initials must be 2-4 letters/digits: ' || initials FROM a WHERE NOT REGEXP_LIKE(initials, '[A-Z0-9]{2,4}')
    UNION ALL SELECT 'duplicate initials: ' || initials FROM a GROUP BY initials HAVING COUNT(*) > 1
    UNION ALL SELECT 'email does not look valid: ' || email FROM a WHERE email IS NOT NULL AND NOT REGEXP_LIKE(email, '[^@ ]+@[^@ ]+\\.[^@ ]+')
    UNION ALL SELECT 'user is disabled: ' || user_name FROM a WHERE ARRAY_CONTAINS(user_name::VARIANT, PARSE_JSON(:disabled_json))
    UNION ALL SELECT 'user ' || user_name || ' does not exist in this account - if this person has no Snowflake user, change that line to {"user": "NEW", "initials": "' || initials || '"} to create a temporary lab login' FROM a
      WHERE user_name <> 'NEW'
        AND NOT ARRAY_CONTAINS(user_name::VARIANT, PARSE_JSON(:enabled_json))
        AND NOT ARRAY_CONTAINS(user_name::VARIANT, PARSE_JSON(:disabled_json))
        AND user_name NOT IN (SELECT user_name FROM new_logins)
  );
  IF (COALESCE(problems, '') <> '') THEN
    EXECUTE IMMEDIATE 'SELECT TO_NUMBER(''STOP: fix the attendee list in section 0 - ' || REPLACE(problems, '''', '') || ''')';
  END IF;
  SELECT $LAB_TEMP_PASSWORD INTO :temp_pwd;
  IF (NOT (LENGTH(temp_pwd) >= 8 AND REGEXP_LIKE(temp_pwd, '.*[A-Z].*')
           AND REGEXP_LIKE(temp_pwd, '.*[a-z].*') AND REGEXP_LIKE(temp_pwd, '.*[0-9].*')
           AND NOT CONTAINS(temp_pwd, ''''))) THEN
    EXECUTE IMMEDIATE 'SELECT TO_NUMBER(''STOP: LAB_TEMP_PASSWORD in section 0 needs 8+ characters with an uppercase letter, a lowercase letter and a number (no quotes)'')';
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
--    A) existing user: adds the lab role (their default role/warehouse/login are NOT changed)
--    B) "NEW": creates lab login TRICON_DE_<INITIALS> with LAB_TEMP_PASSWORD (must be changed at first sign-in).
--       On a re-run, a lab login that has never signed in gets LAB_TEMP_PASSWORD re-applied;
--       one that has already signed in is left alone (it keeps the password its owner chose).
--    C) shared login: same as A or B; each person still gets their own schema
-- -------------------------------------------------------------------------------------
CREATE OR REPLACE TEMPORARY TABLE TRICON_DE.PUBLIC.TRICON_DE_SETUP_RESULTS
  (attendee STRING, login_user STRING, initials STRING, login_type STRING, temp_password STRING, first_steps STRING);

DECLARE
  c CURSOR FOR
    SELECT UPPER(TRIM(f.value:user::STRING)) AS user_name, UPPER(TRIM(f.value:initials::STRING)) AS initials,
           TRIM(f.value:email::STRING) AS email, f.index AS pos
    FROM TABLE(FLATTEN(INPUT => PARSE_JSON($ATTENDEES))) f
    ORDER BY IFF(UPPER(TRIM(f.value:user::STRING)) = 'NEW', 0, 1), pos;   -- create NEW logins first
  users_rs RESULTSET;
  login STRING;
  login_type STRING;
  pwd STRING;
  steps STRING;
  temp_pwd STRING;
  exists_already BOOLEAN;
  never_signed_in BOOLEAN;
  sch STRING;
  ini STRING;
  req STRING;
  report STRING DEFAULT '';
BEGIN
  SELECT $LAB_TEMP_PASSWORD INTO :temp_pwd;
  FOR r IN c DO
    sch := 'TRICON_DE.DBT_' || r.initials;
    pwd := NULL;
    IF (r.user_name = 'NEW') THEN
      login := 'TRICON_DE_' || r.initials;
      exists_already := FALSE;
      never_signed_in := TRUE;
      users_rs := (SHOW USERS LIKE 'TRICON\\_DE\\_%');
      FOR u IN users_rs DO
        IF (UPPER(u."name") = login) THEN
          exists_already := TRUE;
          never_signed_in := (u."last_success_login" IS NULL);
        END IF;
      END FOR;
      IF (NOT exists_already) THEN
        EXECUTE IMMEDIATE 'CREATE USER ' || login ||
          ' TYPE = PERSON PASSWORD = ''' || temp_pwd || ''' MUST_CHANGE_PASSWORD = TRUE' ||
          ' DAYS_TO_EXPIRY = 30' ||
          ' DEFAULT_ROLE = TRICON_DE_ROLE DEFAULT_SECONDARY_ROLES = () DEFAULT_WAREHOUSE = TRICON_DE_WH DEFAULT_NAMESPACE = ''' || sch || '''' ||
          IFF(r.email IS NULL, '', ' EMAIL = ''' || REPLACE(r.email, '''', '') || '''') ||
          ' COMMENT = ''TEMPORARY - Tricon CoCo DE lab login for initials ' || r.initials || ' (expires after 30 days). Remove with admin/99_teardown.sql''';
        login_type := 'B) new lab login';
        pwd := temp_pwd;
      ELSEIF (never_signed_in) THEN
        -- Re-apply the starting password. If Snowflake says PRIOR_USE, it already has this password - nothing to do.
        BEGIN
          EXECUTE IMMEDIATE 'ALTER USER ' || login || ' SET PASSWORD = ''' || temp_pwd || ''' MUST_CHANGE_PASSWORD = TRUE';
          login_type := 'B) lab login (not signed in yet - starting password re-applied)';
        EXCEPTION
          WHEN OTHER THEN
            IF (CONTAINS(SQLERRM, 'PRIOR_USE')) THEN
              login_type := 'B) lab login (not signed in yet - already has the starting password)';
            ELSE
              RAISE;
            END IF;
        END;
        pwd := temp_pwd;
      ELSE
        login_type := 'B) lab login (already signed in - uses the password they chose)';
      END IF;
      IF (exists_already) THEN   -- keep lab logins scoped to the lab role only (older runs did not set this)
        EXECUTE IMMEDIATE 'ALTER USER ' || login || ' SET DEFAULT_SECONDARY_ROLES = ()';
      END IF;
    ELSE
      login := NULL;
      users_rs := (SHOW USERS);
      FOR u IN users_rs DO
        IF (UPPER(u."name") = r.user_name) THEN login := u."name"; END IF;
      END FOR;
      login_type := IFF(STARTSWITH(UPPER(login), 'TRICON_DE_'), 'C) shared lab login', 'A) existing user');
    END IF;
    steps := IFF(pwd IS NOT NULL,
        '1) Open the login URL  2) Username ' || login || ', password ' || COALESCE(pwd, '') ||
        '  3) Choose your own new password when asked  4) Set up MFA when asked  5) Follow Getting Started in the lab app',
      IFF(STARTSWITH(login_type, 'A)'),
        'Sign in as you normally do (e.g. Tricon SSO), then follow Getting Started in the lab app',
        'Sign in with username ' || login || ' and the password already chosen, then follow Getting Started in the lab app'));
    EXECUTE IMMEDIATE 'GRANT ROLE TRICON_DE_ROLE TO USER "' || REPLACE(login, '"', '""') || '"';
    EXECUTE IMMEDIATE 'CREATE SCHEMA IF NOT EXISTS ' || sch ||
      ' COMMENT = ''TEMPORARY - Tricon CoCo DE lab: personal area for ' || r.initials || ' (login ' || REPLACE(login, '''', '') || ')''';
    EXECUTE IMMEDIATE 'GRANT OWNERSHIP ON SCHEMA ' || sch || ' TO ROLE TRICON_DE_ROLE COPY CURRENT GRANTS';
    ini := r.initials;
    req := r.user_name;
    INSERT INTO TRICON_DE.PUBLIC.TRICON_DE_SETUP_RESULTS VALUES (:req, :login, :ini, :login_type, :pwd, :steps);
    report := report || r.initials || ' -> ' || login || ' (' || login_type || '); ';
  END FOR;
  RETURN report;
END;

-- -------------------------------------------------------------------------------------
-- 5. LAB USER LIST - send each attendee their row (download it with the button above the result).
--    This must stay the LAST statement: Snowsight's Run All shows the last result.
-- -------------------------------------------------------------------------------------
SELECT r.initials                                                              AS initials,
       r.login_user                                                            AS username,
       COALESCE(r.temp_password, '')                                           AS temporary_password,
       'https://app.snowflake.com/' || LOWER(CURRENT_ORGANIZATION_NAME()) || '/' || LOWER(CURRENT_ACCOUNT_NAME())
                                                                               AS login_url,
       r.first_steps                                                           AS first_login_steps,
       r.login_type,
       'TRICON_DE.DBT_' || r.initials                                          AS personal_schema,
       'TRICON_DE_ROLE'                                                        AS coco_desktop_role,
       'TRICON_DE_WH'                                                          AS coco_desktop_warehouse,
       CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME()            AS account_identifier,
       'https://coco-hol-tricon-de-gejm3sg47ufychnq9jpkqg.streamlit.app/'      AS lab_guide,
       IFF(s.schema_name IS NOT NULL, 'READY', 'MISSING')                      AS status,
       IFF(COUNT(*) OVER (PARTITION BY r.login_user) > 1,
           'SHARED LOGIN (' || COUNT(*) OVER (PARTITION BY r.login_user) || ' people) - see ADMIN_GUIDE.md', '') AS note
FROM TRICON_DE.PUBLIC.TRICON_DE_SETUP_RESULTS r
LEFT JOIN TRICON_DE.INFORMATION_SCHEMA.SCHEMATA s ON s.schema_name = 'DBT_' || r.initials
ORDER BY IFF(r.temp_password IS NOT NULL, 0, 1), r.initials;

-- EXPECT every row READY. Next: admin/05_verify.sql (2 minutes), then send attendees their rows.
-- Optional extras (reviewer role, email, Adaptive demo): admin/03_optional.sql
