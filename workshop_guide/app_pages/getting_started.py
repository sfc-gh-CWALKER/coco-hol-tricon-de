import streamlit as st

from components import (
    GUIDE_URL,
    LAB_DB,
    LAB_ROLE,
    LAB_WH,
    REPO_NAME,
    REPO_URL,
    attendee_schema,
    attendee_user,
    profiles_yml,
    render_code,
    render_expected,
    render_guide_change,
    render_same_as_guide,
    render_troubleshoot,
    setup_complete,
)

st.title("Getting Started")
st.markdown(f"""
This page is the guide's **Setup** section ([Data Engineering with CoCo]({GUIDE_URL})), step by step.
Finish it **before lab day**: installs can need IT approval.

The only change from the guide: everyone shares one Snowflake account, so each person builds in their **own schema**,
`{LAB_DB}.TPCH_<INITIALS>`, instead of the guide's `{LAB_DB}.TPCH_TRANSFORMED`. Fill in the sidebar and every step below uses yours.
""")

if not setup_complete():
    st.warning("**First, fill in the sidebar** (initials, Snowflake username, account). Every script and file below then fills itself in.", icon=":material/arrow_back:")

# ---------------------------------------------------------------- Step 1
st.markdown("#### Step 1: Fork and clone the guide repository")
with st.container(border=True):
    render_same_as_guide("Setup → Fork and Clone the Guide Repository")
    st.markdown(f"""
1. Open the workshop's copy of the guide repo: **[{REPO_URL.removeprefix('https://')}]({REPO_URL})**
2. Click **Fork** (top right) → **Create fork**. Your fork is where Module 4's pull request and CI/CD run.
3. Clone **your fork**:
""")
    render_code(f"""git clone https://github.com/<YOUR_GITHUB_USERNAME>/{REPO_NAME}
cd {REPO_NAME}""")
    render_expected(f"A `{REPO_NAME}` folder containing `dbt/`, `scripts/`, `part2/`, `README.md`.")
    render_guide_change(
        "Fork `Snowflake-Labs/sfguide-data-engineering-with-coco`.",
        f"Fork the workshop copy at `{REPO_URL.removeprefix('https://github.com/')}`. Same starter project, plus a per-person `scripts/setup.sql` and an optional `part2/` folder that dbt never reads.",
        "Lets 30+ people run the guide on one account without overwriting each other.")
    render_troubleshoot([
        ("No GitHub account, or GitHub is blocked", f"Clone without forking: `git clone {REPO_URL}`. Modules 1–3 work the same; only Module 4's CI/CD needs a fork."),
        ("*Could not resolve host github.com*", "GitHub is blocked on your network. Try off VPN, or ask the facilitator for a ZIP (then run `git init && git add -A && git commit -m start` inside it)."),
        ("*destination path already exists*", f"You cloned before. `cd {REPO_NAME} && git pull`."),
    ])

# ---------------------------------------------------------------- Step 2
st.markdown("#### Step 2: Install the tools")
with st.container(border=True):
    st.markdown("""
| Tool | Install |
|---|---|
| **CoCo Desktop** | [Download](https://www.snowflake.com/en/product/snowflake-coco/downloads/) · Windows: the **User installer** needs no admin rights |
| **Git** | macOS: run `git --version` (it offers to install). Windows: [Git for Windows](https://git-scm.com/download/win), keep the defaults (includes **Git Bash**, used by the Module 3 hook) |
| **dbt Core + dbt-snowflake** | The commands below. `uv` brings its own Python, so your system Python doesn't matter |
""")
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
    render_expected("`dbt --version` lists **Core 1.10 or newer** and **Plugins: snowflake**.")
    render_troubleshoot([
        ("`dbt: command not found`", "Close **all** terminals (and CoCo Desktop) and reopen. Still missing: `uv tool update-shell`, then reopen."),
        ("Installer blocked by IT", "With any Python 3.10–3.13: `python3 -m pip install --user dbt-core dbt-snowflake`. Don't use macOS's built-in Python 3.9."),
        ("No **snowflake** plugin listed", "`uv tool install --force --python 3.12 dbt-core --with dbt-snowflake`"),
    ])

