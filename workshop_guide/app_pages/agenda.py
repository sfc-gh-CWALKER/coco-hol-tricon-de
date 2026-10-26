import streamlit as st

st.title("Agenda")
st.markdown(
    "A one-day workshop: talks in the morning, then hands-on labs. "
    "The hands-on part is self-paced: everyone does Part 1, then picks the Part 2 workflows that fit their role."
)
st.caption(":material/schedule: Times are tentative and will be confirmed with Tricon.")

st.space("small")

SCHEDULE = [
    ("9:00", "Welcome and goals for the day", "Snowflake account team", None),
    ("9:15", "Data Engineering with CoCo", "Jeremiah Hansen, Snowflake", "Keynote"),
    ("10:00", "What's new from Snowflake Expedition", "Snowflake account team", "Talk"),
    ("10:20", "Break", None, None),
    ("10:30", "Hands-on Part 1: Engineering standards", "Everyone", "Lab"),
    ("11:45", "Lunch", None, None),
    ("12:30", "AI and data in financial services and retail", "Johnathan, Financial & Retail SME", "Talk"),
    ("1:15", "Hands-on Part 2: Automating Tricon's workflows", "Pick by role", "Lab"),
    ("2:45", "Break", None, None),
    ("3:00", "Putting workflows on a schedule", "Everyone", "Discussion"),
    ("3:30", "Tricon priorities, next steps, Q&A", "Tricon and Snowflake", None),
    ("4:00", "Close", None, None),
]

with st.container(border=True):
    for time, title, who, kind in SCHEDULE:
        c1, c2 = st.columns([1, 6])
        c1.markdown(f"**{time}**")
        if who is None:
            c2.markdown(f":gray[{title}]")
        else:
            badge = f" :blue-badge[{kind}]" if kind else ""
            c2.markdown(f"**{title}**{badge}  \n:gray[{who}]")

st.space("medium")

st.markdown("#### Part 1: Engineering standards (everyone, ~75 min)")
st.markdown("Follows Jeremiah Hansen's guide. You build the pieces that every Part 2 workflow reuses.")
PART1 = [
    ("1", "Give CoCo your project context", "AGENTS.md and a conventions audit", "15 min"),
    ("2", "Turn a standard into a skill", "Schema tests, then a `new-dbt-model` skill", "20 min"),
    ("3", "Package it as a plugin", "Prod-safety hook and a `dbt-review` subagent", "25 min"),
    ("4", "Share it and run it in CI", "Plugins Catalog and GitHub Actions", "15 min, optional"),
]
with st.container(border=True):
    for key, title, detail, dur in PART1:
        c1, c2 = st.columns([1, 6])
        c1.markdown(f"**{key}**")
        c2.markdown(f"**{title}** :gray-badge[{dur}]  \n:gray[{detail}]")

st.space("medium")

st.markdown("#### Part 2: Automating Tricon's workflows (pick by role, ~90 min)")
st.markdown("These are the tasks Tricon asked to automate, grouped the same way.")

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
