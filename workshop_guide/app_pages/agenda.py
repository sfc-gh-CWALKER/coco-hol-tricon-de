import streamlit as st

st.title("Agenda")
st.markdown("A 2.5-hour guided lab. Everyone does Part 1 hands-on (Jeremiah Hansen's guide). Part 2 is optional: the facilitator showcases each workflow live, and you can try them yourself if you have time. Any workflow can become your afternoon hackathon project.")

st.space("small")

st.markdown("#### Lab run order (9:30 AM to 12:00 PM PST, tentative)")
LAB_PATH = [
    ("9:30", "Intro and setup check", "15 min"),
    ("9:45", "Part 1, Modules 1 to 3", "60 min"),
    ("10:45", "Part 1, Module 4: plugin sharing and automated PR review", "30 min"),
    ("11:15", "Part 2 showcase, optional hands-on: A1 to A7, then a quick recap", "45 min"),
]
with st.container(border=True):
    for time, title, dur in LAB_PATH:
        c1, c2 = st.columns([1, 6])
        c1.markdown(f"**{time}**")
        c2.markdown(f"{title} :gray-badge[{dur}]")
st.caption("Finish the Getting Started readiness check before lab day; the plan has no time for installs.")

st.space("medium")

st.markdown("#### Part 1: Engineering standards (everyone, ~90 min)")
st.markdown("Follows Jeremiah Hansen's guide. You build the pieces that every Part 2 workflow reuses.")
PART1 = [
    ("1", "Give CoCo your project context", "AGENTS.md and a conventions audit", "15 min"),
    ("2", "Turn a standard into a skill", "Schema tests, then a `new-dbt-model` skill", "20 min"),
    ("3", "Package it as a plugin", "Prod-safety hook and a `dbt-review` subagent", "25 min"),
    ("4", "Share it and run it in CI", "Plugins Catalog and GitHub Actions", "30 min"),
]
with st.container(border=True):
    for key, title, detail, dur in PART1:
        c1, c2 = st.columns([1, 6])
        c1.markdown(f"**{key}**")
        c2.markdown(f"**{title}** :gray-badge[{dur}]  \n:gray[{detail}]")

st.space("medium")

st.markdown("#### Part 2: Automating Tricon's workflows (optional: showcased live, try them if you have time)")
st.markdown("These are the tasks Tricon asked to automate, grouped the same way. If there's no time to build them in the lab, treat them as hackathon ideas.")

PART2 = [
    ("Data engineering", [
        ("A1", "dbt project upkeep",
         "Run `dbt build`, triage failing tests, and draft fixes for simple failures, such as an accepted-values list that needs a new value.",
         "15 min", "Data engineers"),
    ]),
    ("Data quality and governance", [
        ("A2", "Sensitive data classification sweep",
         "Classify new schemas, suggest masking or tagging policies, and route them to a person for approval.",
         "15 min", "Governance, data engineers"),
        ("A3", "Monthly access review",
         "List users with excess privileges, dormant users, and orphaned roles.",
         "10 min", "Admins"),
    ]),
    ("Analytics and business reporting", [
        ("A4", "Recurring KPI reports",
         "Query a semantic view through Cortex Analyst, write a narrative summary, and publish an HTML report or send an email.",
         "15 min", "Analysts, BI developers"),
        ("A5", "Anomaly explanation",
         "When a metric moves by more than X%, break it down by dimension and explain what drove the change.",
         "10 min", "Analysts, BI developers"),
    ]),
    ("Cost and performance", [
        ("A6", "Warehouse right-sizing and Adaptive Warehouses",
         "Find heavy spilling, long queueing, or long idle periods and recommend size or auto-suspend changes. "
         "Then compare with letting an Adaptive Warehouse size compute for mixed workloads like COMPUTE_WH's.",
         "15 min", "Admins"),
    ]),
    ("Running it for real", [
        ("A7", "Putting workflows on a schedule",
         "Turn the workflows above into scheduled automations that people still approve.",
         "10 min", "Everyone"),
    ]),
]

for area, rows in PART2:
    with st.container(border=True):
        st.markdown(f"**{area}**")
        for key, title, detail, dur, who in rows:
            c1, c2 = st.columns([1, 6])
            c1.markdown(f"**{key}**")
            c2.markdown(f"**{title}** :gray-badge[{dur}] :blue-badge[{who}]  \n{detail}")

st.info(
    "Every Part 2 workflow **proposes** and a person **approves**. No agent revokes access, applies masking, "
    "resizes a warehouse, or pushes to `main` on its own.",
    icon=":material/verified_user:",
)

st.space("medium")

st.markdown("#### What you'll have at the end")
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
