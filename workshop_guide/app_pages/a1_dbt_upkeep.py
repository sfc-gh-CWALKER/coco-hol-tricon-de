import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_guardrail

render_session_header("A1", "dbt Project Upkeep", "15 min", "dbt-test-triage skill: run the build, triage failing tests, draft simple fixes for review")

render_technologies_used([
    {"name": "dbt build results", "description": "dbt writes run results to target/run_results.json, so the agent can tell which tests failed and why.", "icon": "fact_check"},
    {"name": "Custom skill", "description": "Encodes Tricon's triage rules: which failures are safe to auto-draft and which always go to a person.", "icon": "auto_fix_high"},
    {"name": "Fix branch + proposal", "description": "Fixes land on a fix/ branch with a written explanation. Nothing reaches main without a PR.", "icon": "call_split"},
])

st.markdown("""
**The scenario:** a teammate added an `accepted_values` test on `orders_summary.order_status`, but listed only two of the three statuses that appear in the data. The nightly build now fails. That's the textbook "the list needs a new value" failure.
""")

PROMPT_A1_1 = """Simulate a teammate's change: in dbt/models/_schema.yml, add (or replace) an accepted_values
test on orders_summary.order_status with values ['F', 'O'] only. Nest the parameters under an
arguments: key. Then run dbt build --project-dir dbt/ and show me which tests failed."""

render_prompt("Prompt A1.1", "Plant the Failing Test", PROMPT_A1_1)
st.caption("Expected: the accepted_values test fails because TPC-H also contains status 'P' (partially fulfilled orders).")

PROMPT_A1_2 = """Create a skill at .cortex/plugins/tricon-de/skills/dbt-test-triage/SKILL.md named dbt-test-triage.
Description: Triage failing dbt tests after a build and draft fixes for simple failures. Use when dbt build fails or for routine project upkeep.

# Conventions
1. Never edit models or tests on main. Create a branch named fix/<short-description> before changing anything.
2. Only draft a fix automatically for SIMPLE failures: an accepted_values list missing a legitimate value, a relationships test pointing at a renamed column, or a stale source column name. Everything else is REPORT ONLY.
3. Before proposing a new accepted value, query the actual distinct values and their row counts, and say whether the new value looks legitimate or like bad data.
4. Never weaken a test by deleting it, adding a where: clause, or changing severity unless I explicitly approve.
5. Write a triage report to proposals/dbt-triage-<YYYY-MM-DD>.md and stop for my approval before committing.

# Workflow
1. Run dbt build --project-dir dbt/ and read target/run_results.json
2. For each failure: test name, model, column, failing row count, and a sample of failing values
3. Classify each failure as SIMPLE (draft fix), DATA ISSUE (report upstream), or NEEDS INVESTIGATION
4. For SIMPLE failures, show the exact diff you propose and the evidence behind it
5. Write the triage report, then ask me to approve, edit, or reject each fix
6. After approval: apply the fix on the fix/ branch, rerun dbt build --select <model> --project-dir dbt/, and commit

Keep the skill concise."""

render_prompt("Prompt A1.2", "Create the dbt-test-triage Skill", PROMPT_A1_2)

PROMPT_A1_3 = """Use the dbt-test-triage skill to triage the current dbt build."""

render_prompt("Prompt A1.3", "Run the Triage", PROMPT_A1_3)

render_guardrail("Read the triage report and the proposed diff before you reply *approve*. The agent should show the distinct values of `order_status` (F, O, P), explain that `P` means partially fulfilled, and propose adding `P` to the list on a `fix/` branch.")

render_explanation("Extend it", """
- **Run it nightly.** See A7. A GitHub Actions cron job can run this skill and open a PR with the fix and the report as its description.
- **Add Tricon rules.** For example: "accepted values for `LEASE_STATUS` must match the Yardi code list in `seeds/lease_status_codes.csv`."
- **Pair it with dbt-review.** The PR that dbt-test-triage opens is reviewed by the Module 3 subagent, so one agent proposes and another checks.
""")

render_key_concepts([
    {"term": "Why the SIMPLE list is explicit", "definition": "Agents happily \"fix\" a failing test by deleting it. Spelling out which failures may be drafted, and which never may, keeps upkeep from silently lowering your quality bar."},
    {"term": "Evidence before edits", "definition": "Requiring distinct values and row counts turns \"add P to the list\" from a guess into a reviewable decision."},
])

render_what_you_built([
    "dbt-test-triage skill in the tricon-de plugin",
    "Triage report in proposals/ with classified failures",
    "Approved fix on a fix/ branch, rebuilt and committed",
])