# ---------------------------------------------------------------- Step 3
st.markdown("#### Step 3: Configure CoCo Desktop and open the project")
with st.container(border=True):
    render_same_as_guide("Setup → Configure CoCo Desktop and Open the Project")
    st.markdown(f"""
1. Open CoCo Desktop and add a Snowflake connection: account **`{st.session_state.get('sf_account') or '<YOUR_ACCOUNT>'}`**, user **`{attendee_user()}`**, authentication **Local OAuth**.
2. **File → Open Folder** → the `{REPO_NAME}` folder you cloned → **Trust** when asked (plugins only work in a trusted folder).
3. Click the connection name at the top → **Change Role** → **{LAB_ROLE}**.
""")
    render_expected(f"The top bar shows your connection with role **{LAB_ROLE}**, and the Explorer shows `dbt/`, `scripts/`, `part2/`.")
    render_troubleshoot([
        (f"{LAB_ROLE} isn't in the role list", f"Your admin hasn't granted it to `{attendee_user()}` yet (`scripts/admin_setup.sql`). Send them your username."),
        ("*Account not found*", "Use the `orgname-accountname` form from Snowsight → your name → *Connect a tool to Snowflake*."),
        ("Browser didn't open", "Click **Browser didn't open?** and open the link yourself."),
    ])

# ---------------------------------------------------------------- Step 4
st.markdown("#### Step 4: Create your Snowflake demo environment")
with st.container(border=True):
    st.markdown(f"""
Your admin already created the shared **{LAB_ROLE}**, **{LAB_WH}** and **{LAB_DB}**. You create only your own schema:

1. In CoCo Desktop, open **`scripts/setup.sql`**.
2. Change `XX` on this line to your initials:
""")
    render_code(f"SET MY_INITIALS = '{st.session_state.get('initials', '').strip().upper() or 'XX'}';", language="sql")
    st.markdown("3. **Run all**: the down arrow next to the blue play button → *Run all*, or `CMD/CTRL+Shift+Enter`.")
    render_expected(f"*Your schema `{LAB_DB}.{attendee_schema()}` is ready*, then a count of **1500000** orders.")
    render_guide_change(
        f"`setup.sql` creates the role, warehouse, database and one schema, `{LAB_DB}.TPCH_TRANSFORMED`.",
        f"The admin creates the shared objects once (`scripts/admin_setup.sql`). Your `setup.sql` creates only `{LAB_DB}.{attendee_schema()}`.",
        "With one shared schema, everyone's `dbt build` would replace everyone else's tables.")
    render_troubleshoot([
        ("*Set MY_INITIALS at the top of scripts/setup.sql...*", "You ran it with `XX`. Change it to your initials and Run all again."),
        (f"*Role '{LAB_ROLE}' ... not authorized* / *does not exist*", "Your admin hasn't granted you the role yet. Send them your username."),
        ("*Insufficient privileges to operate on database*", f"You ran it with a different role. Select **{LAB_ROLE}** at the top and run again."),
        ("The count query fails", f"{LAB_ROLE} can't read `SNOWFLAKE_SAMPLE_DATA`. Ask your admin to run the sample-data grant in `scripts/admin_setup.sql`."),
        ("Someone else already has your initials", "Add a letter (e.g. `CWA`), and use the same initials in the sidebar."),
    ])

