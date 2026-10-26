import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_guardrail

render_session_header("A4", "Recurring KPI Report", "15 min", "Semantic view over your dbt models + kpi-report subagent publishing HTML (and optional email)")

st.markdown(":blue-badge[:material/add_circle: New for Tricon] Not in the original guide. Built on the same AGENTS.md, skill, and subagent pattern from Part 1.")

render_technologies_used([
    {"name": "Semantic view", "description": "Business definitions (metrics, dimensions, relationships) as a Snowflake object, so every report uses the same math.", "icon": "description"},
    {"name": "Cortex Analyst", "description": "Turns natural-language KPI questions into SQL using the semantic view.", "icon": "chat"},
    {"name": "HTML report / email", "description": "A self-contained HTML file written locally, or sent through SYSTEM$SEND_EMAIL with an admin-approved notification integration.", "icon": "summarize"},
])

PROMPT_A4_1 = """Create a semantic view TRICON_DE.DBT_<INITIALS>.SALES_KPI_VIEW over my dbt models ORDERS_SUMMARY and CUSTOMERS.
- Relationship: ORDERS_SUMMARY.CUSTOMER_KEY -> CUSTOMERS.CUSTOMER_KEY (left = ORDERS_SUMMARY, right = CUSTOMERS;
  primary key CUSTOMER_KEY on CUSTOMERS; do not specify join_type)
- Dimensions: ORDER_DATE (time), ORDER_STATUS, ORDER_PRIORITY, REGION, NATION, MARKET_SEGMENT
- Metrics: net_revenue = SUM(TOTAL_NET_PRICE), order_count = COUNT(ORDER_KEY), avg_order_value = net_revenue / order_count,
  active_customers = COUNT(DISTINCT CUSTOMER_KEY)
- AI_SQL_GENERATION instruction: data is TPC-H with order dates from 1992-01 to 1998-08; August 1998 is a partial month,
  so "latest month" means the latest COMPLETE month (July 1998)
Execute it, then ask Cortex Analyst: "What was net revenue by region last month?" and show the SQL."""

render_prompt("Prompt A4.1", "Create the Semantic View", PROMPT_A4_1)

PROMPT_A4_2 = """Create a subagent at .cortex/plugins/tricon-de/agents/kpi-report.md named kpi-report.
Description: Produce the recurring KPI report from a semantic view with a written narrative, as a self-contained HTML file.
Tools: bash, read, write. Model: auto.

Behavior:
1. Input: semantic view (default TRICON_DE.DBT_<INITIALS>.SALES_KPI_VIEW) and reporting month (default: latest complete month)
2. Ask Cortex Analyst for: net revenue, order count, avg order value, and active customers for the month, prior month,
   and same month last year; net revenue by region and by market segment; top 5 nations by revenue growth
3. Only use numbers returned by those queries. Never estimate or invent figures. Keep the SQL for each number.
4. Write a 150-word executive narrative: headline, what moved, and one question worth asking. No causal claims without evidence.
5. Write reports/kpi-<YYYY-MM>.html: self-contained (inline CSS, no external scripts), with KPI cards, a MoM/YoY table,
   the narrative, and an appendix with the SQL behind every number
6. Email is OPTIONAL and only on my explicit approval: if I say "send it", call SYSTEM$SEND_EMAIL with integration
   TRICON_DE_EMAIL_INT to the address I give, with the narrative as the body and the report path noted"""

render_prompt("Prompt A4.2", "Create the kpi-report Subagent", PROMPT_A4_2)

PROMPT_A4_3 = """Use the kpi-report agent for July 1998, then open the HTML report."""

render_prompt("Prompt A4.3", "Generate the Report", PROMPT_A4_3)
st.caption("Tip: run `coco reports/` in the terminal, or open the file from the Explorer.")

render_guardrail("Read the numbers and narrative before sending anything. Emails go out only when you say *send it*, and only through the admin-created `TRICON_DE_EMAIL_INT` integration. Snowflake email integrations can only send to verified users' addresses.")

render_explanation("Bring it to Tricon data", """
The same pattern works on a Tricon semantic view of occupancy, rent growth, turnover, and delinquency. That's how this lab connects to the Power BI reporting work: define the KPI once in the semantic view, and the report, the agent, and Cortex Analyst all agree with Power BI. Reconcile a few numbers against the existing Power BI report before trusting it.
""")

render_key_concepts([
    {"term": "Why the SQL appendix", "definition": "Every number in a generated report should be traceable. The appendix makes the report auditable and makes Power BI reconciliation quick."},
    {"term": "HTML vs. email vs. Snowflake Intelligence", "definition": "Start with HTML files you review. Add email once the content is trusted. Teams on Snowflake Intelligence can publish the same HTML as a shared report artifact."},
])

render_what_you_built([
    "SALES_KPI_VIEW semantic view over your dbt models",
    "kpi-report subagent with a narrative and SQL appendix",
    "reports/kpi-1998-07.html",
])
