import streamlit as st
from components import (
    GUIDE_URL,
    LAB_DB,
    LAB_ROLE,
    LAB_WH,
    REPO_NAME,
    attendee_schema,
    render_code,
    render_expected,
    render_explanation,
    render_guide_change,
    render_key_concepts,
    render_prompt,
    render_same_as_guide,
    render_session_header,
    render_technologies_used,
    render_troubleshoot,
    render_what_you_built,
    setup_complete,
)

render_session_header("Module 1", "Create an AGENTS.md", "15 min", "Project context CoCo reads every session, then a conventions audit of the starter models")
st.caption(f"Follows the guide section *Create an AGENTS.md* in [Data Engineering with CoCo]({GUIDE_URL}). Work through the steps in order; each one ends with what you should see.")

if not setup_complete():
    st.warning("**Type your initials in the sidebar first.** The prompts on this page then use your schema.", icon=":material/arrow_back:")

render_technologies_used([
    {"name": "CoCo Desktop", "description": "Snowflake's AI coding agent as a desktop IDE, with local file access, Git, and full support for skills, plugins, hooks, and subagents.", "icon": "desktop_windows"},
    {"name": "AGENTS.md", "description": "A Markdown file at the project root with the conventions and commands the agent should know in every session.", "icon": "description"},
    {"name": "dbt build", "description": "Compiles, runs, and tests models in one command.", "icon": "construction"},
])

# ---------------------------------------------------------------- Concept
st.markdown("#### What is AGENTS.md?")
st.markdown("""
Before you write a single prompt, one file improves every interaction you'll have with CoCo in this project: `AGENTS.md`.

It's a Markdown file at the root of your project with the conventions, context, and commands you want the agent to know **every session, automatically**. Without it, you re-explain your database names, naming conventions, and preferred commands in every new chat. With it, that context is always there.

Think of it as the onboarding document you'd write for a new team member, except this one reads it perfectly every time. Three rules for writing one:

- **Keep it short.** The context window is a shared, finite resource. Does the agent *actually* need this sentence?
- **Encode what the model can't infer.** Don't explain how dbt works; CoCo knows. Do write down your database, schema, and the exact build command.
- **It doesn't change session to session.** Stable project facts go here; session-specific instructions go in your prompts.
""")

# ---------------------------------------------------------------- Step 1
st.markdown("#### Step 1: Check you're ready")
with st.container(border=True):
    st.markdown(f"""
Confirm all four before you start. If any fails, go back to **Module 0: Setup**.

| Check | Where to look |
|---|---|
| The project is open | CoCo Desktop's **Explorer** (left sidebar, file icon) shows `dbt/`, `scripts/`, `part2/`. If not: **File → Open Folder** → your `{REPO_NAME}` folder |
| You're on the right role | The connection name at the **top** of CoCo Desktop shows role **{LAB_ROLE}**. If not: click it → **Change Role** → {LAB_ROLE} |
| Your schema exists | You ran `scripts/setup.sql` and it printed *Ready: {LAB_DB}.{attendee_schema()}* |
| dbt connects | `dbt debug --project-dir dbt/` ended with *All checks passed!* |
""")

# ---------------------------------------------------------------- Step 2
st.markdown("#### Step 2: Start a new chat")
with st.container(border=True):
    st.markdown("""
1. Find the **chat panel**: the CoCo panel on the right side of CoCo Desktop, with a message box at the bottom.
2. Click **+** (*New Session*) at the top of the chat panel, so this module starts with a clean conversation.
3. Leave the model on its default.
""")
    render_expected("An empty chat with a message box at the bottom.")
    st.caption("Start a new chat at the beginning of every module. Long conversations from earlier work can confuse CoCo.")

