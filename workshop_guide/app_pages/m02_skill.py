import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_code, render_guide_change, render_new_for_tricon

render_session_header("Module 2", "Tests & a Custom Skill", "20 min", "Schema tests, a new-dbt-model skill, and a supplier_performance model built with it")

render_technologies_used([
    {"name": "Agent Skills", "description": "A folder with a SKILL.md file: YAML frontmatter (name, description) plus Markdown instructions for a repeatable workflow.", "icon": "auto_fix_high"},
    {"name": "Project skills", "description": "CoCo auto-discovers skills in .snowflake/cortex/skills/ inside the open workspace, with no install step.", "icon": "folder_special"},
    {"name": "dbt schema tests", "description": "not_null, unique, accepted_values, and other checks that run on every dbt build.", "icon": "fact_check"},
])

st.markdown("#### Step 1: CoCo without a skill")
st.markdown("For common tasks, you can just ask. CoCo already knows dbt test syntax and how `_schema.yml` is structured.")

PROMPT_2_1 = """Add schema tests to the existing models in this project.
Save the results in dbt/models/_schema.yml.
At a minimum, each model's primary key should have not_null and unique tests.
Add any other tests that make sense given the columns in each model.
For parameterized tests like accepted_values, nest all test parameters under an arguments: key.
Then run dbt build --project-dir dbt/."""

render_guide_change(
    "Same prompt, and you run `dbt build` yourself afterwards.",
    "The final line \"Then run dbt build --project-dir dbt/.\" is appended.",
    "Saves a step; the result is the same.")

render_prompt("Prompt 2.1", "Add Schema Tests (No Skill)", PROMPT_2_1)

render_explanation("What this demonstrates", """
CoCo finds the primary keys (`customer_key`, `order_key`), writes `_schema.yml`, and picks sensible column tests on its own.

We still had to name the file `_schema.yml`; otherwise CoCo defaults to `schema.yml`. **The model knows the tool, not your team's choices.** It doesn't know that you always use `dbt build`, that every primary key needs tests, or that raw tables must go through `_sources.yml`. That is what a custom skill is for.

:material/info: If a test fails, check the message. Not every column that looks like a key is unique in TPC-H.
""")

st.markdown("#### Step 2: Write a custom skill")
st.markdown("Rule of thumb: if you find yourself starting a prompt with *\"remember, we always...\"*, that's a skill waiting to be written. Create the folder first:")
render_code("mkdir -p .snowflake/cortex/skills/new-dbt-model")

PROMPT_2_2 = """Create a custom skill at .snowflake/cortex/skills/new-dbt-model/SKILL.md for creating
new dbt models in this project.

The skill should have exactly two sections:

# Conventions — a numbered list of these three rules:
1. Always use `dbt build` (not `dbt run`) so tests run together with compilation
2. Every model's primary key must have not_null and unique tests in _schema.yml
3. All raw tables must be referenced through _sources.yml using source() — never reference the source database directly in model SQL

# Workflow — a numbered list of these four steps:
1. Confirm which source table(s) to model — ask if not specified
2. Write the model SQL using source() references
3. Add the model entry to _schema.yml with a description and primary key tests
4. Run dbt build --select <model_name> --project-dir dbt/ and report the result

Use the name new-dbt-model. Write a one-sentence description that tells CoCo when
to invoke this skill. Keep the skill concise — no sub-steps, no examples, no error
handling instructions. The model is smart enough to infer the details."""

st.caption(":green-badge[Same as original guide] Prompts 2.2 and 2.3 are word-for-word from the guide.")

render_prompt("Prompt 2.2", "Create the new-dbt-model Skill", PROMPT_2_2)

render_explanation("What a good SKILL.md looks like", """
```markdown
---
name: new-dbt-model
description: Create a new dbt model in this project. Use when adding a model for a new source table or analytical use case.
---

# Conventions

1. Always use `dbt build` (not `dbt run`) so tests run together with compilation.
2. Every model's primary key must have `not_null` and `unique` tests in `_schema.yml`.
3. Reference all raw tables through `_sources.yml`. Never reference the source database directly in model SQL.

# Workflow

1. Confirm which source table(s) to model — ask if not specified.
2. Write the model SQL in `dbt/models/<model_name>.sql` using `{{ source('<source>', '<table>') }}` references.
3. Add the model entry to `dbt/models/_schema.yml` with a description and tests for the primary key.
4. Run `dbt build --select <model_name> --project-dir dbt/` and report the result.
```

The `description` field is how CoCo decides when to use the skill automatically, so write it as a clear trigger.
""")

st.markdown("#### Step 3: Use the skill")

PROMPT_2_3 = """Use the new-dbt-model skill to create a supplier_performance model.
It should summarize performance metrics per supplier from the supplier and lineitem source tables.
Include total orders, total revenue, and average discount."""

render_prompt("Prompt 2.3", "Build a Model with the Skill", PROMPT_2_3)

render_explanation("What to watch for", """
CoCo matches your prompt to the skill's description, then follows the workflow in order:

1. Finds `supplier` and `lineitem` in `_sources.yml`
2. Writes `dbt/models/supplier_performance.sql` with `source()` references
3. Adds the model to `_schema.yml` with primary key tests
4. Runs `dbt build --select supplier_performance --project-dir dbt/`

You never repeated a convention. That's the difference between a one-off prompt and a skill.
""")

render_key_concepts([
    {"term": "Bundled vs. custom skills", "definition": "Bundled skills (shipped by Snowflake) cover Snowflake-specific workflows such as dynamic tables and Iceberg. Custom skills encode *your* team's choices: conventions, step order, guardrails."},
    {"term": "Skill best practices", "definition": "Keep skills under 500 lines, write the description as a specific trigger, and don't repeat general knowledge. Test a skill by checking whether CoCo follows every convention without extra prompting."},
    {"term": "Keep skills focused", "definition": "A narrow \"create a new dbt model\" skill is more useful than one that tries to cover everything dbt-related."},
])

render_what_you_built([
    "dbt/models/_schema.yml with primary key and column tests",
    "new-dbt-model project skill",
    "supplier_performance model built and tested by the skill",
])
