import streamlit as st

from components import (
    attendee_schema,
    attendee_user,
    profiles_yml,
    render_code,
    render_expected,
    render_guide_change,
    render_troubleshoot,
    setup_complete,
    uses_temp_login,
)

st.title("Getting Started")
st.markdown("""
Finish this page **before lab day**: installs often need IT approval, and first sign-in takes a few minutes.
Work top to bottom. Every step says what you should see; if you see something else, open the **Fixes** box under it.
""")

render_guide_change(
    "Fork `Snowflake-Labs/sfguide-data-engineering-with-coco`, run `scripts/setup.sql` yourself (creates `DEMO_ROLE`/`DEMO_WH`/`DEMO_DB`), create a Personal Access Token, and bypass the network policy.",
    "Clone `coco-hol-tricon-de` (same `dbt/` starter). Tricon's admin pre-provisions everything. dbt and CoCo Desktop sign in through the **browser** (no password or token stored), and each attendee gets their own `DBT_<INITIALS>` schema.",
    "Customer account: least privilege, no stored secrets, no network-policy changes, and no collisions between attendees.")

if not setup_complete():
    st.warning("**First, fill in the four boxes in the sidebar** (initials, how you sign in, username, account identifier) from the row your admin sent you. Every command below then fills itself in.", icon=":material/arrow_back:")

# ---------------------------------------------------------------- Step 0
st.markdown("#### Step 0: What you need from your admin")
with st.container(border=True):
    st.markdown("""
Your admin ran the lab setup and sent you **one row** from the lab user list. You need these columns:

| Column | Example | Goes into |
|---|---|---|
| `initials` | `CW` | Sidebar → *Your initials* |
| `username` | `JSMITH` or `TRICON_DE_CW` | Sidebar → *Snowflake username* |
| `login_type` | `A) existing user` or `B) new lab login` | Sidebar → *How do you sign in* |
| `account_identifier` | `tricon-prod` | Sidebar → *Account identifier* |
| `login_url`, `temporary_password` | B/C only | Step 1 below |

No row yet? Ask your admin. Don't guess the initials: they must match the schema the admin created for you.
""")

# ---------------------------------------------------------------- Step 1
st.markdown("#### Step 1: Sign in to Snowflake once in a browser")
with st.container(border=True):
    if uses_temp_login():
        st.markdown(f"""
1. Open the **`login_url`** from your admin.
2. Username **`{attendee_user()}`**, password: the **`temporary_password`** from your row.
3. Snowflake asks you to **choose your own new password**. Write it in your password manager.
4. Snowflake asks you to **set up MFA** (e.g. Duo Mobile on your phone). Finish it.
""")
        render_expected("Snowsight opens and the role picker (bottom left, under your name) shows **TRICON_DE_ROLE**.")
        render_troubleshoot([
            ("*Incorrect username or password*", "Check the username is `TRICON_DE_<your initials>`. If you already changed the password and forgot it, ask your admin to reset it (one SQL line in their guide)."),
            ("*Your user is locked / disabled / expired*", "Lab logins expire after 30 days. Ask your admin to re-run the setup script."),
            ("Page won't load or *IP not allowed*", "Tricon's network policy blocks your network. Connect to the Tricon VPN and try again."),
            ("No MFA prompt on your phone", "Open the authenticator app manually; you can also choose *passcode* and type the 6-digit code."),
        ])
    else:
        st.markdown("""
Open your usual Snowflake URL and sign in as you normally do (e.g. Tricon SSO). Then click your name (bottom left) → **Switch role**.
""")
        render_expected("**TRICON_DE_ROLE** is in the role list. You don't need to switch to it here.")
        render_troubleshoot([
            ("TRICON_DE_ROLE isn't listed", "Your admin hasn't added you yet, or used a different username. Send them your username from Snowsight (your name → *Profile*)."),
            ("*IP not allowed*", "Connect to the Tricon VPN and try again."),
        ])