# ---------------------------------------------------------------- Step 3
st.markdown("#### Step 3: Ask CoCo to create your AGENTS.md")
with st.container(border=True):
    st.markdown("Copy the prompt below (hover over it and click the **copy** icon, top right), paste it into the chat box, and press **Enter**.")

    PROMPT_1_1 = f"""Create an AGENTS.md file at the root of this project. Include:
- The Snowflake database ({LAB_DB}), schema (TPCH_<INITIALS>), and warehouse ({LAB_WH})
- The dbt build command to use: `dbt build --project-dir dbt/`
- The command to build a single model: `dbt build --select <model_name> --project-dir dbt/`
- Snake_case naming convention for model files
- The source data is TPCH_SF1 in SNOWFLAKE_SAMPLE_DATA; all raw tables must be referenced through _sources.yml
- Feature branches should follow the pattern: feature/<description>
- PRs are required before merging to main
- This project uses CoCo Desktop — do not use the `cortex` CLI command"""

    render_prompt("Prompt 1.1", "Create AGENTS.md", PROMPT_1_1)
    render_same_as_guide("Create an AGENTS.md → Create Your AGENTS.md")
    render_guide_change("schema (TPCH_TRANSFORMED)", f"schema ({attendee_schema()})", "Your own schema, so CoCo builds and checks your tables, not a neighbour's.")

    st.markdown("""
**What happens next:**

1. CoCo reads the project and writes a proposed `AGENTS.md`. It may show what it's doing as it goes ("reading files...", "creating file...").
2. The new file appears as a **change to review**, with **Keep** and **Undo** buttons (in the chat, or at the top of the file).
3. Read it, then click **Keep** to save it.
""")
    render_expected(f"A new `AGENTS.md` in the Explorer, at the **top level** of the project (next to `dbt/`, not inside it).")

# ---------------------------------------------------------------- Step 4
st.markdown("#### Step 4: Check the file")
with st.container(border=True):
    st.markdown(f"Click `AGENTS.md` in the Explorer to open it. Your version may be worded differently, and that's OK, but it should look something like this. Most importantly, the schema must be **{attendee_schema()}**:")
    render_code(f"""# Project: CoCo DE Guide

## Snowflake
- Database: {LAB_DB}
- Schema: TPCH_<INITIALS>
- Warehouse: {LAB_WH}

## dbt Commands
- Build + test: `dbt build --project-dir dbt/`
- Single model: `dbt build --select <model_name> --project-dir dbt/`

## Naming Conventions
- Model files: snake_case
- Source schema: TPCH_SF1 in SNOWFLAKE_SAMPLE_DATA
- Transformed schema: TPCH_<INITIALS>

## Branching
- Feature branches: `feature/<description>`
- PRs required before merging to main

## CoCo
- This project uses CoCo Desktop — do not use the `cortex` CLI command""", language="markdown")
    st.info(":material/info: **Why the last line?** CoCo has bundled skills that know about the CoCo CLI `cortex` command. Those skills can activate and make CoCo attempt CLI operations. This line prevents it.")
    render_troubleshoot([
        ("`AGENTS.md` landed inside `dbt/`", "Ask CoCo: *Move AGENTS.md to the project root.*"),
        ("It says `TPCH_TRANSFORMED` or `<INITIALS>`", f"Type your initials in the sidebar, or edit the file yourself: change the schema to `{attendee_schema()}` and save (`CMD/CTRL+S`)."),
        ("You clicked **Undo** by mistake", "Send Prompt 1.1 again."),
        ("CoCo asks a question instead of creating the file", "Answer it, or reply: *Use the values in my prompt and create the file.*"),
    ])

# ---------------------------------------------------------------- Step 5
st.markdown("#### Step 5: Audit the starter code against your conventions")
with st.container(border=True):
    st.markdown("""
Now put `AGENTS.md` to work. The starter project was written **before** these conventions existed, which is exactly what you'll face when you inherit a codebase.
Paste this into the **same chat** and press **Enter**:
""")
    PROMPT_1_2 = """Review all dbt models in this project against the conventions in AGENTS.md
and fix any violations you find."""
    render_prompt("Prompt 1.2", "Audit the Starter Models", PROMPT_1_2)
    render_same_as_guide("Create an AGENTS.md → Validate the Starter Code Against Your Conventions")
    st.markdown("""
**What happens next:** CoCo reads `AGENTS.md`, then opens each model in `dbt/models/`. It should find that `orders_summary.sql` reads the source tables by their full Snowflake path, instead of going through `_sources.yml`:

```sql
-- Violation: direct source reference
FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS o
LEFT JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.LINEITEM l ...
```

and propose rewriting it to use `source()`:

```sql
-- Fixed: references go through _sources.yml
FROM {{ source('tpch', 'orders') }} o
LEFT JOIN {{ source('tpch', 'lineitem') }} l ...
```

Review the change to `orders_summary.sql` (red lines removed, green lines added), then click **Keep**.
""")
    render_expected("One changed file: `dbt/models/orders_summary.sql`. CoCo reports that `customers.sql` already follows the conventions.")
    render_troubleshoot([
        ("CoCo says it found no violations", "Ask: *Look at the FROM clauses in orders_summary.sql. Do they use source()?*"),
        ("CoCo also changed `_sources.yml`", "Click **Undo** on that file, or ask: *Only change the model files.*"),
        ("CoCo edits files in `part2/`", "Click **Undo** on those, and say: *part2/ isn't part of this project.*"),
        ("CoCo runs `cortex ...` commands", "Say: *Do not use the cortex CLI.*"),
    ])

