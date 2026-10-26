import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header("A5", "Anomaly Explanation", "10 min", "anomaly-explainer subagent: detect a move beyond X%, decompose by dimension, explain the driver")

st.caption("Builds on the SALES_KPI_VIEW semantic view from A4. Run Prompt A4.1 first if you skipped A4.")

st.markdown(":blue-badge[:material/add_circle: New for Tricon] Not in the original guide. Built on the same AGENTS.md, skill, and subagent pattern from Part 1.")

render_technologies_used([
    {"name": "Contribution analysis", "description": "Splits a metric's change across dimension members. Each member's delta divided by the total delta shows where the move came from.", "icon": "stacked_bar_chart"},
    {"name": "Normalization checks", "description": "Before blaming a segment, check calendar effects such as days in the period or partial months.", "icon": "calendar_month"},
    {"name": "Cortex Analyst", "description": "Every breakdown goes through the semantic view, so the metric definition stays consistent.", "icon": "chat"},
])

PROMPT_A5_1 = """Create a subagent at .cortex/plugins/tricon-de/agents/anomaly-explainer.md named anomaly-explainer.
Description: When a KPI moves more than X% period over period, break it down by dimension and explain what drove the change.
Tools: bash, read, write. Model: auto.

Behavior:
1. Inputs: semantic view (default TRICON_DE.DBT_<INITIALS>.SALES_KPI_VIEW), metric (default net_revenue),
   current period, comparison period, threshold X (default 5%)
2. Compute the change. If |change| <= X, say there is no anomaly, show the change, and stop.
3. Normalization first: compare the per-day metric and the number of days in each period; check for partial periods.
   If normalization explains most of the move, say so plainly before any segment analysis.
4. Decompose the change by each dimension (REGION, MARKET_SEGMENT, ORDER_PRIORITY, ORDER_STATUS): show each member's delta and
   its share of the total delta. Flag members whose share is far out of line with their share of the base.
5. Separate the move into volume (order_count) and price (avg_order_value) effects.
6. Write proposals/anomaly-<metric>-<period>.md: headline, normalized vs raw change, top 3 drivers with numbers,
   and a "what this does NOT tell us" section. Use "contributed" or "associated with" — never claim causation.
Use only numbers returned by queries."""

render_prompt("Prompt A5.1", "Create the anomaly-explainer Subagent", PROMPT_A5_1)

PROMPT_A5_2 = """Use the anomaly-explainer agent: did net revenue in February 1997 move more than 5% versus January 1997? Explain what drove it."""

render_prompt("Prompt A5.2", "Explain a Real Move", PROMPT_A5_2)

render_explanation("What a good answer looks like", """
Net revenue falls about **8%** from January to February 1997 (≈ $2.78B → $2.56B), which clears the 5% threshold, and every region, segment, and priority moves by a similar share.

A naive agent invents a story ("APAC demand softened"). A good one notices February has **28 days vs 31**, normalizes per day, and reports that revenue per day actually **rose about 2%**: the drop is a **calendar effect**, not a demand problem. That's the behavior the normalization step teaches, and it matters for Tricon KPIs like monthly collections and work-order volume.
""")

render_explanation("Turn it into an alert", """
Detection can be cheap and deterministic. A Snowflake **ALERT** runs a SQL condition on a schedule (for example, month-over-month change in net revenue > 5%), and the alert's action notifies a person or triggers this subagent. The agent does the expensive part, the explanation, only when needed. See A7.
""")

render_key_concepts([
    {"term": "Contribution ≠ causation", "definition": "Decomposition shows *where* a change happened, not *why*. The report should end with questions for a person, not conclusions."},
    {"term": "Mix vs. rate", "definition": "Revenue can fall because there were fewer orders (volume) or because orders got smaller (price). Splitting the two changes the conversation."},
])

render_what_you_built([
    "anomaly-explainer subagent with normalization and decomposition",
    "proposals/anomaly-net_revenue-1997-02.md",
])
