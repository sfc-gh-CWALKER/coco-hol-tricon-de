import streamlit as st

st.title("A7: Put It on a Schedule")
st.markdown("You now have the workflows. Here's how each could run on its own, with the approval step kept in place. Treat this as a discussion for hackathon week; pick one and pilot it.")

st.space("small")

st.markdown("#### Scheduling options")
st.markdown("""
| Option | Runs where | Good for | Notes |
|--------|-----------|----------|-------|
| **GitHub Actions** (cron or PR) | GitHub runners with the CoCo CLI | dbt-review on PRs, nightly dbt-test-triage that opens a fix PR | Needs a Tricon-approved service user and network policy (Module 4) |
| **Snowflake Task + stored procedure** | Inside Snowflake | Deterministic SQL: access-review queries into a history table, warehouse metrics snapshots | No LLM needed. Cheapest and most predictable |
| **Snowflake Alert** | Inside Snowflake | Threshold detection, for example net revenue MoM > 5% | The alert action notifies a person, who then runs anomaly-explainer |
| **CoCo Desktop automations** | Your laptop, while Desktop is open | Personal recurring reports (kpi-report, monthly access review) | Same tools and approvals as an interactive chat |
| **CoCo cloud automations** | Snowflake-managed sandbox | Unattended recurring agent runs while laptops are closed | Check availability and required privileges in Tricon's account first |
""")

st.space("small")

st.markdown("#### Suggested mapping")
st.markdown("""
| Workflow | Trigger | Automated part | Human step |
|----------|---------|----------------|------------|
| A1 dbt upkeep | Nightly, after the dbt job | Build, triage, draft the fix on a `fix/` branch, open a PR | Approve and merge the PR |
| A2 Classification | New schema, or weekly | Classify, write the `.md` and `.sql` proposal | Data owner approves; governance applies |
| A3 Access review | 1st of the month | Report with recommended actions | Security owner decides on revocations |
| A4 KPI report | Monthly, after close | Numbers, narrative, HTML | Review, then send |
| A5 Anomaly | Snowflake Alert on threshold | Explanation report | Analyst validates the drivers |
| A6 Warehouses | Monthly | Ranked proposals with rollback | Admin pilots the changes |
""")

st.space("small")

with st.container(border=True):
    st.markdown("""
#### :material/verified_user: Keep the boundary as you automate

- Scheduled runs use a **dedicated, least-privilege role**, never a person's admin role.
- Outputs go to a place a person reviews: a PR, a ticket, or an email to an owner.
- Anything that changes access, masking, or compute stays behind an explicit approval.
- Log every run (inputs, queries, outputs) so findings are auditable.
""")

st.space("small")
st.markdown("#### Hackathon ideas")
st.markdown("""
- Point `kpi-report` at a Tricon occupancy and rent-growth semantic view and reconcile it with Power BI.
- Turn `dbt-test-triage` into a nightly GitHub Action for the India team's dbt project.
- Add Tricon's break-glass allow-list and a month-over-month diff to `access-review`.
- Run `warehouse-advisor`, then pilot an Adaptive Warehouse on COMPUTE_WH for one week with before/after metrics.
""")
st.caption("Reference versions of every skill and subagent: `solutions/tricon-de-plugin/` in the repo.")
