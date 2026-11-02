import streamlit as st

st.title("Tricon Data Engineering with CoCo")
st.markdown("Turn your team's data engineering standards — and your recurring operations chores — into reusable, reviewable Cortex Code automations.")

st.space("small")

col1, col2, col3 = st.columns(3)
col1.metric("Modules", "4 + 7", help="4 core engineering modules plus 7 automation workflows")
col2.metric("Prompts", "27", help="Cortex Code prompts across all modules")
col3.metric("Lab time", "2.5 hrs", help="Part 1 hands-on, plus a Part 2 showcase you can try if time allows")

st.space("medium")

st.markdown("#### Why this lab")
with st.container(border=True):
    st.markdown("""
> Anyone can get an AI agent to produce a result. Professionals ensure the right result, every time.

**Part 1** is Jeremiah Hansen's Snowflake guide, [Data Engineering with CoCo](https://www.snowflake.com/en/developers/guides/data-engineering-with-coco/), step by step and prompt for prompt. The only change: everyone builds in their own schema, `DEMO_DB.TPCH_<INITIALS>`, so 30+ people can run it on one account. You encode team standards in an `AGENTS.md`, a custom skill, and a plugin with a production-safety hook and a dbt review subagent, then run that same subagent in CI/CD.

**Part 2** reuses the same pattern for the tasks Tricon asked to automate:

| Area | Workflow | Module |
|------|----------|--------|
| Data engineering | dbt project upkeep: run `dbt build`, triage failing tests, draft simple fixes | A1 |
| Data quality and governance | Sensitive data classification sweep, with masking and tagging proposals routed for approval | A2 |
| Data quality and governance | Monthly access review: excess privileges, dormant users, orphaned roles | A3 |
| Analytics and business reporting | Recurring KPI reports from a semantic view, published as HTML or email | A4 |
| Analytics and business reporting | Anomaly explanation: when a metric moves more than X%, find the driver | A5 |
| Cost and performance | Warehouse right-sizing and/or Adaptive Warehouses | A6 |
| All | Putting these workflows on a schedule | A7 |

**Speakers:** Jeremiah Hansen (Snowflake), author of the Data Engineering with CoCo guide, and Jonathan Regenstein (Snowflake), Industry Principal, Wealth & Asset Management.
""")

st.space("small")

st.markdown("#### The rule for every automation")
with st.container(border=True):
    st.markdown("""
Every Part 2 workflow **proposes**; a person **approves**. The agents draft fixes, policies, findings, and SQL — they never revoke access, apply masking to shared data, resize production warehouses, or push to `main` on their own. This lab builds that boundary in three layers:

1. **Least-privilege roles**: the workshop role `DEMO_ROLE` can only create objects in `DEMO_DB` and use `DEMO_WH`, and `AGENTS.md` plus your dbt profile keep CoCo in your own schema.
2. **A PreToolUse hook**: blocks `dbt ... --target prod` before CoCo can run it.
3. **Approval steps in every skill and subagent**: outputs are written as proposals for review.
""")

st.space("small")

st.markdown("#### Prerequisites")
with st.container(border=True):
    st.markdown("""
- Familiarity with dbt (models, sources, tests), Snowflake, and Git
- If you can, install **CoCo Desktop, Git and dbt** before the lab (Module 0, Step 2): installs can need IT approval. We do the rest of Module 0 together
- Your initials, Snowflake username and account typed into the **sidebar**
- Optional, for Module 4's CI/CD: a GitHub account to fork the repo
- Optional, for modules A3 and A6: the `DEMO_REVIEWER` role (read-only account metadata)

Stuck at any point? **Help & Troubleshooting** in the menu lists every known symptom and its fix.
""")

st.space("medium")
st.caption("Built for Tricon Residential — November 2026 · Part 1 adapted from \"Data Engineering with CoCo\" by Jeremiah Hansen")
