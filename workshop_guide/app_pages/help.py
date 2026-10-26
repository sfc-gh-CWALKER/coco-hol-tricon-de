import streamlit as st

from components import render_code, render_expected

st.title("Help & Troubleshooting")
st.markdown("Find your symptom below. If nothing matches, use the **reset** steps at the bottom, then ask the facilitator.")

st.markdown("#### Quick health check")
with st.container(border=True):
    st.markdown("Run this in the CoCo Desktop terminal at any time. It changes nothing.")
    render_code("""pwd                                  # should end in coco-hol-tricon-de
git branch --show-current            # feature/add-tricon-de-plugin after Module 1
dbt debug --project-dir dbt/ | tail -2""")
    render_expected("A path ending in `coco-hol-tricon-de`, your branch name, and `All checks passed!`")

st.markdown("#### Signing in")
st.markdown("""
| If you see | Do this |
|---|---|
| *Account not found* | Copy `account_identifier` exactly from your admin's row (`orgname-accountname`) into the sidebar, then redo Getting Started, Step 5 |
| *Incorrect username or password* | Check the sidebar username. Temporary lab logins: you must have changed the starting password (Getting Started, Step 1). Forgot it? Your admin can reset it |
| *IP ... is not allowed to access Snowflake* | Tricon's network policy: connect to the Tricon VPN |
| A browser tab opens on every dbt command | Normal for SSO or password logins if Tricon hasn't enabled sign-in caching. Switch `profiles.yml` to `authenticator: oauth_authorization_code` if your admin says Local OAuth is available |
| *Role TRICON_DE_ROLE ... is not granted* | Your admin hasn't added this username. Send them the username shown in Snowsight → your name → Profile |
| CoCo Desktop: *access blocked* or no replies | Your admin's readiness check, row 2 (CoCo Desktop credit limit). Send them the error |
""")

st.markdown("#### dbt")
st.markdown("""
| If you see | Do this |
|---|---|
| `Could not find profile named 'tricon_de'` | Run `pwd`. You must be in the `coco-hol-tricon-de` folder, and `profiles.yml` must exist there (Getting Started, Step 5) |
| `<...>` placeholders in an error | Fill in the sidebar, then redo Getting Started, Step 5 |
| *Schema 'TRICON_DE.DBT_..' does not exist or not authorized* | Your sidebar initials don't match your admin's list |
| *Object 'SNOWFLAKE_SAMPLE_DATA...' does not exist* | Ask your admin to re-run the setup script (it adds the sample data) |
| `dbt: command not found` | Close and reopen the terminal (and CoCo Desktop). Then Getting Started, Step 2 |
| *Warehouse 'TRICON_DE_WH' cannot be resumed / suspended* | The lab's weekly credit cap was hit. Tell the facilitator (admin raises it in one line) |
| A test fails on `order_status` | TPC-H statuses are **F, O, P**. In Module 2, fix the test; in Module A1, that failure is the point |
""")

st.markdown("#### CoCo Desktop")
st.markdown("""
| If you see | Do this |
|---|---|
| CoCo edits files in `workshop_guide/` or `solutions/` | Say: *Revert that; AGENTS.md says to ignore those folders.* Then check `AGENTS.md` has that line |
| CoCo runs `cortex ...` commands | Say: *Do not use the cortex CLI; write the files directly* |
| CoCo uses the wrong schema | Check `AGENTS.md` and `profiles.yml` both say `DBT_<your initials>` |
| The plugin, skill, or hook doesn't show up | Settings → Plugins → **↻**. The folder must be **trusted** (Command Palette → *Manage Workspace Trust*) |
| CoCo seems confused by an earlier conversation | Start a **new chat** for each module |
| You want to see the reference answer | Every skill, subagent, and hook is in `solutions/tricon-de-plugin/` |
""")

st.markdown("#### Git")
st.markdown("""
| If you see | Do this |
|---|---|
| *Please tell me who you are* | `git config --global user.name "Your Name"` and `git config --global user.email "you@triconresidential.com"`, then commit again |
| dbt-review says *no changes* | You're on `main` or haven't committed. See Module 3, *If dbt-review finds no changes* |
| *Permission denied* on `git push` | Expected: you cloned the shared repo. Pushing is only needed for Module 4 Option B, which uses your own fork |
""")

st.markdown("#### Start a module over")
with st.container(border=True):
    st.markdown("Committing at each module's checkpoint means you can always go back. To throw away everything since your last commit:")
    render_code("""git status             # see what would be lost
git restore .          # undo changes to tracked files
git clean -fd -e profiles.yml   # delete new untracked files, keep your profile""")
    st.caption("Your Snowflake objects stay in your schema; `dbt build` overwrites them. Behind and want the finished state for a module? Copy it from `solutions/tricon-de-plugin/`.")
