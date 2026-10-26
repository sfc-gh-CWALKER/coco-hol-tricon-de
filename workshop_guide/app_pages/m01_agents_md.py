import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_code, render_guide_change, render_new_for_tricon

render_session_header("Module 1", "AGENTS.md", "15 min", "Project context CoCo reads every session, plus a conventions audit")

render_technologies_used([
    {"name": "CoCo Desktop", "description": "Snowflake's AI coding agent as a desktop IDE, with local file access, Git, and full support for skills, plugins, hooks, and subagents.", "icon": "desktop_windows"},
    {"name": "AGENTS.md", "description": "A Markdown file at the project root with the conventions and commands the agent should know in every session.", "icon": "description"},
    {"name": "dbt build", "description": "Compiles, runs, and tests models in one command. This project uses it instead of dbt run.", "icon": "construction"},
])

st.markdown("""
`AGENTS.md` is the onboarding document you'd write for a new team member, except this team member reads it every time and never forgets it. Three rules for writing one:

- **Keep it short.** The context window is a shared, finite resource.
- **Encode what the model can't infer.** CoCo already knows dbt. It doesn't know your database name, schema convention, or build command.
- **Keep it stable.** Session-specific instructions belong in prompts.
""")

PROMPT_1_1 = """Create an AGENTS.md file at the root of this project. Include:
- The Snowflake database (TRICON_DE), my schema (DBT_<INITIALS>), warehouse (TRICON_DE_WH), and role (TRICON_DE_ROLE)
- The dbt build command to use: `dbt build --project-dir dbt/`
- The command to build a single model: `dbt build --select <model_name> --project-dir dbt/`
- Snake_case naming convention for model files
- The source data is TPCH_SF1 in SNOWFLAKE_SAMPLE_DATA; all raw tables must be referenced through _sources.yml
- Feature branches should follow the pattern: feature/<description>
- PRs are required before merging to main
- Only create or change objects in TRICON_DE.DBT_<INITIALS>; never write to another attendee's DBT_* schema
- Never run dbt against --target prod, and never change grants, masking policies, or warehouse settings without my explicit approval — write proposals to the proposals/ folder instead
- Ignore the workshop_guide/ and solutions/ folders; they are lab materials, not project code
- This project uses CoCo Desktop — do not use the `cortex` CLI command"""

render_guide_change(
    "`DEMO_DB`, `TPCH_TRANSFORMED`, `DEMO_WH` (no role line, no safety line).",
    "`TRICON_DE`, `DBT_<INITIALS>`, `TRICON_DE_WH`, `TRICON_DE_ROLE`, plus two added lines: a **safety rule** (no `--target prod`; grants, masking, and warehouse changes go to `proposals/`) and **ignore `workshop_guide/` and `solutions/`**.",
    "Per-attendee schemas on a shared customer account, and Part 2 relies on the safety rule.")

render_prompt("Prompt 1.1", "Create AGENTS.md", PROMPT_1_1)

render_explanation("What a good result looks like", """
Click **Keep** to accept the file. It should look roughly like this:

```markdown
# Project: Tricon Data Engineering with CoCo

## Snowflake
- Database: TRICON_DE · Schema: DBT_<INITIALS> · Warehouse: TRICON_DE_WH · Role: TRICON_DE_ROLE

## dbt Commands
- Build + test: `dbt build --project-dir dbt/`
- Single model: `dbt build --select <model_name> --project-dir dbt/`

## Conventions
- Model files: snake_case
- Raw tables only through _sources.yml (SNOWFLAKE_SAMPLE_DATA.TPCH_SF1)

## Safety
- Only write to TRICON_DE.DBT_<INITIALS>; never touch other attendees' DBT_* schemas
- Never use --target prod
- Grants, masking policies, and warehouse changes need my approval; write proposals to proposals/

## Branching
- feature/<description>; PRs required before merging to main

## CoCo
- Use CoCo Desktop; do not use the `cortex` CLI. Ignore workshop_guide/ and solutions/.
```

The **Safety** section is an addition to the original guide. Part 2 relies on it.
""")

PROMPT_1_2 = """Review all dbt models in this project against the conventions in AGENTS.md
and fix any violations you find."""

render_prompt("Prompt 1.2", "Audit the Starter Models", PROMPT_1_2)

render_explanation("What this prompt does", """
CoCo should find that `orders_summary.sql` references source tables by their full Snowflake path:

```sql
-- Violation: direct source reference
FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS o
LEFT JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.LINEITEM l ...
```

It rewrites them to go through `_sources.yml`:

```sql
FROM {{ source('tpch', 'orders') }} o
LEFT JOIN {{ source('tpch', 'lineitem') }} l ...
```

Nobody told CoCo what the violation was. It read the conventions, read the code, and connected the two.
""")

PROMPT_1_3 = """Run dbt build --project-dir dbt/ and summarize the result."""

render_prompt("Prompt 1.3", "Confirm the Build", PROMPT_1_3)

st.caption("You can also run `dbt build --project-dir dbt/` yourself in the terminal.")

render_key_concepts([
    {"term": "Why AGENTS.md beats repeating yourself", "definition": "Without it, you re-explain database names, conventions, and commands in every chat. With it, every prompt is grounded in your standards rather than the model's best guess."},
    {"term": "The `cortex` CLI note", "definition": "CoCo has bundled skills that know the `cortex` CLI. Those can activate and make CoCo attempt CLI operations; the AGENTS.md line prevents it."},
    {"term": "When to update AGENTS.md", "definition": "Whenever you find yourself repeating the same context in multiple prompts, move it into AGENTS.md."},
])

render_what_you_built([
    "AGENTS.md with Snowflake context, dbt commands, conventions, and safety rules",
    "orders_summary.sql fixed to use source() references",
    "A clean dbt build in TRICON_DE.DBT_<INITIALS>",
])
