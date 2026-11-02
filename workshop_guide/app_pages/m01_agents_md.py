import streamlit as st
from components import (
    LAB_DB,
    LAB_ROLE,
    LAB_WH,
    REPO_NAME,
    attendee_schema,
    render_before_you_start,
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
)

render_session_header("Module 1", "AGENTS.md", "15 min", "Project context CoCo reads every session, then a conventions audit of the starter models")

render_technologies_used([
    {"name": "CoCo Desktop", "description": "Snowflake's AI coding agent as a desktop IDE, with local file access, Git, and full support for skills, plugins, hooks, and subagents.", "icon": "desktop_windows"},
    {"name": "AGENTS.md", "description": "A Markdown file at the project root with the conventions and commands the agent should know in every session.", "icon": "description"},
    {"name": "dbt build", "description": "Compiles, runs, and tests models in one command.", "icon": "construction"},
])

render_before_you_start([
    "**Getting Started** is done: `dbt debug` says *All checks passed!*",
    f"CoCo Desktop has the `{REPO_NAME}` folder open, with role **{LAB_ROLE}** at the top.",
    "Start a **new chat** for each module, so earlier conversations don't confuse CoCo.",
])

st.markdown("""
`AGENTS.md` is the onboarding document you'd write for a new team member, except this team member reads it every time and never forgets it. Three rules for writing one:

- **Keep it short.** The context window is a shared, finite resource.
- **Encode what the model can't infer.** CoCo already knows dbt. It doesn't know your database name, schema, or build command.
- **It doesn't change session to session.** Stable project facts belong here; session-specific instructions belong in prompts.
""")

st.markdown("#### Create your AGENTS.md")

PROMPT_1_1 = f"""Create an AGENTS.md file at the root of this project. Include:
- The Snowflake database ({LAB_DB}), schema (TPCH_<INITIALS>), and warehouse ({LAB_WH})
- The dbt build command to use: `dbt build --project-dir dbt/`
- The command to build a single model: `dbt build --select <model_name> --project-dir dbt/`
- Snake_case naming convention for model files
- The source data is TPCH_SF1 in SNOWFLAKE_SAMPLE_DATA; all raw tables must be referenced through _sources.yml
- Feature branches should follow the pattern: feature/<description>
- PRs are required before merging to main
- This project uses CoCo Desktop — do not use the `cortex` CLI command"""

render_same_as_guide("Create an AGENTS.md → Create Your AGENTS.md")
render_prompt("Prompt 1.1", "Create AGENTS.md", PROMPT_1_1)
render_guide_change("schema (TPCH_TRANSFORMED)", f"schema ({attendee_schema()})", "Your own schema, so CoCo builds and checks your tables, not a neighbour's.")
render_expected(f"CoCo proposes a new `AGENTS.md` at the project root. Click **Keep**. Check it says **{attendee_schema()}**, not `TPCH_TRANSFORMED` or `<INITIALS>`.")

render_explanation("What a good result looks like", f"""
Your `AGENTS.md` may be slightly different, and that's OK, but it should look something like this:

```markdown
# Project: CoCo DE Guide

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
- This project uses CoCo Desktop — do not use the `cortex` CLI command
```

CoCo has bundled skills that know about the `cortex` CLI. The last line keeps them from making CoCo attempt CLI operations.
""")

st.markdown("#### Validate the starter code against your conventions")
st.markdown("The starter project was built before these conventions existed, which is exactly what you'll face when you inherit a codebase.")

PROMPT_1_2 = """Review all dbt models in this project against the conventions in AGENTS.md
and fix any violations you find."""

render_same_as_guide("Create an AGENTS.md → Validate the Starter Code Against Your Conventions")
render_prompt("Prompt 1.2", "Audit the Starter Models", PROMPT_1_2)
render_expected("CoCo edits `dbt/models/orders_summary.sql` to use `{{ source('tpch', 'orders') }}` and `{{ source('tpch', 'lineitem') }}`. `customers.sql` already complies. Click **Keep**.")

render_explanation("What this prompt does", """
CoCo should find that `orders_summary.sql` references source tables by their full Snowflake path:

```sql
-- Violation: direct source reference
FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS o
LEFT JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.LINEITEM l ...
```

and rewrite them to go through `_sources.yml`:

```sql
-- Fixed: references go through _sources.yml
FROM {{ source('tpch', 'orders') }} o
LEFT JOIN {{ source('tpch', 'lineitem') }} l ...
```

Nobody told CoCo what the violation was. It read the conventions, read the code, and connected the two.
""")

st.markdown("Once the fix is applied, run `dbt build` in the terminal to confirm nothing broke:")
render_code("dbt build --project-dir dbt/")
render_expected(f"`Done. PASS=2 WARN=0 ERROR=0`: `customers` (150,000 rows) and `orders_summary` (1,500,000 rows), built in **{LAB_DB}.{attendee_schema()}**.")

render_troubleshoot([
    ("CoCo created `AGENTS.md` inside `dbt/`", "Ask: *Move AGENTS.md to the project root.*"),
    ("CoCo says it found no violations", "Ask: *Look at the FROM clauses in orders_summary.sql. Do they use source()?*"),
    ("CoCo runs `cortex ...` commands", "Say: *Do not use the cortex CLI.* The AGENTS.md line prevents it from then on."),
    ("Build output mentions `TPCH_TRANSFORMED`", f"Your `~/.dbt/profiles.yml` still has the guide's schema. Change `schema:` to `{attendee_schema()}`."),
    ("`Compilation Error ... source named 'tpch'`", "CoCo changed `_sources.yml`. Ask it to restore the `tpch` source, or run `git checkout dbt/models/_sources.yml`."),
    ("CoCo edits files in `part2/`", "Say: *Revert that; part2/ isn't part of this project.* It's workshop reference material."),
])

render_key_concepts([
    {"term": "Why AGENTS.md beats repeating yourself", "definition": "Without it, you re-explain database names, conventions, and commands in every chat. With it, every prompt is grounded in your standards rather than the model's best guess."},
    {"term": "When to update AGENTS.md", "definition": "Whenever you find yourself repeating the same context in multiple prompts, that's a signal it belongs in AGENTS.md."},
])

render_what_you_built([
    "AGENTS.md with your Snowflake context, dbt commands, and conventions",
    "orders_summary.sql fixed to use source() references",
    f"A clean dbt build in {LAB_DB}.TPCH_<INITIALS>",
])
