import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_guardrail

render_session_header("A2", "Sensitive Data Classification Sweep", "15 min", "classification-sweep subagent: classify new tables, propose tags and masking, route for approval")

st.markdown(":blue-badge[:material/add_circle: New for Tricon] Not in the original guide. Built on the same AGENTS.md, skill, and subagent pattern from Part 1.")

render_technologies_used([
    {"name": "SYSTEM$CLASSIFY", "description": "Samples a table's columns and recommends semantic categories (EMAIL, PHONE_NUMBER, DATE_OF_BIRTH...) and privacy categories (IDENTIFIER, QUASI_IDENTIFIER, SENSITIVE). Enterprise Edition.", "icon": "policy"},
    {"name": "System tags", "description": "SNOWFLAKE.CORE.SEMANTIC_CATEGORY and PRIVACY_CATEGORY record classification results on columns, and tag-based masking can key off them.", "icon": "sell"},
    {"name": "Masking policies", "description": "Column-level policies that return masked values unless the querying role is allowed to see raw data.", "icon": "visibility_off"},
])

st.markdown("""
**The data:** `dbt seed` in Getting Started loaded `RESIDENT_CONTACTS` into your schema: 40 synthetic residents with names, emails, phones, birth dates, addresses, income, IP addresses, and free-text service notes. It's fake, but shaped like the real thing.
""")

PROMPT_A2_1 = """In TRICON_DE.DBT_<INITIALS>, run:
CALL SYSTEM$CLASSIFY('TRICON_DE.DBT_<INITIALS>.RESIDENT_CONTACTS', {'sample_count': 40});

Do NOT use auto_tag. Summarize the result as a table: column, semantic category, privacy category, confidence.
Then list any columns that standard classification did not flag but that a property manager would still
consider sensitive (for example income, or free-text notes that mention health, disability, or language), and explain why."""

render_prompt("Prompt A2.1", "Classify One Table", PROMPT_A2_1)

render_explanation("Why look past the classifier", """
Standard classification is pattern-based. It reliably catches emails, phones, names, and birth dates. It can miss sensitive content in **free text**: `SERVICE_NOTES` mentions service animals, medical conditions, and language preference, which are fair-housing-sensitive in property management. The agent's job is to flag those for a person, not to decide.

`{'ai_mode': true}` (preview) uses an LLM to find more categories. Try it if your account allows it.
""")

PROMPT_A2_2 = """Create a subagent at .cortex/plugins/tricon-de/agents/classification-sweep.md named classification-sweep.
Description: Sweep a schema for new or changed tables, classify sensitive columns, and propose tags and masking policies for human approval.
Tools: bash, read, write, grep, glob. Model: auto.

Behavior:
1. Input: a fully qualified schema name (ask if not given) and an optional "since" date (default: 30 days ago)
2. Find tables in that schema created or altered since that date, using INFORMATION_SCHEMA.TABLES
3. Run SYSTEM$CLASSIFY on each table WITHOUT auto_tag, one table at a time
4. For every column with a privacy category, plus any free-text column likely to hold sensitive content, propose:
   - ALTER TABLE ... MODIFY COLUMN ... SET TAG statements for SNOWFLAKE.CORE.SEMANTIC_CATEGORY and PRIVACY_CATEGORY
   - One masking policy per data type (string, date, number) that returns the raw value only when
     IS_ROLE_IN_SESSION('TRICON_DE_PII_READER') is true, with partial masking for email and phone
   - ALTER TABLE ... MODIFY COLUMN ... SET MASKING POLICY statements
5. Write two files: proposals/classification-<schema>-<YYYY-MM-DD>.md (findings table, rationale, open questions
   for the data owner) and proposals/classification-<schema>-<YYYY-MM-DD>.sql (all proposed DDL, commented with which finding it addresses)
6. NEVER execute CREATE MASKING POLICY, SET TAG, or SET MASKING POLICY. End by asking who the data owner is and telling me to route the proposal for approval."""

render_prompt("Prompt A2.2", "Create the classification-sweep Subagent", PROMPT_A2_2)

PROMPT_A2_3 = """Use the classification-sweep agent on TRICON_DE.DBT_<INITIALS>.

After it finishes, I'll review the proposal. Once I say approve, apply the approved DDL ONLY to
TRICON_DE.DBT_<INITIALS> (my sandbox), then show me SELECT * FROM RESIDENT_CONTACTS LIMIT 5 so I can confirm the masking."""

render_prompt("Prompt A2.3", "Sweep, Approve, Apply in Your Sandbox", PROMPT_A2_3)

render_guardrail("In the lab, *you* are the approver for your own sandbox schema. In production, route the `.md` and `.sql` files to the data owner or governance team, for example as a PR or a ticket, and let them apply it.")

render_explanation("If applying the masking policy fails", """
Many accounts use **centralized policy management**: only a governance role holds `APPLY MASKING POLICY`. If the apply step fails with a privilege error, that's the control working as designed. Hand the `.sql` proposal to whoever owns policies.

`TRICON_DE_PII_READER` doesn't need to exist for the policy to be valid. Until someone has that role, everyone sees masked values.
""")

render_key_concepts([
    {"term": "Propose, don't apply", "definition": "Classification is probabilistic. Tags and masking change what people can see, so a person decides."},
    {"term": "Tag-based masking", "definition": "A mature next step: attach masking policies to tags so any column tagged EMAIL is masked automatically. The sweep then only proposes tags."},
    {"term": "Sweep cadence", "definition": "Run the sweep on new schemas, or weekly with since = last run. See A7."},
])

render_what_you_built([
    "Classification of RESIDENT_CONTACTS, including free-text sensitivity flags",
    "classification-sweep subagent that writes .md and .sql proposals",
    "Approved masking applied to your sandbox copy only",
])
