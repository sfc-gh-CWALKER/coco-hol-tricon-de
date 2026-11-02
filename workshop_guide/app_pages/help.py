import streamlit as st

from components import LAB_DB, LAB_ROLE, LAB_WH, PLUGIN, REPO_NAME, attendee_schema, render_code, render_expected

st.title("Help & Troubleshooting")
st.markdown("Find your symptom below. If nothing matches, use the **reset** steps at the bottom, then ask the facilitator.")

st.markdown("#### Quick health check")
with st.container(border=True):
    st.markdown("Run this in the CoCo Desktop terminal at any time. It changes nothing.")
    render_code(f"""pwd                                     # should end in {REPO_NAME}
grep -n "schema:" ~/.dbt/profiles.yml   # should show {attendee_schema()}
dbt debug --project-dir dbt/ | tail -2""")
    render_expected(f"A path ending in `{REPO_NAME}`, `schema: {attendee_schema()}`, and `All checks passed!`")

st.markdown("#### Setup and sign-in")
st.markdown(f"""
| If you see | Do this |
|---|---|
| *Set MY_INITIALS at the top of scripts/setup.sql...* | Change `XX` to your initials in `scripts/setup.sql`, then Run all again |
| *Role '{LAB_ROLE}' ... not authorized* or not in the role list | Your admin hasn't granted it to your username yet (`scripts/admin_setup.sql`). Send them the username from Snowsight → your name → Profile |
| *Account not found* | Use `orgname-accountname` from Snowsight → your name → *Connect a tool to Snowflake* |
| *Incorrect username or password* from dbt | `password:` in `~/.dbt/profiles.yml` must be the PAT itself, in quotes |
| *Network policy is required* / *IP not allowed* | Connect to the company VPN, or switch the profile to `authenticator: externalbrowser` (Module 0, Step 6) |
| Module 4 CI run is red: *IP ... is not allowed* | GitHub's runners aren't allowed in. Use the laptop fallback (Module 4, Step 5) |
| CoCo Desktop: *access blocked* or no replies | CoCo may not be enabled for your user yet. Send the error to your admin |
""")

st.markdown("#### dbt")
st.markdown(f"""
| If you see | Do this |
|---|---|
| `Could not find profile named 'coco_de_guide'` | Add the `coco_de_guide` block to `~/.dbt/profiles.yml` (Module 0, Step 6) |
| `<...>` placeholders in an error | Fill in the sidebar, then copy the Step 6 block again |
| *Schema '{LAB_DB}.TPCH_..' does not exist* | Run `scripts/setup.sql` with your initials, and use the same initials in `profiles.yml` |
| Tables appear in `TPCH_TRANSFORMED` or someone else's schema | Your `schema:` line isn't `{attendee_schema()}`. Fix it, then `dbt build` again |
| *Object 'SNOWFLAKE_SAMPLE_DATA...' does not exist* | Ask your admin to run the sample-data grant in `scripts/admin_setup.sql` |
| `dbt: command not found` | Close and reopen the terminal (and CoCo Desktop). Then Module 0, Step 2 |
| *Warehouse '{LAB_WH}' ... queued* for a long time | 30 people are building at once. Wait, or ask the admin to size `{LAB_WH}` up for the session |
| A test fails on `order_status` | TPC-H statuses are **F, O, P**. In Module 2, fix the test; in Module A1, that failure is the point |
""")

st.markdown("#### CoCo Desktop")
st.markdown(f"""
| If you see | Do this |
|---|---|
| CoCo runs `cortex ...` commands | Say: *Do not use the cortex CLI; write the files directly* |
| CoCo uses the wrong schema | Check `AGENTS.md` and `~/.dbt/profiles.yml` both say `{attendee_schema()}` |
| CoCo edits files in `part2/` | Say: *Revert that; part2/ isn't part of this project* |
| The plugin, skill, or hook doesn't show up | Settings → Plugins → **↻**. The folder must be **trusted** (Command Palette → *Manage Workspace Trust*) |
| CoCo seems confused by an earlier conversation | Start a **new chat** for each module |
| You want to see the reference answer | Every skill, subagent and hook is in `part2/solutions/{PLUGIN}/` |
""")

st.markdown("#### Git and GitHub")
st.markdown("""
| If you see | Do this |
|---|---|
| *Please tell me who you are* | `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`, then commit again |
| dbt-review says *no changes* | Ask it to include uncommitted and untracked files (Module 3, *If dbt-review finds no changes*) |
| *Permission denied* on push | You cloned the workshop repo instead of your fork. Fork it, then `git remote set-url origin https://github.com/<YOUR_GITHUB_USERNAME>/sfguide-data-engineering-with-coco` |
| The PR opened against the workshop repo | Close it and open one with base repository = your fork |
""")

st.markdown("#### Start a module over")
with st.container(border=True):
    st.markdown("To throw away everything since your last commit:")
    render_code("""git status             # see what would be lost
git restore .          # undo changes to tracked files
git clean -fd          # delete new untracked files""")
    st.caption(f"Your Snowflake tables stay in your schema; `dbt build` overwrites them. Want the finished state for a module? Copy it from `part2/solutions/{PLUGIN}/`.")
