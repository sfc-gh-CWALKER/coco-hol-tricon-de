import streamlit as st

from components import attendee_schema, render_code

st.title("Getting Started")
st.markdown("Install the tools, clone the starter project, and connect dbt and CoCo Desktop to Tricon's Snowflake account. **Do this before the lab** — installs often need IT approval.")

st.space("small")

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
Add a Snowflake connection in CoCo Desktop using your normal Tricon Snowflake login.

| Setting | Value |
|---------|-------|
| **Account** | Tricon's account identifier (from your admin) |
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

st.space("small")

st.markdown("#### Step 5: Verify")
with st.container(border=True):
    st.markdown("In a CoCo Desktop terminal (**Terminal → New Terminal**):")
    render_code("dbt debug --project-dir dbt/")
    st.markdown("You should see `All checks passed!`. Then seed the synthetic data used later in Module A2:")
    render_code("dbt seed --project-dir dbt/")
