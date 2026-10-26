import streamlit as st

st.title("Agenda")
st.markdown("Self-paced. Part 1 is the shared core; then each person or team picks **one or two** Part 2 workflows that match their role. Facilitators set the clock times.")

st.space("small")

PART1 = [
    ("1", "AGENTS.md — project context and a conventions audit", "15 min"),
    ("2", "Schema tests without a skill, then a custom new-dbt-model skill", "20 min"),
    ("3", "Plugin: move the skill, add a prod-safety hook and a dbt-review subagent", "25 min"),
    ("4", "Share via the Plugins Catalog; run the subagent in GitHub Actions", "15 min, optional"),
]
PART2 = [
    ("A1", "dbt upkeep: triage a failing test and draft the fix", "15 min", "Data engineers"),
    ("A2", "Classification sweep with tag and masking proposals", "15 min", "Governance, data engineers"),
    ("A3", "Monthly access review report", "10 min", "Admins (reviewer role)"),
    ("A4", "KPI report from a semantic view, as HTML or email", "15 min", "Analysts, BI developers"),
    ("A5", "Anomaly explanation over the semantic view", "10 min", "Analysts, BI developers"),
    ("A6", "Warehouse right-sizing and Adaptive Warehouse evaluation", "15 min", "Admins (reviewer role)"),
    ("A7", "Putting workflows on a schedule (discussion)", "10 min", "Everyone"),
]

st.markdown("##### Part 1: Engineering standards")
for key, title, dur in PART1:
    c1, c2 = st.columns([1, 6])
    c1.markdown(f"**{key}**")
    c2.markdown(f":material/play_circle: {title} :gray-badge[{dur}]")

st.space("small")
st.markdown("##### Part 2: Automation workflows (pick one or two)")
for key, title, dur, who in PART2:
    c1, c2 = st.columns([1, 6])
    c1.markdown(f"**{key}**")
    c2.markdown(f":material/play_circle: {title} :gray-badge[{dur}] :blue-badge[{who}]")

st.space("medium")

st.markdown("##### What you'll have at the end")
st.markdown("""
| Artifact | Where |
|----------|-------|
| `AGENTS.md` | Project root |
| `tricon-de` plugin: `new-dbt-model` and `dbt-test-triage` skills, prod-safety hook, `dbt-review` subagent | `.cortex/plugins/tricon-de/` |
| Automation subagents: classification sweep, access review, KPI report, anomaly explainer, warehouse advisor | `.cortex/plugins/tricon-de/agents/` |
| dbt models, tests, and a semantic view in your own schema | `TRICON_DE.DBT_<INITIALS>` |
| Proposal files for every approval step | `proposals/` |
| Optional GitHub Actions PR review | `.github/workflows/pr-review.yml` |
""")
st.caption("Stuck? Reference versions of every skill and subagent are in `solutions/tricon-de-plugin/` in the repo.")