# ---------------------------------------------------------------- Step 5
st.markdown("#### Step 5: Create a Snowflake Personal Access Token")
with st.container(border=True):
    render_same_as_guide("Setup → Create a Snowflake Personal Access Token")
    st.markdown(f"""
In Snowsight: your name (bottom left) → **Settings** → **Authentication** → **Programmatic access tokens** → **Generate new token**:

- **Name**: `DEMO_PAT`
- **Expires in**: default (15 days)
- **Grant access**: **Single role** → `{LAB_ROLE}`

**Copy the token now**; you can't see it again. Tokens belong to your user, so everyone can name theirs `DEMO_PAT`.
""")
    st.info(":material/lock: The guide also runs `ALTER USER ... SET MINS_TO_BYPASS_NETWORK_POLICY_REQUIREMENT = 60` here, so GitHub Actions can connect. **Skip that on a company account.** It's only needed for Module 4's CI/CD, which covers what to do instead.")
    render_troubleshoot([
        ("No *Programmatic access tokens* section", "PATs may be disabled by an authentication policy on your account. Ask your admin, or use the Local OAuth alternative in Step 6."),
        (f"{LAB_ROLE} isn't in the *Single role* list", "Your admin hasn't granted you the role. See Step 3."),
    ])

# ---------------------------------------------------------------- Step 6
st.markdown("#### Step 6: Configure dbt")
with st.container(border=True):
    render_same_as_guide("Setup → Configure dbt")
    st.markdown("dbt looks for `~/.dbt/profiles.yml`. If you don't have one yet, copy the example file. Run this in the CoCo Desktop terminal (it opens in the project folder):")
    render_code("""mkdir -p ~/.dbt
cp dbt/profiles.yml.example ~/.dbt/profiles.yml""")
    st.markdown("Open `~/.dbt/profiles.yml` (`CMD/CTRL+P`) and make the `coco_de_guide` block look like this. Paste your token over `<YOUR_PERSONAL_ACCESS_TOKEN>`:")
    if not setup_complete():
        st.error("Fill in the sidebar first, or the block below still has placeholders.", icon=":material/error:")
    render_code(profiles_yml(), language="yaml")
    st.caption("If you already have a `~/.dbt/profiles.yml`, add this `coco_de_guide` block alongside your other profiles; they don't conflict. The file lives outside the repo, so your token can't be committed.")
    render_guide_change(
        "`schema: TPCH_TRANSFORMED`",
        f"`schema: {attendee_schema()}`",
        "Your own schema, from Step 4.")
    with st.expander(":material/key: Can't create a PAT? Sign in through the browser instead"):
        st.markdown("Replace the `password:` line with the line below. dbt opens a browser tab to sign in, and nothing is stored in the file. You'll still need a PAT (or a service user) for Module 4's GitHub Actions.")
        render_code("      authenticator: externalbrowser", language="yaml")

# ---------------------------------------------------------------- Step 7
st.markdown("#### Step 7: Verify your dbt setup")
with st.container(border=True):
    render_same_as_guide("Setup → Verify Your dbt Setup")
    render_code("dbt debug --project-dir dbt/")
    render_expected("`Connection test: [OK connection ok]` and **`All checks passed!`**")
    render_troubleshoot([
        ("`Could not find profile named 'coco_de_guide'`", "The block isn't in `~/.dbt/profiles.yml`, or the top-level name is different. Redo Step 6."),
        ("*Incorrect username or password*", "Paste the PAT itself (a long string) as `password:`, in quotes, and check `user:` matches your username."),
        (f"*Role '{LAB_ROLE}' specified in the connect string is not granted*", "The PAT was created for a different role. Create a new one with *Single role* → " + LAB_ROLE + "."),
        (f"*Schema '{LAB_DB}.TPCH_..' does not exist*", "Step 4 didn't run, or the initials in `profiles.yml` differ from the ones in `setup.sql`."),
        ("*Network policy is required* / *IP not allowed*", "Your account requires a network policy for PATs. Connect to the company VPN, or use the browser sign-in in Step 6."),
        ("`<...>` in an error", "A placeholder is left in `profiles.yml`. Fill in the sidebar and copy the Step 6 block again."),
    ])

st.space("small")
st.markdown("#### On lab day")
st.markdown(f"""
- Open this app and check the sidebar still shows your details (they're kept in the page link, so bookmark it).
- Keep CoCo Desktop open on the `{REPO_NAME}` folder with role `{LAB_ROLE}`, then start **Module 1**.
- Stuck? **Help & Troubleshooting** in the menu, then the facilitator.
""")
