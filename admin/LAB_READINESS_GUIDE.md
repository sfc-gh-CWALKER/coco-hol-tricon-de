# Lab Readiness Guide: "Data Engineering with CoCo" at Tricon

**Audience:** Tricon's Snowflake admin, Tricon IT (laptops), and anyone running a dry run (e.g. Jeremiah Hansen).
**Goal:** every attendee can run the dbt HOL end to end (Getting Started → Modules 1–3, optional 4) on **Tricon's own Snowflake account**, with nothing left to chance on lab day.
**Lab guide app:** https://coco-hol-tricon-de-gejm3sg47ufychnq9jpkqg.streamlit.app/
**Repo:** https://github.com/sfc-gh-cwalker/coco-hol-tricon-de (public, read-only for attendees)
**Original guide (Part 1 source):** [Data Engineering with CoCo](https://www.snowflake.com/en/developers/guides/data-engineering-with-coco/) by Jeremiah Hansen

---

## The short version

| # | Who | What | When | Time |
|---|---|---|---|---|
| A1 | Tricon admin | Run `admin/00_readiness_check.sql` (read-only) and resolve any **FAIL** | 2+ weeks before | 10 min |
| A2 | Tricon admin | Fill in the attendee list and run `admin/tricon_de_lab_setup.sql` | 1–2 weeks before | 15 min |
| A3 | Tricon admin | Run `admin/05_verify.sql`, then send each attendee their row | Same day as A2 | 5 min |
| B1 | Tricon IT | Approve and install CoCo Desktop, Git, uv + dbt on every laptop | 1–2 weeks before | varies |
| C1 | Each attendee | Complete the app's **Getting Started** page (ends with a 6-row PASS check) | By 3 days before | 30 min |
| D1 | Dry-run tester | Run Part E below on a **real Tricon laptop + Tricon login** | 1 week before | 75 min |
| E1 | Facilitator | Review the attendee PASS checks; chase anyone missing | 2 days before | 15 min |

If every row is done, lab day is only Modules 1–3. Nobody installs or configures anything that day.

---

## Part A: Tricon's Snowflake account (admin)

### A1. Readiness check: read-only, run first

Snowsight → **Projects → Worksheets → + SQL Worksheet** → paste `admin/00_readiness_check.sql` → choose any warehouse → **Run All**. It **changes nothing** and returns one table:

| # | Check | Lab impact if not met | What a FAIL/WARN means |
|---|---|---|---|
| 1 | `CORTEX_ENABLED_CROSS_REGION` not `DISABLED` | **Blocker.** CoCo Desktop does not work | Security-team decision. The setup script stops on this and never changes it |
| 2 | `CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER` not `0` | **Blocker.** CoCo Desktop is switched off | Set per attendee: `ALTER USER "<name>" SET CORTEX_CODE_DESKTOP_DAILY_EST_CREDIT_LIMIT_PER_USER = 20;` |
| 3 | `CORTEX_MODELS_ALLOWLIST` | **Blocker if `NONE`**. WARN if restricted | CoCo and `AI_COMPLETE('claude-sonnet-4-5')` need their models allowed |
| 4 | `SNOWFLAKE$LOCAL_APPLICATION` enabled | WARN. Attendees use fallback sign-ins | This built-in integration powers the recommended **Local OAuth** browser sign-in for CoCo Desktop *and* dbt. It's rolling out to all accounts |
| 5 | SAML (SSO) integration | Info | Decides which sign-in SSO users choose |
| 6 | Account network policy | WARN | Every attendee laptop (incl. the India team) must reach Snowflake from an allowed network or VPN |
| 7 | Authentication policies | WARN | If one applies to attendees, it must allow client type **DRIVERS** (CoCo Desktop and dbt) and method **OAUTH**, plus **PASSWORD** for temporary lab logins |
| 8 | `SNOWFLAKE_SAMPLE_DATA` | Info | Setup adds it from Snowflake's free share if missing |
| 9 | No `TRICON_DE*` name conflicts | **Blocker** | Something named like the lab already exists: contact the facilitator |
| 10 | Sign-in caching (`ALLOW_ID_TOKEN`, `ALLOW_CLIENT_MFA_CACHING`) | WARN | Only matters if #4 isn't PASS: without caching, SSO users get a browser pop-up and password users an MFA push on **every** dbt command CoCo runs |
| 11 | Account identifier and region | Info | The `account_identifier` attendees type in |

**Not checkable with SQL, confirm yourself:**
- **Edition:** Module A2 (classification and masking) needs Enterprise or higher. Part 1 (Modules 1–4) works on any edition.
- **Personal databases** are enabled, if you want Module 4 Option A (Plugins Catalog). Otherwise the facilitator demos it.
- **Optional, recommended if #4 is PASS:** lengthen the Local OAuth access token so attendees sign in about once an hour instead of every 10 minutes:
  ```sql
  USE ROLE SECURITYADMIN;
  ALTER SECURITY INTEGRATION SNOWFLAKE$LOCAL_APPLICATION SET OAUTH_ACCESS_TOKEN_VALIDITY = 3600;
  ```

### A2. Setup script

Follow `admin/ADMIN_GUIDE.md`, Steps 1–2: edit **section 0 only** of `admin/tricon_de_lab_setup.sql` (one line per attendee, **including yourself and the dry-run tester**), then **Run All**.

What attendees end up with, and nothing more:

| Object | Purpose | Attendee privileges |
|---|---|---|
| `TRICON_DE_ROLE` | The only role attendees use | Granted to each attendee; their default role is unchanged |
| `TRICON_DE_WH` (Small, 60 s auto-suspend) | Lab compute | USAGE, OPERATE (cannot resize) |
| `TRICON_DE_MONITOR` | Hard stop at 40 credits/week on the lab warehouse only | — |
| `TRICON_DE` database | One personal schema per attendee: `TRICON_DE.DBT_<INITIALS>` | USAGE, CREATE SCHEMA; owns the schemas |
| `SNOWFLAKE_SAMPLE_DATA` | TPC-H source data for the dbt project | IMPORTED PRIVILEGES (read-only) |
| `SNOWFLAKE.CORTEX_USER` | CoCo Desktop, `AI_COMPLETE`, Cortex Analyst | Database role |
| `TRICON_DE_<INI>` users | **Only** for people marked `"NEW"` (no Snowflake user today) | Lab role only, no secondary roles, must change password and enroll MFA, expire after 30 days |

**Data exposure:** none. The lab never reads Tricon data. It uses TPC-H sample data and a 40-row **synthetic** CSV (fake names, `@example.com`). All attendees share one role, so an attendee *could* write to a neighbour's `DBT_*` schema. `AGENTS.md` (Module 1) tells CoCo to stay in its own schema. That's fine for a sandbox; production would use a role per schema.

### A3. Verify and send rows

1. Run `admin/05_verify.sql`. Every check should pass, and the two "should fail" checks must fail with *insufficient privileges*.
2. Download the lab user list (the last result of the setup script) as CSV.
3. Send **each attendee only their own row**, plus the lab app link. The row contains: `initials`, `username`, `login_type`, `account_identifier`, `login_url`, and, for temporary logins, `temporary_password`.
4. Ask them to finish **Getting Started** by a set date and reply with their Step 7 PASS table.

---

## Part B: attendee laptops (Tricon IT)

Every item below is something an attendee would otherwise discover on lab day.

| Item | Required for | macOS | Windows | Notes for IT |
|---|---|---|---|---|
| **CoCo Desktop** (latest) | Everything | [Download](https://www.snowflake.com/en/product/snowflake-coco/downloads/) | **User installer** (no admin rights) or System installer for managed fleets | Auto-updates. Allow it through endpoint security |
| **Git** | Clone (Getting Started), commits (Modules 1–3) | `git --version` triggers Apple's installer | [Git for Windows](https://git-scm.com/download/win) with defaults | **Windows: must include Git Bash.** The Module 3 hook runs with `bash` |
| **uv** | Installing dbt reliably | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `irm https://astral.sh/uv/install.ps1 \| iex` | Installs to the user profile, no admin rights. Brings its own Python, so system Python doesn't matter |
| **dbt Core ≥ 1.10 + dbt-snowflake** | Modules 1–3 | `uv tool install --python 3.12 dbt-core --with dbt-snowflake` | same | Tested with dbt-core 1.12.6 / dbt-snowflake 1.12.4. **≥ 1.10 is required**: the tests use the `arguments:` syntax |
| A default web browser | Snowflake sign-in for CoCo Desktop and dbt | — | — | Sign-in redirects to `http://127.0.0.1:<port>` on the laptop. Endpoint tools must not block localhost redirects |

**Network access the laptops need** (on the network attendees will use on lab day, including VPN):

| Destination | Why |
|---|---|
| `https://app.snowflake.com` and `https://<account_identifier>.snowflakecomputing.com` | Snowsight, CoCo Desktop, dbt |
| `https://github.com` (read) | `git clone` of the lab repo |
| `https://astral.sh`, `https://github.com` (uv releases), `https://pypi.org`, `https://files.pythonhosted.org` | Installing uv and dbt (install time only) |
| `https://coco-hol-tricon-de-gejm3sg47ufychnq9jpkqg.streamlit.app` | The lab guide |
| Allowed by the Snowflake network policy (Part A, check 6) | Otherwise sign-in fails with *IP not allowed* |

**If IT can't allow uv:** any Python 3.10–3.13 works: `python3 -m pip install --user dbt-core dbt-snowflake` (macOS's built-in Python 3.9 is **too old**). Windows: `py -3.12 -m pip install dbt-core dbt-snowflake`. Confirm `dbt --version` shows the **snowflake** plugin.

**If GitHub is blocked:** give attendees a ZIP of the repo. They must then run `git init && git add -A && git commit -m start` in the folder, because Module 3 relies on Git history.

---

## Part C: what each attendee does before lab day

All of this is on the app's **Getting Started** page, with copy-ready commands, expected results, and fixes for each step:

| Step | What | Done when |
|---|---|---|
| 0 | Fill in the app sidebar from their admin row (initials, sign-in type, username, account) | Sidebar shows a green "Every command and prompt now uses ..." box |
| 1 | Sign in to Snowsight once (temporary logins: change password, set up MFA) | Role picker lists `TRICON_DE_ROLE` |
| 2 | Install CoCo Desktop, Git, uv, dbt | `dbt --version` shows Core ≥ 1.10 and the snowflake plugin |
| 3 | Clone the repo; set Git name and email | Folder `coco-hol-tricon-de` exists |
| 4 | Connect CoCo Desktop (Local OAuth), pick role and warehouse, open the folder, **Trust** it | Top bar shows `TRICON_DE_ROLE` |
| 5 | Paste the generated command that writes `profiles.yml` into the **project folder** | File printed back with their username and schema |
| 6 | `dbt debug`, then `dbt seed` | `All checks passed!`, then `INSERT 40` |
| 7 | Paste the read-only self-check prompt into CoCo | 6 PASS rows. **They send this table to the facilitator** |

Design choices that remove common failures:
- **The dbt profile lives in the project folder**, generated by the app from the sidebar. Attendees never edit YAML by hand, and an existing `~/.dbt/profiles.yml` is never overwritten. The file is git-ignored.
- **No secrets anywhere.** Local OAuth signs in through the browser. Fallbacks: `externalbrowser` (SSO) or `username_password_mfa` with the password read from an environment variable.
- **Sidebar values are kept in the page URL.** A refresh or a bookmarked link keeps them. Only non-secret values are stored.

---

## Part D: what can still go wrong, and how the lab handles it

| Risk | Where | How it's handled |
|---|---|---|
| CoCo blocked by an account setting | Part A | Readiness checks 1–3 catch it before setup |
| Wrong username, account, or initials | Getting Started | Sidebar drives every command; dbt errors are mapped to fixes on the page |
| dbt install fails (old Python, PATH) | Getting Started, Step 2 | uv brings its own Python; Fixes box covers PATH and proxy issues |
| Existing `~/.dbt/profiles.yml` overwritten | Getting Started, Step 5 | Not touched: the profile is written to the project folder |
| Repeated sign-in prompts on every dbt command | Modules 1–3 | Local OAuth (cached token); optional 60-minute token (A1); readiness check 10 explains the fallback trade-off |
| `git commit` fails (*Please tell me who you are*) | Module 1 checkpoint | Git identity is set in Getting Started, Step 3 |
| `accepted_values` test fails on `order_status = P` | Module 2 | Expected result and fix on the page (TPC-H has F, O, P) |
| `rm -rf .snowflake/` run from the home folder deletes Snowflake connections | Module 3, Step 1 | **Replaced** with a folder guard and removing only empty folders |
| Hook relies on `jq`/`python3` and silently allows everything | Module 3, Prompt 3.2 | Prompt asks for bash + grep only; a direct hook test shows **exit code 2**; the reference hook in `solutions/` works without Python |
| CoCo refuses `--target prod` before the hook fires | Module 3, Prompt 3.4 | Explained as a pass (AGENTS.md layer); the direct hook test proves the hook layer |
| dbt-review finds no changes | Module 3, Prompt 3.5 | Branch checkpoints in Modules 1–2; recovery commands on the page |
| Windows-specific commands | Getting Started, Modules 2–3 | PowerShell tabs for every terminal block; Git Bash for the hook test |
| Plugin not detected | Module 3, Step 4 | Trust, refresh, and path checks; reference manifest in `solutions/` |
| Module 4 needs credentials Tricon hasn't approved | Module 4 | Marked optional; Option B is facilitator demo unless a CI service user exists |

---

## Part E: end-to-end dry run (for Jeremiah or any tester)

Run this on **a Tricon-managed laptop** with **a Tricon login**: one existing user (login type A) and, ideally, one temporary lab login (type B). This is the only way to catch laptop, network, and policy issues. Allow about 75 minutes. Tick each box.

**Prerequisites:** the admin has run Parts A1–A3 with your user in the list, and you have your row.

### E1. Getting Started (≈ 25 min)
- [ ] App sidebar filled in; green box shows your username and `TRICON_DE.DBT_<INI>`
- [ ] Step 1: Snowsight sign-in works; `TRICON_DE_ROLE` is listed (type B: password change and MFA enrolment work)
- [ ] Step 2: `dbt --version` → Core ≥ 1.10, plugin snowflake
- [ ] Step 3: clone works on the Tricon network/VPN
- [ ] Step 4: CoCo Desktop connects with **Local OAuth**; role `TRICON_DE_ROLE`, warehouse `TRICON_DE_WH`; folder opened and trusted
- [ ] Step 5: generated `profiles.yml` in the project folder; `git status` does **not** list it
- [ ] Step 6: `dbt debug` → *All checks passed!* (browser sign-in once); `dbt seed` → `INSERT 40`
- [ ] Step 6, again: run `dbt debug` a second time. **Note whether the browser opens again.** If it does every time, record the readiness check row 10 result
- [ ] Step 7: CoCo self-check returns 6 PASS

### E2. Module 1: AGENTS.md (≈ 15 min)
- [ ] Prompt 1.1 creates `AGENTS.md` at the root containing your `DBT_<INI>`
- [ ] Prompt 1.2 rewrites `orders_summary.sql` to `source('tpch', 'orders')` and `source('tpch', 'lineitem')`
- [ ] Prompt 1.3 → `PASS=3` (customers 150,000 rows; orders_summary 1,500,000)
- [ ] Checkpoint: branch `feature/add-tricon-de-plugin` created and committed

### E3. Module 2: tests and a skill (≈ 20 min)
- [ ] Prompt 2.1 creates `dbt/models/_schema.yml`; all tests PASS (if `order_status` fails, the Fixes box resolves it)
- [ ] Prompt 2.2 creates `.snowflake/cortex/skills/new-dbt-model/SKILL.md`
- [ ] Prompt 2.3: CoCo says it is using **new-dbt-model**; `supplier_performance` builds; `supplier_key` tests PASS
- [ ] Checkpoint committed

### E4. Module 3: plugin, hook, subagent (≈ 25 min)
- [ ] Step 1 commands move the skill; `ls -d .snowflake` → *No such file or directory*
- [ ] Prompts 3.1–3.3 create `plugin.json`, `activation.md`, `hooks.json`, `validate-bash.sh`, `dbt-review.md`
- [ ] Settings → Plugins shows `tricon-de` **on**, with 1 skill, 1 agent, 1 hook
- [ ] Direct hook test: prod → *Blocked...* and **exit code: 2**; dev → **exit code: 0** (Windows: in Git Bash)
- [ ] Prompt 3.4: hook blocks it, **or** CoCo declines citing AGENTS.md (record which)
- [ ] Commit, then Prompt 3.5: dbt-review lists `orders_summary` and `supplier_performance`, ends with overall **PASS**

### E5. Module 4 (optional, ≈ 10 min)
- [ ] Option A: Publish to Plugins Catalog returns a `snow://skill_catalog/...` link (if it fails: record the error; personal databases may be disabled)
- [ ] Option B: skip unless Tricon has approved a CI service user

### E6. Report back
Send the facilitator:
- the ticked checklist, with notes on anything that needed a fix;
- the readiness check table (A1);
- whether dbt prompted for sign-in more than once (E1);
- the outcome of Prompt 3.4 (hook vs. AGENTS.md);
- laptop OS and version, CoCo Desktop version (*Help → About*), and `dbt --version` output.

### Tested by Snowflake before release
On a Snowflake demo account, using a temporary lab login (lab role only, no secondary roles):
- the readiness check, setup, verify, and teardown scripts;
- `dbt debug`, `seed`, and `build` with the exact project-root `profiles.yml` the app generates;
- the uv install (dbt-core 1.12.6 / dbt-snowflake 1.12.4);
- the Module 1 fix (PASS=3) and Module 2 tests (PASS=11), and the A1 failing test (fails on `P` as intended);
- the Module 3 command sequence: the safe skill move, the direct hook test (2 / 0, including without Python), the dbt-review diff, and per-model builds;
- the A2 classification and masking, the A4 semantic view, the A5 numbers, and `AI_COMPLETE`.

**Not testable from a script, so covered by this dry run:** CoCo Desktop's own responses to each prompt, browser sign-in (Local OAuth) from dbt on a Tricon laptop, Tricon's network and authentication policies, and Windows laptops.

---

## Part F: lab day (facilitator)

- Before starting, confirm everyone sent a Step 7 PASS table. Pair anyone who didn't with someone who did.
- Keep `TRICON_DE_MONITOR` in mind. 40 credits/week is ample for ~15 people. Raise it if needed: `ALTER RESOURCE MONITOR TRICON_DE_MONITOR SET CREDIT_QUOTA = 80;`
- The app's **Help & Troubleshooting** page lists every known symptom. Reference answers are in `solutions/tricon-de-plugin/`.
- Afterwards, the teardown is `admin/99_teardown.sql` (or section 6 of the setup script).

**Contact:** Carson Walker, Snowflake (carson.walker@snowflake.com)
