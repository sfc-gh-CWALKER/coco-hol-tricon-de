# Tricon Admin Guide: "Data Engineering with CoCo" Lab Setup

**For:** Tricon's Snowflake administrator (needs the ACCOUNTADMIN role)
**Time:** about 15 minutes, at least 3 business days before the lab
**Lab guide (send to attendees):** https://coco-hol-tricon-de-gejm3sg47ufychnq9jpkqg.streamlit.app/
**Scripts:** the `admin/` folder of https://github.com/sfc-gh-cwalker/coco-hol-tricon-de

The lab follows Snowflake's [Data Engineering with CoCo](https://www.snowflake.com/en/developers/guides/data-engineering-with-coco/) guide, adapted so a whole team can run it at once. **Each attendee gets their own personal schema**, so nobody overwrites anyone else.

---

## What the setup does, and what it never does

**It creates only these new, temporary objects.** Each one's comment starts with `TEMPORARY - Tricon CoCo DE lab`.

| Object | What it is |
|---|---|
| `TRICON_DE_ROLE` | The role attendees pick in CoCo Desktop |
| `TRICON_DE_WH` | Small warehouse; suspends after 60 s idle |
| `TRICON_DE_MONITOR` | **Hard stop at 40 credits/week**, on the lab warehouse only |
| `TRICON_DE` database | Holds one personal schema per attendee: `TRICON_DE.DBT_<INITIALS>` |

**It never:**
- changes or drops any existing user, role, warehouse, database, or grant
- changes attendees' default role, default warehouse, password, or MFA (it only *adds* the lab role)
- changes account parameters, network policies, or authentication
- creates tokens or service users. It creates a password **only** for people you mark `"NEW"`: a temporary login that must change its password and enroll in MFA, and that expires after 30 days
- gives access to any Tricon data. Attendees work only with Snowflake's built-in TPC-H sample and a 40-row **synthetic** CSV with fake names and `@example.com` emails

**Built-in safety checks.** The script stops before changing anything if:
- a `TRICON_DE*` object already exists that this lab didn't create
- CoCo Desktop's cross-region inference requirement isn't met
- the attendee list has a typo, a duplicate, or an unknown or disabled user

**Tested:** the full script, a re-run, the attendee checks, and teardown were all run end to end on a Snowflake account before release.

---

## Step 1: Fill in the attendee list

Open `admin/tricon_de_lab_setup.sql` and edit **section 0 only**. Add one line per person, including yourself so you can test. You can mix the three login types below in one list:

```sql
SET ATTENDEES = '[
  {"user": "JSMITH", "initials": "JS"},                                   -- A) existing user (recommended)
  {"user": "NEW",    "initials": "KL", "email": "kim.lee@triconresidential.com"},  -- B) no Snowflake user yet
  {"user": "YOURNAME", "initials": "YN"}                                  -- you, to test
]';
```

- `user` is the **NAME** column in Snowsight → **Governance & security → Users & Roles → Users**, not the email address. You can also use `"NEW"` (see below).
- `initials` must be 2–4 letters or digits and unique. Each person's area becomes `TRICON_DE.DBT_<initials>`.
- `email` is optional and only used for `"NEW"` logins.

### Choosing how attendees log in

Every option gives each person **their own schema**. They differ only in which Snowflake login the person uses.

| Option | Write in `user` | Who it's for | Login experience | Recommendation |
|---|---|---|---|---|
| **A) Existing user** | Their user NAME | Anyone with a Snowflake login today | Exactly as today (e.g. Tricon SSO). dbt uses `authenticator: externalbrowser` | **Use this whenever possible** |
| **B) Temporary lab login** | `"NEW"` | People with no Snowflake user (contractors, new joiners, India team members not yet provisioned) | Script creates `TRICON_DE_<INITIALS>` with a **one-time password**. The person must change it **and enroll in MFA** at first login. **Auto-expires after 30 days** | Good fallback. Send each password privately (not in a group chat) |
| **C) Shared login** | The same user for several people (e.g. `"NEW"` with initials `LAB`, then `"TRICON_DE_LAB"` for the others) | Last resort when individual logins aren't possible | Everyone signs in as one user; each still uses their own initials and schema | **Not recommended** (see below) |