# ---------------------------------------------------------------- Step 6
st.markdown("#### Step 6: Run dbt build to confirm nothing broke")
with st.container(border=True):
    st.markdown("""
1. Open a terminal in CoCo Desktop: **Terminal → New Terminal** (or `` CTRL+` ``). It opens in the project folder, below the editor.
2. Run:
""")
    render_code("dbt build --project-dir dbt/")
    st.markdown("This builds both models in your schema and runs any tests (there are none yet; Module 2 adds them).")
    render_expected(f"Two `OK created` lines, for `{attendee_schema()}.customers` and `{attendee_schema()}.orders_summary`, then **`Done. PASS=2 WARN=0 ERROR=0 SKIP=0`**.")
    render_troubleshoot([
        ("`Could not find profile named 'coco_de_guide'`", "Your `~/.dbt/profiles.yml` is missing the block. Redo Module 0, Step 6."),
        ("Output mentions `TPCH_TRANSFORMED`", f"`schema:` in `~/.dbt/profiles.yml` is still the example value. Change it to `{attendee_schema()}`, save, and run again."),
        ("`Compilation Error ... source named 'tpch'`", "`_sources.yml` was changed. Run `git checkout dbt/models/_sources.yml` and build again."),
        ("`dbt: command not found`", "Close and reopen the terminal. Still missing: Module 0, Step 2."),
        ("The terminal isn't in the project folder", f"Run `cd` to your `{REPO_NAME}` folder first (the one containing `dbt/`)."),
    ])

# ---------------------------------------------------------------- Step 7
st.markdown("#### Step 7 (optional): See your tables in Snowflake")
with st.container(border=True):
    st.markdown("Ask CoCo in the chat. It runs read-only SQL against your schema:")
    render_code(f"List the tables in {LAB_DB}.TPCH_<INITIALS> with their row counts.", language="text")
    render_expected("`CUSTOMERS` with 150,000 rows and `ORDERS_SUMMARY` with 1,500,000 rows. Approve the query if CoCo asks.")

render_explanation("Why this matters", """
CoCo didn't need to be told what the violation was or what the fix should look like. It read the conventions, read the code, and connected the two.
That's the value of `AGENTS.md`: not one dramatic prompt, but **every prompt in the session grounded in your standards** rather than the model's best guess.

Any time you find yourself repeating the same context in multiple prompts (a team convention, a frequent command, an important constraint), that's a signal it belongs in `AGENTS.md`.
""")

st.markdown("#### Checkpoint")
st.markdown(f"""
| You should have | Check |
|---|---|
| `AGENTS.md` at the project root | Mentions `{LAB_DB}`, `{attendee_schema()}`, `{LAB_WH}` |
| `dbt/models/orders_summary.sql` | Uses `{{{{ source('tpch', ...) }}}}` |
| A clean build | `PASS=2` in your schema |

Don't commit yet; the guide commits everything at the end of Module 4. Next: **Module 2**, in a new chat.
""")

render_key_concepts([
    {"term": "Why AGENTS.md beats repeating yourself", "definition": "Without it, you re-explain database names, conventions, and commands in every chat. With it, every prompt is grounded in your standards rather than the model's best guess."},
    {"term": "When to update AGENTS.md", "definition": "Whenever you find yourself repeating the same context in multiple prompts, that's a signal it belongs in AGENTS.md."},
])

render_what_you_built([
    "AGENTS.md with your Snowflake context, dbt commands, and conventions",
    "orders_summary.sql fixed to use source() references",
    f"A clean dbt build in {LAB_DB}.TPCH_<INITIALS>",
])