# ---------------------------------------------------------------- Step 2
st.markdown("#### Step 2: Install the tools")
with st.container(border=True):
    st.markdown("""
| Tool | Why | Install |
|---|---|---|
| **CoCo Desktop** | The AI coding agent you'll use all day | [Download](https://www.snowflake.com/en/product/snowflake-coco/downloads/) · Windows: choose the **User installer** (no admin rights needed) |
| **Git** | Clone the project; Module 3 commits | macOS: run `git --version` (it offers to install). Windows: [Git for Windows](https://git-scm.com/download/win), keep the defaults (includes **Git Bash**, needed for the Module 3 hook) |
| **uv** | Installs dbt with its own Python, so your system Python doesn't matter | See the commands below |
| **dbt Core + dbt-snowflake** | Builds the models | See the commands below |
""")
    st.markdown("**Install uv, then dbt.** Run these in a normal terminal (macOS: *Terminal*; Windows: *PowerShell*), one block at a time:")
    tab_mac, tab_win = st.tabs(["macOS", "Windows (PowerShell)"])
    with tab_mac:
        render_code("""curl -LsSf https://astral.sh/uv/install.sh | sh
# close and reopen the terminal, then:
uv tool install --python 3.12 dbt-core --with dbt-snowflake
dbt --version""")
    with tab_win:
        render_code("""powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# close and reopen PowerShell, then:
uv tool install --python 3.12 dbt-core --with dbt-snowflake
dbt --version""", language="powershell")
    render_expected("`dbt --version` lists **Core: installed 1.10 or newer** and **Plugins: snowflake**.")
    render_troubleshoot([
        ("`dbt: command not found` / *not recognized*", "Close **all** terminals (and CoCo Desktop) and reopen them. Still missing? Run `uv tool update-shell`, then reopen."),
        ("`curl`/`irm` blocked, or uv install refused", "IT may block installers. Alternative with any Python 3.10–3.13: `python3 -m pip install --user dbt-core dbt-snowflake` (Windows: `py -3.12 -m pip install dbt-core dbt-snowflake`). Don't use macOS's built-in Python 3.9."),
        ("`dbt --version` shows no **snowflake** plugin", "`uv tool install --force --python 3.12 dbt-core --with dbt-snowflake`"),
        ("Corporate proxy / SSL errors during install", "Ask IT for the proxy settings, or install dbt from IT's software portal."),
    ])

# ---------------------------------------------------------------- Step 3
st.markdown("#### Step 3: Clone the project and tell Git who you are")
with st.container(border=True):
    render_code("""git clone https://github.com/sfc-gh-cwalker/coco-hol-tricon-de.git
cd coco-hol-tricon-de
git config --global user.name  >/dev/null || git config --global user.name  "Your Name"
git config --global user.email >/dev/null || git config --global user.email "you@triconresidential.com\"""")
    st.caption("The two `git config` lines only set your name and email if Git doesn't have them yet. Module 3 makes a commit, which fails without them. Windows PowerShell: run `git config --global user.name \"Your Name\"` and `git config --global user.email \"you@triconresidential.com\"` instead.")
    render_expected("A new `coco-hol-tricon-de` folder containing `dbt/`, `admin/`, `solutions/` and `workshop_guide/`.")
    render_troubleshoot([
        ("*Could not resolve host github.com* or a timeout", "GitHub is blocked on your network. Ask the facilitator for a ZIP, or try off VPN. With a ZIP, also run `git init && git add -A && git commit -m start` inside the folder (Module 3 needs Git)."),
        ("*destination path already exists*", "You cloned before. Use the existing folder, or `cd coco-hol-tricon-de && git pull`."),
    ])
    st.info(":material/info: Module 4 (CI/CD, optional) needs your own fork on GitHub. Skip it unless the facilitator says otherwise.")

# ---------------------------------------------------------------- Step 4
st.markdown("#### Step 4: Open the project in CoCo Desktop and connect to Snowflake")
with st.container(border=True):
    st.markdown(f"""
1. Launch CoCo Desktop. If it shows the setup flow, click **Add connection**; otherwise click the connection name at the top → **Manage Snowflake Connections** → **Add Connection**.
2. Fill in:

| Field | Value |
|---|---|
| Account identifier | `{st.session_state.get('sf_account') or '<account_identifier from your admin>'}` |
| Username | `{attendee_user()}` |
| Authentication method | **Local OAuth (recommended)** · if your admin says it isn't available: **External browser** for SSO users, **Password** for temporary lab logins |

3. Click **Sign in** and finish signing in in the browser.
4. Click the connection name at the top → **Change Role** → **TRICON_DE_ROLE**. Then → **Default Warehouse** → **TRICON_DE_WH**.
5. **File → Open Folder** → choose the `coco-hol-tricon-de` folder → **Trust** when asked. (Plugins and hooks only work in a trusted folder.)
""")
    render_expected("The top bar shows your connection with role **TRICON_DE_ROLE**, and the Explorer shows `dbt/`, `admin/`, `solutions/`.")
    render_troubleshoot([
        ("*Account not found*", "Copy the account identifier exactly from your admin's row (`orgname-accountname`, with a hyphen)."),
        ("Browser didn't open", "Click **Browser didn't open?** in CoCo Desktop and open the link yourself."),
        ("*Access blocked* / CoCo won't chat", "Your admin's readiness check covers this (CoCo Desktop credit limit). Send them the message."),
        ("TRICON_DE_ROLE missing in Change Role", "Sign out and back in. Still missing: your admin hasn't granted it to this username."),
        ("You opened the wrong folder", "**File → Open Folder** again. The folder must contain `dbt/` directly."),
    ])

