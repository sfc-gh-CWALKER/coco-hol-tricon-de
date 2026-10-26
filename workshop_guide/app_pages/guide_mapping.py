import streamlit as st

st.title("Guide Mapping")
st.markdown("""
Part 1 follows Jeremiah Hansen's [Data Engineering with CoCo](https://www.snowflake.com/en/developers/guides/data-engineering-with-coco/) section by section, using **the same prompts** with Tricon object names. Part 2 is new. This page lists every difference, so anyone who has run the original guide can run this one.

:orange-badge[Adjusted for Tricon] marks a deliberate change to an original step. :blue-badge[New for Tricon] marks content that isn't in the original.
""")

st.markdown("#### Section-by-section")
st.markdown("""
| Original guide section | This lab | Status |
|---|---|---|
| Overview / What is Cortex Code? | Home | Condensed |
| Setup: fork & clone | Getting Started, Step 2 | :orange-badge[Adjusted] Clone `sfc-gh-cwalker/coco-hol-tricon-de` (fork only for CI/CD) |
| Setup: run `scripts/setup.sql` | `admin/ADMIN_GUIDE.md` + scripts, run by Tricon's admin | :orange-badge[Adjusted] Pre-provisioned; attendees get no ownership or DDL rights |
| Setup: create a PAT + network-policy bypass | — | :orange-badge[Adjusted] Removed; dbt uses SSO (`externalbrowser`) |
| Setup: configure dbt / `dbt debug` | Getting Started, Steps 4–5 | :orange-badge[Adjusted] `tricon_de` profile, per-attendee schema, plus `dbt seed` |
| Create an AGENTS.md | Module 1, Prompts 1.1–1.3 | :orange-badge[Adjusted] Prompt 1.1 adds two lines: safety rules, and ignore lab folders |
| What is a Skill? / Using CoCo Without a Skill | Module 2, Prompt 2.1 | Same prompt, plus "then run dbt build" |
| Create a Custom Skill | Module 2, Prompts 2.2–2.3 | Identical prompts |
| What is a Plugin? / Create a Custom Plugin | Module 3, Prompts 3.1–3.5 | Same prompts; plugin renamed `coco-de-guide` → `tricon-de`, manifest adds `description` |
| Publish to the Plugin Catalog | Module 4, Option A | Same steps; object is `...SKILL_SHARING.TRICON_DE` |
| Enforce Standards in CI/CD | Module 4, Option B, Prompt 4.1 | Identical prompt; :orange-badge[Adjusted] auth guidance (service user, no bypass) |
| — | Modules A1–A7 | :blue-badge[New] Tricon's automation list |
""")

st.markdown("#### Name substitutions")
st.markdown("""
| Original | This lab |
|---|---|
| `DEMO_ROLE` | `TRICON_DE_ROLE` |
| `DEMO_WH` | `TRICON_DE_WH` |
| `DEMO_DB` | `TRICON_DE` |
| `TPCH_TRANSFORMED` | `DBT_<INITIALS>` (one per attendee) |
| dbt profile/project `coco_de_guide` | `tricon_de` |
| plugin `coco-de-guide` | `tricon-de` |
| `sfguide-data-engineering-with-coco` repo | `coco-hol-tricon-de` repo (same `dbt/` starter, including the planted `orders_summary` violation) |
""")

st.markdown("#### Starter repo additions")
st.markdown("""
| Path | Purpose | Affects Part 1? |
|---|---|---|
| `dbt/seeds/resident_contacts.csv` | Synthetic PII for A2 | `dbt build` also loads this seed. No effect on the conventions or on dbt-review |
| `solutions/tricon-de-plugin/` | Reference skill, subagents, hook | No. Not auto-discovered, and AGENTS.md tells CoCo to ignore it |
| `workshop_guide/` | This Streamlit app | No. Ignored via AGENTS.md |
| `admin/` | Setup and teardown SQL | No |
""")

st.info(":material/play_arrow: **Running it exactly like the original:** in a trial account, run the original `scripts/setup.sql` from the guide repo, then in each prompt read `DEMO_DB / TPCH_TRANSFORMED / DEMO_WH / coco-de-guide` wherever this app shows the Tricon names. Every Part 1 step and expected result is otherwise the same.")
