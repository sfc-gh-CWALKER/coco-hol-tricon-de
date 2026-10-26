import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_guardrail

render_session_header("A3", "Monthly Access Review", "10 min", "access-review subagent: excess privileges, dormant users, orphaned roles")

st.info(":material/key: **Requires the `TRICON_DE_REVIEWER` role** (read-only account metadata, granted by your admin). Without it, follow along with the facilitator's demo, or build the subagent now and run it later.")

render_technologies_used([
    {"name": "ACCOUNT_USAGE views", "description": "USERS, ROLES, GRANTS_TO_USERS, GRANTS_TO_ROLES, and LOGIN_HISTORY. Account-wide security metadata, with up to about 2 hours of latency.", "icon": "admin_panel_settings"},
    {"name": "SECURITY_VIEWER", "description": "The SNOWFLAKE database role that grants read access to the security views. It can read metadata only; it can't change grants.", "icon": "shield"},
    {"name": "Report-only subagent", "description": "Finds issues and recommends actions. It never runs REVOKE, ALTER USER, or DROP ROLE.", "icon": "fact_check"},
])

PROMPT_A3_1 = """Create a subagent at .cortex/plugins/tricon-de/agents/access-review.md named access-review.
Description: Produce a monthly Snowflake access review: excess privileges, dormant users, and orphaned roles. Report only.
Tools: bash, read, write. Model: auto.

Behavior:
1. Use role TRICON_DE_REVIEWER. Query SNOWFLAKE.ACCOUNT_USAGE (exclude deleted users and roles).
2. Excess privileges: users holding ACCOUNTADMIN, SECURITYADMIN, SYSADMIN, USERADMIN or ORGADMIN directly or through
   inheritance; roles granted OWNERSHIP or MANAGE GRANTS on the account; any grant of these admin roles to PUBLIC.
3. Dormant users: enabled users with no successful login in 90 days, or who never logged in and were created more than 30 days ago.
   Show last login, owner, default role, and whether the user is a person or a service (TYPE column).
4. Orphaned roles: custom roles not granted to any user or role, and roles with no privileges at all.
5. Also flag: person users without MFA, and users with ACCOUNTADMIN as their default role.
6. Write proposals/access-review-<YYYY-MM>.md with a summary table of counts, one section per finding with the
   evidence query, and a recommended action per row (keep / disable / revoke / investigate). Put suggested SQL in
   commented code blocks only.
7. NEVER execute REVOKE, ALTER USER, DROP ROLE, or GRANT. State the ACCOUNT_USAGE latency caveat at the top of the report."""

render_prompt("Prompt A3.1", "Create the access-review Subagent", PROMPT_A3_1)

PROMPT_A3_2 = """Use the access-review agent to produce this month's access review."""

render_prompt("Prompt A3.2", "Run the Review", PROMPT_A3_2)

render_guardrail("The report recommends; a security owner decides. Service users often look dormant or over-privileged by design, so the agent should mark them *investigate* rather than *disable*.")

render_explanation("Make it Tricon's", """
- Add an **allow-list** of known break-glass and service accounts to the subagent so they're annotated rather than flagged.
- Adjust the dormancy threshold (90 days) to match Tricon's policy.
- Have the subagent compare against last month's report and highlight **new** findings only.
""")

render_key_concepts([
    {"term": "Why report-only", "definition": "A wrong REVOKE can break a pipeline or lock out an admin. Access changes stay with SECURITYADMIN under Tricon's change process."},
    {"term": "Least privilege for the reviewer", "definition": "TRICON_DE_REVIEWER can read security metadata but can't change it. It's also sensitive: query history and grant lists reveal a lot, so grant it to admins only."},
])

render_what_you_built([
    "access-review subagent (report-only)",
    "proposals/access-review-<YYYY-MM>.md with findings and recommended actions",
])
