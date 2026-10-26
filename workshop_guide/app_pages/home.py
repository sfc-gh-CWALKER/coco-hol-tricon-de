import streamlit as st

st.title("Tricon Data Engineering with CoCo")
st.markdown("Turn your team's data engineering standards — and your recurring operations chores — into reusable, reviewable Cortex Code automations.")

st.space("small")

col1, col2, col3 = st.columns(3)
col1.metric("Modules", "4 + 7", help="4 core engineering modules plus 7 automation workflows")
col2.metric("Prompts", "28", help="Cortex Code prompts across all modules")
col3.metric("Core path", "~75 min", help="Part 1 plus one or two Part 2 workflows")

st.space("medium")

st.markdown("#### Why this lab")
with st.container(border=True):
    st.markdown("""
> Anyone can get an AI agent to produce a result. Professionals ensure the right result, every time.

**Part 1** follows Jeremiah Hansen's Snowflake guide, [Data Engineering with CoCo](https://www.snowflake.com/en/developers/guides/data-engineering-with-coco/). You encode team standards in an `AGENTS.md`, a custom skill, and a plugin with a production-safety hook and a dbt review subagent, then run that same subagent in CI/CD.

**Part 2** reuses the same pattern for the operations work Tricon wants to automate:

| Area | Workflow | Module |
|------|----------|--------|
| Data engineering | dbt project upkeep: run `dbt build`, triage failing tests, draft simple fixes | A1 |
| Data quality & governance | Sensitive data classification sweep with tag and masking proposals | A2 |
| Data quality & governance | Monthly access review: excess privileges, dormant users, orphaned roles | A3 |
| Analytics & reporting | Recurring KPI report from a semantic view, published as HTML or email | A4 |
| Analytics & reporting | Anomaly explanation: when a metric moves more than X%, find the driver | A5 |
| Cost & performance | Warehouse right-sizing and Adaptive Warehouse evaluation | A6 |
| All | Putting these workflows on a schedule | A7 |
""")

st.space("small")

st.markdown("#### The rule for every automation")
with st.container(border=True):
    st.markdown("""
Every Part 2 workflow **proposes**; a person **approves**. The agents draft fixes, policies, findings, and SQL — they never revoke access, apply masking to shared data, resize production warehouses, or push to `main` on their own. This lab builds that boundary in three layers:

1. **Least-privilege roles** — the lab role can only write to your own dbt schema.
2. **A PreToolUse hook** — blocks `dbt ... --target prod` before CoCo can run it.
3. **Approval steps in every skill and subagent** — outputs are written as proposals for review.
""")

st.space("small")

st.markdown("#### Prerequisites")
with st.container(border=True):
    st.markdown("""
- Familiarity with dbt (models, sources, tests), Snowflake, and Git
- **CoCo Desktop**, **Git**, and **dbt Core with dbt-snowflake** installed (see **Getting Started**)
- The `TRICON_DE_ROLE` role and `TRICON_DE_WH` warehouse, both pre-provisioned by your admin
- Optional for modules A3 and A6: the `TRICON_DE_REVIEWER` role (read-only account metadata)
- Your initials entered in the sidebar
""")

st.space("medium")
st.caption("Built for Tricon Residential — November 2026 · Part 1 adapted from \"Data Engineering with CoCo\" by Jeremiah Hansen")
