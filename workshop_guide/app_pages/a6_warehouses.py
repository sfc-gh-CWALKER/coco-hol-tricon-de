import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_guardrail

render_session_header("A6", "Warehouse Right-Sizing & Adaptive Warehouses", "15 min", "warehouse-advisor subagent and an Adaptive Warehouse evaluation for COMPUTE_WH")

st.info(":material/key: **Requires the `TRICON_DE_REVIEWER` role** (usage and query-history metadata). Changing a warehouse stays with Tricon's Snowflake admin.")

render_technologies_used([
    {"name": "Usage & load history", "description": "WAREHOUSE_METERING_HISTORY (credits), WAREHOUSE_LOAD_HISTORY (queueing), and QUERY_HISTORY (spilling, queue time, duration).", "icon": "monitoring"},
    {"name": "Right-sizing signals", "description": "Remote spill means the warehouse is too small. Sustained queueing means you need more clusters. Credits with little query time means idle cost, so lower AUTO_SUSPEND.", "icon": "speed"},
    {"name": "Adaptive Warehouses", "description": "Snowflake sizes and scales compute per query. You set MAX_QUERY_PERFORMANCE_LEVEL and QUERY_THROUGHPUT_MULTIPLIER instead of size and clusters. Enterprise Edition, select regions.", "icon": "auto_mode"},
])

PROMPT_A6_1 = """Create a subagent at .cortex/plugins/tricon-de/agents/warehouse-advisor.md named warehouse-advisor.
Description: Find warehouses with heavy spilling, long queueing, or long idle periods and recommend size, auto-suspend, cluster, or Adaptive Warehouse changes. Report only.
Tools: bash, read, write. Model: auto.

Behavior:
1. Use role TRICON_DE_REVIEWER. Look back 30 days (configurable).
2. Per warehouse, from SNOWFLAKE.ACCOUNT_USAGE:
   - credits (WAREHOUSE_METERING_HISTORY), query count, p50/p95 elapsed time
   - % of queries with local spill and with remote spill, total GB spilled (QUERY_HISTORY)
   - avg and p95 queued_overload_time, and hours with avg_queued_load > 0 (WAREHOUSE_LOAD_HISTORY)
   - idle ratio: metered hours with little or no query execution time
   - current size, type, auto_suspend, min/max clusters, scaling policy (SHOW WAREHOUSES)
3. Rules of thumb: remote spill on more than 5% of queries -> consider one size up for those workloads;
   sustained queueing -> more max clusters, or Adaptive; idle ratio over 40% or AUTO_SUSPEND over 300s -> lower auto-suspend;
   mixed workloads with very different query sizes on one warehouse -> Adaptive Warehouse candidate
4. Estimate the credit impact of each recommendation as a range, and say what would make the estimate wrong
5. Write proposals/warehouse-review-<YYYY-MM-DD>.md with a ranked table (warehouse, finding, recommendation, est. impact,
   confidence) and the ALTER WAREHOUSE statements in commented code blocks, each with its rollback statement
6. NEVER execute ALTER WAREHOUSE, CREATE WAREHOUSE, or SYSTEM$BULK_UPDATE_WH."""

render_prompt("Prompt A6.1", "Create the warehouse-advisor Subagent", PROMPT_A6_1)

PROMPT_A6_2 = """Use the warehouse-advisor agent for the last 30 days."""

render_prompt("Prompt A6.2", "Run the Right-Sizing Review", PROMPT_A6_2)

st.markdown("#### Adaptive Warehouses for mixed workloads like COMPUTE_WH")
st.markdown("""
An **Adaptive Warehouse** removes the size, multi-cluster, and auto-suspend tuning above. Snowflake picks resources per query, and you control two properties:

- `MAX_QUERY_PERFORMANCE_LEVEL`: the upper bound for any single query, as a t-shirt size (default `XLARGE`)
- `QUERY_THROUGHPUT_MULTIPLIER`: how much total work can run at once (default `2`; `0` = unlimited)

Converting is an online operation (`ALTER WAREHOUSE ... SET WAREHOUSE_TYPE = 'ADAPTIVE'`) and can be reversed (`'STANDARD'`). Billing is per query. Budgets and resource monitors still apply.
""")

PROMPT_A6_3 = """Using role TRICON_DE_REVIEWER, evaluate whether COMPUTE_WH is a good candidate for an Adaptive Warehouse. Do not change anything.
1. Confirm prerequisites: account edition and whether our cloud region supports Adaptive Warehouses (check the docs), and COMPUTE_WH's current type and size
2. Profile the last 30 days: query mix by type and user, spread of bytes scanned and duration (is this a mixed BI + ETL workload?), queueing, spilling, credits
3. Note any blockers: HTAP-heavy use, very-low-latency dashboard queries (interactive warehouses fit better), Snowpark-optimized needs
4. Recommend: convert / don't convert / pilot. For a pilot, give the ALTER WAREHOUSE statement, suggested MAX_QUERY_PERFORMANCE_LEVEL
   and QUERY_THROUGHPUT_MULTIPLIER with reasoning, the rollback statement, a resource monitor or budget guardrail, and the
   before/after metrics to compare after one week (credits per query, p95 latency, queued time) with the QUERY_METERING_HISTORY query to measure them
Write it to proposals/adaptive-compute_wh-<YYYY-MM-DD>.md."""

render_prompt("Prompt A6.3", "Evaluate COMPUTE_WH for Adaptive", PROMPT_A6_3)

render_guardrail("Warehouse changes affect cost and every workload on the warehouse. The lab role can't run `ALTER WAREHOUSE`. The proposal goes to Tricon's Snowflake admin, who can run a one-week pilot with the rollback statement ready.")

render_explanation("Facilitator demo (optional)", """
If the admin set up `TRICON_DE_ADAPTIVE_DEMO_WH` (see `admin/setup.sql`), the facilitator can show the conversion live:

```sql
SHOW WAREHOUSES LIKE 'TRICON_DE_ADAPTIVE_DEMO_WH';
ALTER WAREHOUSE TRICON_DE_ADAPTIVE_DEMO_WH SET WAREHOUSE_TYPE = 'ADAPTIVE';
SHOW WAREHOUSES LIKE 'TRICON_DE_ADAPTIVE_DEMO_WH';   -- note MAX_QUERY_PERFORMANCE_LEVEL, QUERY_THROUGHPUT_MULTIPLIER
ALTER WAREHOUSE TRICON_DE_ADAPTIVE_DEMO_WH SET WAREHOUSE_TYPE = 'STANDARD';   -- rollback
```

Snowflake derives the Adaptive settings from the warehouse's existing size, cluster count, and QAS configuration.
""")

render_key_concepts([
    {"term": "Right-size first or go Adaptive?", "definition": "For a few steady, well-understood warehouses, tuning is enough. For mixed, bursty workloads where queries range from tiny to large, Adaptive removes the tuning problem."},
    {"term": "Measure, don't assume", "definition": "Treat any savings estimate as a hypothesis. A one-week pilot with before/after metrics from QUERY_METERING_HISTORY is the evidence."},
])

render_what_you_built([
    "warehouse-advisor subagent (report-only)",
    "Ranked right-sizing proposals with rollback statements",
    "Adaptive Warehouse evaluation and pilot plan for COMPUTE_WH",
])
