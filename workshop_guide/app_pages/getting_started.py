import streamlit as st

from components import attendee_schema, render_code, render_guide_change, render_guide_change, render_new_for_tricon

st.title("Getting Started")
st.markdown("Install the tools, clone the starter project, and connect dbt and CoCo Desktop to Tricon's Snowflake account. **Do this before the lab** — installs often need IT approval.")

st.space("small")

render_guide_change(
    "Fork `Snowflake-Labs/sfguide-data-engineering-with-coco`, run `scripts/setup.sql` yourself (creates `DEMO_ROLE`/`DEMO_WH`/`DEMO_DB`), create a PAT, and bypass the network policy.",
    "Clone `coco-hol-tricon-de` (same `dbt/` starter). Tricon's admin pre-provisions `TRICON_DE_*` via `admin/ADMIN_GUIDE.md`. dbt signs in with **SSO**, and each attendee gets their own `DBT_<INITIALS>` schema.",
    "Customer account: least privilege, no stored secrets, no network-policy changes, and no collisions between attendees.")

st.markdown("#### Step 1: Install the tools")
with st.container(border=True):
    st.markdown("""
| Tool | Install |
|------|---------|
| **CoCo Desktop** | [Installation guide](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop/onboarding-and-authentication) |
| **Git** | Usually already installed; check with `git --version` |
| **dbt Core + Snowflake adapter** | `python -m pip install dbt-core dbt-snowflake` ([dbt docs](https://docs.getdbt.com/docs/core/installation-overview)) |
| **GitHub account** | Only needed for Module 4 (CI/CD) |
""")

st.space("small")

st.markdown("#### Step 2: Clone the starter project")
with st.container(border=True):
    st.markdown("The starter has a dbt project over `SNOWFLAKE_SAMPLE_DATA.TPCH_SF1` with two models, plus a synthetic resident-contacts seed for the classification workflow.")
    render_code("""git clone https://github.com/sfc-gh-cwalker/coco-hol-tricon-de.git
cd coco-hol-tricon-de""")
    st.markdown("""
In CoCo Desktop, use **File → Open Folder** to open `coco-hol-tricon-de` and choose **Trust** when prompted. Opening the folder lets CoCo read your files and run commands in the right place.

:material/info: For Module 4 (CI/CD), fork the repo on GitHub instead and clone your fork.
""")

st.space("small")

st.markdown("#### Step 3: Connect CoCo Desktop")
with st.container(border=True):
    st.markdown("""
Your admin sent you a row from the setup summary. Your **login type** tells you how to sign in:

| Login type | How you sign in |
|---|---|
| **A) existing user** | Your normal Tricon Snowflake login (e.g. SSO). Nothing new to set up |
| **B) temporary lab login** (`TRICON_DE_<INITIALS>`) | **First**, sign in to Snowsight with the one-time password. Set a new password and enroll in MFA when prompted. Then use that login below |
| **C) shared lab login** | Same as B, with the shared login. Agree who holds the MFA device |

Add a Snowflake connection in CoCo Desktop with these values:

| Setting | Value |
|---------|-------|
| **Account** | `account_identifier` from your admin |
| **User** | `snowflake_login` from your admin |
| **Role** | `TRICON_DE_ROLE` |
| **Warehouse** | `TRICON_DE_WH` |
| **Database** | `TRICON_DE` |
""")

st.space("small")

st.markdown("#### Step 4: Enter your initials and configure dbt")
with st.container(border=True):
    st.markdown(f"""
Type your initials in the **sidebar** and press Enter. Your dbt schema becomes **`TRICON_DE.{attendee_schema()}`**, so attendees don't overwrite each other's models.

Copy the profile into `~/.dbt/profiles.yml`. If that file already exists, add the `tricon_de` block next to your other profiles.
""")
    render_code("""mkdir -p ~/.dbt
cp dbt/profiles.yml.example ~/.dbt/profiles.yml   # or merge the tricon_de block by hand""")
    st.markdown("Then replace the placeholders:")
    render_code("""tricon_de:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "<TRICON_ACCOUNT_IDENTIFIER>"
      user: "<YOUR_SNOWFLAKE_USERNAME>"
      authenticator: externalbrowser
      role: TRICON_DE_ROLE
      database: TRICON_DE
      warehouse: TRICON_DE_WH
      schema: DBT_<INITIALS>
      threads: 4""", language="yaml")
    st.info(":material/lock: **No password or token is stored.** `authenticator: externalbrowser` signs you in with Tricon SSO in a browser pop-up. The original guide uses a Personal Access Token plus a temporary network-policy bypass; we don't do that on a customer account.")
    with st.expander("Login type B or C (temporary or shared lab login)? Use this profile instead"):
        st.markdown("`externalbrowser` only works with SSO. For a password login, read the password from an environment variable so it's never written in a file, and approve the MFA prompt when dbt connects:")
        render_code("""tricon_de:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "<TRICON_ACCOUNT_IDENTIFIER>"
      user: "TRICON_DE_<INITIALS>"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      authenticator: username_password_mfa
      role: TRICON_DE_ROLE
      database: TRICON_DE
      warehouse: TRICON_DE_WH
      schema: DBT_<INITIALS>
      threads: 4""", language="yaml")
        render_code("""export SNOWFLAKE_PASSWORD='<your new password>'    # macOS/Linux, current terminal only
# Windows PowerShell:  $env:SNOWFLAKE_PASSWORD='<your new password>'""")
        st.caption("If the MFA prompt doesn't work from dbt, ask the facilitator. Everything else in the lab works from CoCo Desktop.")

st.space("small")

st.markdown("#### Step 5: Verify")
with st.container(border=True):
    st.markdown("In a CoCo Desktop terminal (**Terminal → New Terminal**):")
    render_code("dbt debug --project-dir dbt/")
    st.markdown("You should see `All checks passed!`. Then seed the synthetic data used later in Module A2:")
    render_code("dbt seed --project-dir dbt/")

st.space("small")

st.markdown("#### Step 6: Ask CoCo to check your lab area")
with st.container(border=True):
    st.markdown("Your admin pre-created your personal schema. Paste this into the CoCo Desktop chat to confirm everything works:")
    render_code("""Check my lab setup. Use role TRICON_DE_ROLE and warehouse TRICON_DE_WH, and run these one at a time:
1. SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();
2. SHOW SCHEMAS LIKE 'DBT_<INITIALS>' IN DATABASE TRICON_DE;
3. SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS;   -- expect 1500000
4. SELECT COUNT(*) FROM TRICON_DE.DBT_<INITIALS>.RESIDENT_CONTACTS;   -- expect 40 after dbt seed
Give me a PASS/FAIL table. Do not create, change, or drop anything.""", language="text")
    st.caption("Any FAIL? Send the table to your admin. Common fixes are in the admin guide's Troubleshooting section.")