# ---------------------------------------------------------------- Step 5
st.markdown("#### Step 5: Create your dbt profile (one command)")
with st.container(border=True):
    st.markdown(f"""
In CoCo Desktop open a terminal (**Terminal → New Terminal**). It opens in the project folder. Paste this whole block: it writes **`profiles.yml` into the project folder**, which dbt reads first. Your `~/.dbt/profiles.yml` is never touched, and the file is git-ignored, so it can't be committed.
""")
    if not setup_complete():
        st.error("Fill in the sidebar first. Otherwise the file will contain placeholders and dbt will fail.", icon=":material/error:")
    yml = profiles_yml("oauth_authorization_code")
    tab_sh, tab_ps = st.tabs(["macOS / Git Bash", "Windows PowerShell"])
    with tab_sh:
        render_code("cat > profiles.yml <<'EOF'\n" + yml + "EOF\ncat profiles.yml")
    with tab_ps:
        render_code("@'\n" + yml + "'@ | Set-Content -Encoding ascii profiles.yml\nGet-Content profiles.yml", language="powershell")
    st.download_button("Or download profiles.yml (save it in the coco-hol-tricon-de folder)", yml, file_name="profiles.yml", icon=":material/download:")
    render_expected(f"`profiles.yml` printed back with **user: {attendee_user()}** and **schema: {attendee_schema()}**, and no `<...>` placeholders left.")
    with st.expander(":material/key: Local OAuth isn't available on Tricon's account? Use one of these instead"):
        st.markdown("Your admin's readiness check tells you. Replace the `authenticator:` line:")
        st.markdown("**SSO users (login type A):**")
        render_code("      authenticator: externalbrowser", language="yaml")
        st.markdown("**Temporary lab logins (B/C):** keep the password out of the file. Set it in the terminal each time you open one, and approve the MFA push:")
        render_code("""      authenticator: username_password_mfa
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}\"""", language="yaml")
        render_code("""export SNOWFLAKE_PASSWORD='<your new password>'        # macOS / Git Bash
$env:SNOWFLAKE_PASSWORD='<your new password>'          # Windows PowerShell""")
        st.caption("Without sign-in caching on the account, these two methods ask again on every dbt command. Local OAuth asks about every 10–60 minutes.")

# ---------------------------------------------------------------- Step 6
st.markdown("#### Step 6: Test dbt and load the lab data")
with st.container(border=True):
    st.markdown("In the same terminal:")
    render_code("dbt debug --project-dir dbt/")
    st.caption("A browser tab opens the first time: sign in, then come back.")
    render_expected("`Connection test: [OK connection ok]` and **`All checks passed!`**")
    render_code("dbt seed --project-dir dbt/")
    render_expected(f"`1 of 1 OK loaded seed file {attendee_schema()}.resident_contacts ... [INSERT 40]` and `Done. PASS=1`.")
    render_troubleshoot([
        ("`Could not find profile named 'tricon_de'`", "You're not in the project folder, or `profiles.yml` wasn't written. Run `pwd` (should end in `coco-hol-tricon-de`) and redo Step 5."),
        ("`account ... <TRICON_ACCOUNT_IDENTIFIER>` or other `<...>` in the error", "The sidebar wasn't filled in when you copied Step 5. Fill it in and redo Step 5."),
        ("*Incorrect username or password* / *invalid OAuth*", "Check `user:` in `profiles.yml` matches your username exactly. Temporary lab logins must finish Step 1 first."),
        ("*Role 'TRICON_DE_ROLE' specified in the connect string is not granted*", "Your admin's list has a different username for you, or you haven't been added."),
        ("*Schema 'DBT_..' does not exist or not authorized*", "Your initials don't match your admin's list. Fix them in the sidebar and redo Step 5."),
        ("Browser opens, then *the redirect URI is invalid* or the sign-in hangs", "Use the fallback authenticator from the Step 5 box."),
        ("`No module named 'dbt'` / wrong dbt", "Run `which dbt` (Windows: `where dbt`). It should point to a `uv` folder. Redo Step 2."),
    ])

# ---------------------------------------------------------------- Step 7
st.markdown("#### Step 7: Ask CoCo to check everything")
with st.container(border=True):
    st.markdown("Paste this into the CoCo Desktop chat. It only reads; it changes nothing.")
    render_code("""Check my lab setup. Use role TRICON_DE_ROLE and warehouse TRICON_DE_WH. Run these one at a time:
1. SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();
2. SHOW SCHEMAS LIKE 'DBT_<INITIALS>' IN DATABASE TRICON_DE;
3. SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS;   -- expect 1500000
4. SELECT COUNT(*) FROM TRICON_DE.DBT_<INITIALS>.RESIDENT_CONTACTS;   -- expect 40
Then run `dbt --version` and `git config user.name` in the terminal.
Give me a PASS/FAIL table. Do not create, change, or drop anything.""", language="text")
    render_expected("Six PASS rows. You're ready for lab day.")
    render_troubleshoot([
        ("Row 2 returns nothing", "Your initials don't match the schema your admin created. Check the sidebar against your admin's row."),
        ("Row 4 fails", "Step 6's `dbt seed` didn't run or failed. Run it again."),
        ("CoCo asks to approve each statement", "That's normal. Approve them; they're all read-only."),
    ])

st.space("small")
st.markdown("#### On lab day")
st.markdown(f"""
- Open this app, check the sidebar still shows your details (they're kept in the page link: bookmark it), and start **Module 1**.
- Keep CoCo Desktop open on the `coco-hol-tricon-de` folder with role `TRICON_DE_ROLE`.
- Stuck? **Help & Troubleshooting** in the menu, then the facilitator. Reference answers for every module are in `solutions/`.
""")