**Why a shared login is a last resort:**
- **MFA:** Snowflake requires MFA for password logins by human users, and only one phone can be enrolled. Everyone would need that person's MFA prompt.
- **No accountability:** query history shows one user for everyone.
- **Shared CoCo state:** CoCo's per-user items (memory, the published plugin in Module 4, `USER$<name>` objects) would collide.
- **Option B instead:** a shared login isn't any faster to set up than giving each person a temporary login.

**About temporary logins (B):**
- Created as `TYPE = PERSON` with `MUST_CHANGE_PASSWORD = TRUE`, `DAYS_TO_EXPIRY = 30`, and `DEFAULT_ROLE`, warehouse and schema already set to the lab objects.
- The password is shown **once**, in the final result table. Copy it, or use the download button, before closing the worksheet. It isn't stored anywhere.
- Re-running the script never resets an existing temporary login's password. To reset one, drop that user and re-run.
- If Tricon enforces SSO-only sign-in through an authentication policy, password logins may be blocked. In that case, provision the person through Tricon's identity provider and use option A.
- `99_teardown.sql` removes these logins. Real users are never dropped.

---

## Step 2: Run the script (choose one option)

### Option A: Snowsight (recommended)

1. Snowsight → **Projects → Worksheets → + → SQL Worksheet**
2. Paste the whole of `tricon_de_lab_setup.sql` (with your edited section 0).
3. Click the **▼** next to the blue **▶** and choose **Run All** (or `Cmd/Ctrl + Shift + Enter`).
4. The last result is a table with **one row per attendee**. Every row should say **READY**.

If the script stops, the error reads `Numeric value 'STOP: <reason>' is not recognized`. Fix what `<reason>` says and click Run All again. Re-running is always safe.

### Option B: Let CoCo Desktop run it

If you already use CoCo Desktop connected to Tricon's account as ACCOUNTADMIN:

1. In CoCo Desktop, **File → Open Folder** and open a clone of the lab repo (`git clone https://github.com/sfc-gh-cwalker/coco-hol-tricon-de.git`).
2. Edit section 0 of `admin/tricon_de_lab_setup.sql` (Step 1).
3. Paste this prompt into the chat:

```
I'm the Snowflake admin setting up a temporary training lab. Use role ACCOUNTADMIN.
Read admin/ADMIN_GUIDE.md, then run admin/tricon_de_lab_setup.sql against my connection:
- First show me the attendee list in section 0 and wait for me to confirm it.
- Execute the statements strictly ONE AT A TIME in file order (never in parallel), each
  DECLARE...END block as a single statement.
- If any statement fails or a check returns STOP, stop immediately and explain the reason in plain English.
- Do not modify, edit, or run anything other than what is in this file. Do not touch any object not named TRICON_DE*.
- When finished, show the final summary table, then run admin/05_verify.sql the same way and give me a PASS/FAIL table.
```

CoCo asks you to approve each SQL statement, depending on your permission settings. Approving each one is a good way to review what runs.

---

## Step 3: Verify (`05_verify.sql`, 2 minutes)

Grant yourself the lab by including your own user in section 0, then run `05_verify.sql` in a worksheet. It tests as the lab role only (`USE SECONDARY ROLES NONE`):

| Check | Expected |
|---|---|
| Read sample data | `1500000` |
| Create schema and table | Success (cleaned up at the end) |
| `AI_COMPLETE` | `ready` |
| `SYSTEM$CLASSIFY` | A JSON result (requires Enterprise edition; on Standard, skip lab module A2) |
| Resize the warehouse | **Error: insufficient privileges** ✅ |
| Create a database | **Error: insufficient privileges** ✅ |

---

## Step 4: Send each attendee their row from the summary table

Each attendee needs these values from the summary table:

| Where | Value |
|---|---|
| Snowflake login | `snowflake_login` column (option A: their usual login) |
| One-time password (B only) | `one_time_password` column. **Send privately; it's shown only once** |
| CoCo Desktop connection: account | `account_identifier` column |
| CoCo Desktop: role / warehouse | `TRICON_DE_ROLE` / `TRICON_DE_WH` |
| Lab guide app sidebar: initials | `initials_for_lab_app` column |
| dbt profile: schema | `personal_schema` column (without the `TRICON_DE.` prefix) |

Also send them the lab guide link and ask them to complete **Getting Started** before lab day: install CoCo Desktop, Git, and `dbt-core` + `dbt-snowflake`, which usually need IT approval.
- **Option A** attendees sign in with their normal Tricon login (e.g. SSO). Nothing is stored and no token is created.
- **Option B/C** attendees sign in to Snowsight first with the one-time password, set a new password, and enroll in MFA. Then they use that login in CoCo Desktop. The Getting Started page has the dbt profile for password logins.

**Adding people later:** add them to section 0 and click Run All again. Existing attendees aren't affected.

---

## Optional extras (`03_optional.sql`): skip if unsure

The core lab doesn't need any of these.

| Block | Enables | Note |
|---|---|---|
| 3a. `TRICON_DE_REVIEWER` role | Lab modules A3 (access review) and A6 (warehouse right-sizing) on real account metadata | Read-only, but it can see all users, grants, logins, and query text. **Grant only to admins.** Without it, the facilitator demos A3/A6 |
| 3b. Email integration | Module A4 can email its report | Can only email the addresses you list |
| 3c. Adaptive demo warehouse | Facilitator demo of Adaptive Warehouses | Enterprise edition and supported regions only |

---

## After the lab: `99_teardown.sql`

Run it in a worksheet after hackathon week. It lists what it will remove, then drops **only** these exact names:
- `TRICON_DE`, including every personal schema
- `TRICON_DE_WH` and `TRICON_DE_ADAPTIVE_DEMO_WH`
- `TRICON_DE_MONITOR`
- `TRICON_DE_EMAIL_INT`
- `TRICON_DE_REVIEWER` and `TRICON_DE_ROLE`. Dropping a role removes it from every user

Similarly named objects (for example `TRICON_DEMO`) are never touched. `SNOWFLAKE_SAMPLE_DATA` is kept.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `STOP: existing ... was not created by this lab` | Something named `TRICON_DE*` already exists. Don't continue; contact the facilitator |
| `STOP: CORTEX_ENABLED_CROSS_REGION is DISABLED` | CoCo Desktop requires cross-region inference ([docs](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop)). Decide with your security team; the script never changes it |
| `STOP: fix the attendee list ... user not found` | Use the NAME column from Governance & security → Users & Roles, not the email. Or use `"NEW"` for people without a Snowflake user |
| Temporary-login (B) attendee can't sign in | They must change the one-time password and enroll in MFA on first login. If it's lost, drop the user (`DROP USER TRICON_DE_<INI>;`) and re-run the script to get a new password |
| Password login blocked for B/C users | Your account may only allow SSO through an authentication policy. Use option A (provision them in your identity provider) |
| Attendee can't pick `TRICON_DE_ROLE` in CoCo Desktop | Confirm their summary row says READY; have them sign out and back in |
| CoCo Desktop says access is blocked | `CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER` may be `0` in your account. Allow attendees: `ALTER USER "<name>" SET CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER = 20;` |
| `unknown model` in `05_verify.sql` | Pick any GA model from `SHOW CORTEX BASE MODELS IN SCHEMA SNOWFLAKE.MODELS` |
| Warehouse suspended mid-lab | The 40-credit weekly cap was hit. Raise `CREDIT_QUOTA` on `TRICON_DE_MONITOR` |
| A "should fail" check in `05_verify.sql` succeeded | Secondary roles were active. Run `USE SECONDARY ROLES NONE` and retry. If the resize ran, set it back: `ALTER WAREHOUSE TRICON_DE_WH SET WAREHOUSE_SIZE = 'SMALL';` |

**Questions:** Carson Walker, Snowflake (carson.walker@snowflake.com)
