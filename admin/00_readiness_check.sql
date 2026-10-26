-- =====================================================================================
--  TRICON "DATA ENGINEERING WITH CoCo" LAB - READINESS CHECK          (READ-ONLY)
--
--  Run this FIRST, before tricon_de_lab_setup.sql. It changes NOTHING: it only reads
--  account settings and reports PASS / WARN / FAIL with what to do about each one.
--
--  HOW TO RUN: Snowsight > Projects > Worksheets > + SQL Worksheet, paste this file,
--              pick any warehouse you normally use (top right), then "Run All".
--              The last result is one table: one row per check.
--
--  FAIL  = the lab will not work until this is fixed.
--  WARN  = the lab works, but read the "what_to_do" column (usually a decision for you).
--  PASS  = nothing to do.
-- =====================================================================================
USE ROLE ACCOUNTADMIN;

DECLARE
  rs RESULTSET;
  checks ARRAY DEFAULT ARRAY_CONSTRUCT();
  v STRING;
  found BOOLEAN;
  conflicts STRING DEFAULT '';
  pol_count INT DEFAULT 0;
BEGIN
  -- 1. Cross-region inference: CoCo Desktop requires it.
  v := 'DISABLED';
  rs := (SHOW PARAMETERS LIKE 'CORTEX_ENABLED_CROSS_REGION' IN ACCOUNT);
  FOR r IN rs DO v := r."value"; END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 1, 'check', 'Cross-region inference (CORTEX_ENABLED_CROSS_REGION)', 'value', v,
    'status', IFF(UPPER(v) = 'DISABLED', 'FAIL', 'PASS'),
    'what_to_do', IFF(UPPER(v) = 'DISABLED',
      'CoCo Desktop requires it. Decide with your security team, then e.g. ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = ''AWS_US''; (the setup script never changes it)', '')));

  -- 2. CoCo Desktop daily credit limit: 0 blocks everyone.
  v := '-1';
  rs := (SHOW PARAMETERS LIKE 'CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER' IN ACCOUNT);
  FOR r IN rs DO v := r."value"; END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 2, 'check', 'CoCo Desktop daily credit limit per user', 'value', v,
    'status', IFF(v = '0', 'FAIL', IFF(v = '-1', 'PASS', 'WARN')),
    'what_to_do', IFF(v = '0', 'CoCo Desktop is switched off for every user. Allow lab attendees: ALTER USER "<name>" SET CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER = 20;',
                  IFF(v = '-1', '', 'A limit is set. A lab day uses roughly 5-15 credits per person; raise it for attendees if it is lower'))));

  -- 3. Model allowlist: the lab uses Claude models through CoCo and AI_COMPLETE.
  v := 'ALL';
  rs := (SHOW PARAMETERS LIKE 'CORTEX_MODELS_ALLOWLIST' IN ACCOUNT);
  FOR r IN rs DO v := r."value"; END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 3, 'check', 'Cortex model allowlist (CORTEX_MODELS_ALLOWLIST)', 'value', v,
    'status', IFF(UPPER(v) = 'ALL', 'PASS', IFF(UPPER(v) = 'NONE', 'FAIL', 'WARN')),
    'what_to_do', IFF(UPPER(v) = 'ALL', '', 'Make sure claude-sonnet-4-5 (and the models CoCo Desktop offers) are allowed, or AI calls will fail')));

  -- 4. Browser sign-in for CoCo Desktop and dbt ("Local OAuth").
  found := FALSE;
  v := 'missing';
  rs := (SHOW SECURITY INTEGRATIONS LIKE 'SNOWFLAKE$LOCAL_APPLICATION');
  FOR r IN rs DO found := TRUE; v := IFF(r."enabled" = 'true', 'enabled', 'disabled'); END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 4, 'check', 'Browser sign-in for desktop tools (SNOWFLAKE$LOCAL_APPLICATION)', 'value', v,
    'status', IFF(v = 'enabled', 'PASS', 'WARN'),
    'what_to_do', IFF(v = 'enabled', '',
      'Attendees cannot use the recommended "Local OAuth" sign-in. SSO users: use External browser. Temporary lab logins: use Password + MFA (see the Getting Started page)')));

  -- 5. SSO: is a SAML integration configured? (decides which sign-in SSO users pick)
  found := FALSE;
  rs := (SHOW SECURITY INTEGRATIONS);
  FOR r IN rs DO
    IF (STARTSWITH(UPPER(r."type"), 'SAML2') AND r."enabled" = 'true') THEN found := TRUE; END IF;
  END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 5, 'check', 'SSO (SAML) integration', 'value', IFF(found, 'configured', 'none found'),
    'status', 'PASS',
    'what_to_do', IFF(found, 'Existing users can sign in to CoCo Desktop and dbt with their normal Tricon SSO',
                             'No SSO: existing users sign in with Local OAuth (browser) using their normal password + MFA')));

  -- 6. Account network policy: attendee laptops must be on an allowed network.
  v := '';
  rs := (SHOW PARAMETERS LIKE 'NETWORK_POLICY' IN ACCOUNT);
  FOR r IN rs DO v := COALESCE(r."value", ''); END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 6, 'check', 'Account network policy', 'value', IFF(v = '', '(none)', v),
    'status', IFF(v = '', 'PASS', 'WARN'),
    'what_to_do', IFF(v = '', '', 'Every attendee laptop (including the India team) must connect from an allowed network or VPN. Ask each person to open the login URL from their laptop before lab day')));

  -- 7. Authentication policies can block desktop tools (CoCo Desktop and dbt are "DRIVERS" clients).
  rs := (SHOW AUTHENTICATION POLICIES IN ACCOUNT);
  FOR r IN rs DO pol_count := pol_count + 1; END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 7, 'check', 'Authentication policies in the account', 'value', pol_count::STRING,
    'status', IFF(pol_count = 0, 'PASS', 'WARN'),
    'what_to_do', IFF(pol_count = 0, '',
      'If a policy applies to the account or to attendees, make sure CLIENT_TYPES allows DRIVERS (CoCo Desktop and dbt) and AUTHENTICATION_METHODS allows OAUTH (and PASSWORD for temporary lab logins). Check: DESCRIBE AUTHENTICATION POLICY <name>;')));

  -- 8. Snowflake's TPC-H sample data: the dbt project reads it.
  found := FALSE;
  rs := (SHOW DATABASES LIKE 'SNOWFLAKE_SAMPLE_DATA');
  FOR r IN rs DO found := TRUE; END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 8, 'check', 'SNOWFLAKE_SAMPLE_DATA (TPC-H)', 'value', IFF(found, 'present', 'not present'),
    'status', 'PASS',
    'what_to_do', IFF(found, '', 'The setup script adds it from Snowflake''s free SFC_SAMPLES share. If that fails, see ADMIN_GUIDE.md troubleshooting')));

  -- 9. Name conflicts: nothing called TRICON_DE* that this lab did not create.
  rs := (SHOW ROLES LIKE 'TRICON\\_DE%');
  FOR r IN rs DO
    IF (NOT COALESCE(r."comment", '') ILIKE 'TEMPORARY - Tricon CoCo DE lab%') THEN conflicts := conflicts || 'role ' || r."name" || '; '; END IF;
  END FOR;
  rs := (SHOW WAREHOUSES LIKE 'TRICON\\_DE%');
  FOR r IN rs DO
    IF (NOT COALESCE(r."comment", '') ILIKE 'TEMPORARY - Tricon CoCo DE lab%') THEN conflicts := conflicts || 'warehouse ' || r."name" || '; '; END IF;
  END FOR;
  rs := (SHOW DATABASES LIKE 'TRICON\\_DE');
  FOR r IN rs DO
    IF (NOT COALESCE(r."comment", '') ILIKE 'TEMPORARY - Tricon CoCo DE lab%') THEN conflicts := conflicts || 'database ' || r."name" || '; '; END IF;
  END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 9, 'check', 'No conflicting TRICON_DE* objects', 'value', IFF(conflicts = '', 'none', conflicts),
    'status', IFF(conflicts = '', 'PASS', 'FAIL'),
    'what_to_do', IFF(conflicts = '', '', 'Something with a lab name already exists. Do not run setup; contact the facilitator')));

  -- 10. Sign-in caching: without it, dbt asks SSO/password+MFA users to sign in on EVERY dbt command.
  --     (Local OAuth from check 4 caches its access token for 10-60 minutes instead, so this matters mainly as a fallback.)
  v := '';
  rs := (SHOW PARAMETERS LIKE 'ALLOW_ID_TOKEN' IN ACCOUNT);
  FOR r IN rs DO v := 'ALLOW_ID_TOKEN=' || r."value"; END FOR;
  rs := (SHOW PARAMETERS LIKE 'ALLOW_CLIENT_MFA_CACHING' IN ACCOUNT);
  FOR r IN rs DO v := v || ', ALLOW_CLIENT_MFA_CACHING=' || r."value"; END FOR;
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 10, 'check', 'Sign-in caching for desktop tools', 'value', v,
    'status', IFF(CONTAINS(v, 'false'), 'WARN', 'PASS'),
    'what_to_do', IFF(CONTAINS(v, 'false'),
      'Fine if check 4 is PASS (attendees use Local OAuth). Otherwise SSO users get a browser pop-up, and password users an MFA push, on every dbt command. Optional, security-team decision: ALTER ACCOUNT SET ALLOW_ID_TOKEN = TRUE; ALTER ACCOUNT SET ALLOW_CLIENT_MFA_CACHING = TRUE;', '')));

  -- 11. Region (informational: confirms cross-region setting is sensible).
  checks := ARRAY_APPEND(checks, OBJECT_CONSTRUCT(
    'n', 11, 'check', 'Account and region', 'value', CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME() || ' / ' || CURRENT_REGION(),
    'status', 'PASS',
    'what_to_do', 'This is the account_identifier attendees type into CoCo Desktop and dbt'));

  rs := (SELECT f.value:n::INT AS n, f.value:status::STRING AS status, f.value:check::STRING AS check_name,
                f.value:value::STRING AS current_value, f.value:what_to_do::STRING AS what_to_do
         FROM TABLE(FLATTEN(INPUT => :checks)) f ORDER BY n);
  RETURN TABLE(rs);
END;

-- NOT CHECKED HERE (cannot be read with SQL):
--   * Snowflake edition: module A2 (classification + masking) needs Enterprise or higher.
--     admin/05_verify.sql tests it directly after setup.
--   * Attendee laptops: CoCo Desktop, Git, Python 3.10-3.13 and dbt installs.
--     See admin/LAB_READINESS_GUIDE.md, Part B.
