# Tricon Admin Guide: "Data Engineering with CoCo" Lab Setup

**Audience:** Tricon's Snowflake administrator (ACCOUNTADMIN access)
**Time needed:** about 30 minutes, at least 3 business days before the lab
**Lab guide app:** https://coco-hol-tricon-de-gejm3sg47ufychnq9jpkqg.streamlit.app/
**Scripts:** `admin/` folder in https://github.com/sfc-gh-cwalker/coco-hol-tricon-de

---

## What this does, and what it never does

The lab gives Tricon users a sandbox for learning **CoCo Desktop** (Snowflake's AI coding agent) and its best practices: project rules (`AGENTS.md`), skills, plugins, safety hooks, and review agents.

**It only creates new, clearly labelled, temporary objects:**

| Object | Type | Purpose |
|---|---|---|
| `TRICON_DE_ROLE` | Role | Attendees' lab role |
| `TRICON_DE` | Database | Sandbox; each attendee creates their own `DBT_<INITIALS>` schema |
| `TRICON_DE_WH` | Warehouse (Small, auto-suspend 60 s) | Lab compute |
| `TRICON_DE_MONITOR` | Resource monitor | **Hard stop at 40 credits/week** on the lab warehouse only |
| `TRICON_DE_REVIEWER` | Role, *optional* | Read-only metadata for two admin-focused modules |
| `TRICON_DE_EMAIL_INT`, `TRICON_DE_ADAPTIVE_DEMO_WH` | *optional* | Email and demo extras; off by default |

Every object's comment begins with `TEMPORARY - Tricon CoCo DE lab`.

**It never:**
- modifies or drops any existing user, role, warehouse, database, or grant
- changes account parameters, network policies, or authentication settings
- creates passwords, tokens (PATs), or service users
- gives attendees access to Tricon data. They see only Snowflake's built-in TPC-H sample data and a 40-row synthetic CSV
- lets attendees resize warehouses, create databases, or change grants (verified in Step 5)

**The data:** TPC-H (`SNOWFLAKE_SAMPLE_DATA`, Snowflake's free read-only sample) plus `resident_contacts.csv`, which is **entirely synthetic** (fake names and `@example.com` emails). No Tricon or resident data is used.

**Removal:** `99_teardown.sql` drops exactly the objects above by exact name and nothing else.

---

## Step 0: Before you start

- [ ] You can log in to Snowsight with the **ACCOUNTADMIN** role (the scripts also use USERADMIN, SYSADMIN, and SECURITYADMIN, which ACCOUNTADMIN inherits).
- [ ] You have the list of attendees' Snowflake **user names** (Admin → Users & Roles → Users).
- [ ] Download the `admin/` folder, or open each file on GitHub and copy it into a Snowsight SQL worksheet.

**How to run a script:** in Snowsight, open **Projects → Worksheets → + SQL Worksheet**, paste the script, and use **Run All** (the down-arrow next to ▶, or `Cmd/Ctrl + Shift + Enter`). Read the `EXPECT:` comments as you go.

---

## Step 1: Pre-flight checks (`01_preflight.sql`). Read-only; changes nothing.

| Check | Expected | If not |
|---|---|---|
| 1a. Account identifier | Note the `account_identifier` value | Send it to attendees and the facilitator |
| 1b. Five name-collision checks | **0 rows each** | **Stop** and contact the facilitator |
| 1c. `SNOWFLAKE_SAMPLE_DATA` | 1 row (already present) | 0 rows is fine; Step 2a mounts it |
| 1d. `CORTEX_ENABLED_CROSS_REGION` | Anything except `DISABLED` | CoCo Desktop requires cross-region inference. Decide with your security team; the lab scripts don't change it |
| 1d. `CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER` | `-1` (no limit) or a positive number | If `0`, Desktop is blocked; see the optional line in Step 4 |
| 1e. Edition | Enterprise or higher | Standard: use the single-cluster warehouse line in Step 2. Module A2 (classification) won't work |

---

## Step 2: Create the lab environment (`02_setup.sql`)

Run the whole script. It's safe to re-run (`IF NOT EXISTS`). It:

1. Mounts the sample data if missing (skip 2a if Step 1c found it).
2. Creates `TRICON_DE_ROLE` and rolls it up to SYSADMIN (standard practice, so admins keep visibility).
3. Creates the `TRICON_DE` database and `TRICON_DE_WH` warehouse, **owned by SYSADMIN**. The lab role gets only `USAGE`/`CREATE SCHEMA` on the database and `USAGE`/`OPERATE` on the warehouse.
4. Creates the 40-credit/week resource monitor and attaches it to the lab warehouse **only**.
5. Grants read access to sample data and `SNOWFLAKE.CORTEX_USER` (needed for CoCo Desktop) to the lab role.

**Expected:** every statement returns "successfully created" or "Statement executed successfully."

**Cost:** Small warehouse = 2 credits/hour while running. It suspends after 60 seconds idle, and the monitor suspends it at 40 credits/week. A typical 20-person, 2-hour lab uses well under that cap.

---

## Step 3: Optional extras (`03_optional.sql`)

Each block is independent. **If unsure, skip all of them.** The core lab (Part 1 and modules A1, A2, A4, A5) doesn't need them.

| Block | Enables | Recommendation |
|---|---|---|
| 3a. `TRICON_DE_REVIEWER` | Modules A3 (access review) and A6 (warehouse right-sizing) on **real account metadata** | Read-only, but it can see all users, grants, login history, and query text. Grant it **only to Snowflake admins**, or skip it and the facilitator demos those modules |
| 3b. Email integration | Module A4 can email its KPI report | Skip unless you want the email demo. It can only send to addresses you list |
| 3c. Adaptive demo warehouse | Facilitator demo of Adaptive Warehouses | Enterprise edition and supported regions only. Skip if unsure |

Blocks 3b and 3c are commented out; uncomment them to use them.

---

## Step 4: Give attendees access (`04_attendees.sql`)

Add one `GRANT ROLE TRICON_DE_ROLE TO USER "<username>";` line per attendee and run it.

This **adds** a role. It doesn't change attendees' default role, default warehouse, password, or MFA.

> If Step 1d showed a credit limit of `0`, uncomment the `ALTER USER ... SET CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER = 20` lines for attendees.

Also grant yourself the role so you can run Step 5.

---

## Step 5: Verify (`05_verify.sql`)

Run it as yourself (after granting yourself `TRICON_DE_ROLE`) or have one attendee run it.

> **Admins:** keep the `USE SECONDARY ROLES NONE;` line. Without it, your admin roles make every check pass, including the ones that should fail.

| Check | Expected |
|---|---|
| Sample data count | `1500000` |
| Create schema / table | Success |
| `AI_COMPLETE` | `ready` |
| `SYSTEM$CLASSIFY` | A JSON result (Enterprise edition) |
| `ALTER WAREHOUSE ... LARGE` | **Error: insufficient privileges** ✅ |
| `CREATE DATABASE ...` | **Error: insufficient privileges** ✅ |

The script drops its test schema at the end and restores your secondary roles.

---

## Step 6: Attendee laptops (send this to attendees)

Each attendee needs these installed **before** lab day. Most need IT approval.

1. **CoCo Desktop** for macOS or Windows: https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop/onboarding-and-authentication
2. **Git**
3. **Python 3.10+** and `python -m pip install dbt-core dbt-snowflake`
4. Network access to Snowflake and github.com (to clone the public lab repo)

They sign in with their **normal Tricon SSO login**. dbt uses `authenticator: externalbrowser`, so no password or token is stored anywhere. The **Getting Started** page of the lab guide app walks them through it.

---

## Step 7: After the lab (`99_teardown.sql`)

Run it after hackathon week. It lists what will be removed, then drops only the exact `TRICON_DE*` objects:

- the database (all attendee schemas inside it)
- the two warehouses
- the resource monitor
- the email integration
- the two roles. Dropping a role also removes it from every user

Objects with similar names, such as an existing `TRICON_DEMO`, are never touched. `SNOWFLAKE_SAMPLE_DATA` is kept.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Attendee can't select `TRICON_DE_ROLE` in CoCo Desktop | Re-run their line in `04_attendees.sql`; they may need to sign out and back in |
| `Database 'SNOWFLAKE_SAMPLE_DATA' does not exist` | Run Step 2a, then the `IMPORTED PRIVILEGES` grant in 2e |
| CoCo Desktop says Cortex isn't available | Check Step 1d (cross-region inference, credit limit) and the `CORTEX_USER` grant |
| `unknown model` in Step 5 | Pick any GA model from `SHOW CORTEX BASE MODELS IN SCHEMA SNOWFLAKE.MODELS` |
| Warehouse suspended mid-lab | The weekly 40-credit monitor triggered. Raise `CREDIT_QUOTA` on `TRICON_DE_MONITOR` if needed |
| A negative check in Step 5 *succeeded* | Secondary roles were active. Run `USE SECONDARY ROLES NONE`, and if it was the resize, run `ALTER WAREHOUSE TRICON_DE_WH SET WAREHOUSE_SIZE = 'SMALL'` |

**Questions:** Carson Walker, Snowflake (carson.walker@snowflake.com)
