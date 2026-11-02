import streamlit as st

from components import GUIDE_URL, LAB_DB, REPO_URL

st.title("Guide Mapping")
st.markdown(f"""
Part 1 is Jeremiah Hansen's [Data Engineering with CoCo]({GUIDE_URL}), section by section and prompt for prompt.
The workshop runs it for 30+ people on **one** Snowflake account, so each person builds in their own schema. This page lists every difference.

:green-badge[Same as the guide] marks a step that's word for word. :orange-badge[Workshop change] marks a deliberate change.
""")

st.markdown("#### The one substitution")
st.markdown(f"""
| Original guide | This workshop |
|---|---|
| `TPCH_TRANSFORMED` | `TPCH_<INITIALS>`, one per person, in the same `{LAB_DB}` |

Everything else keeps the guide's names: `DEMO_ROLE`, `DEMO_WH`, `{LAB_DB}`, the `coco_de_guide` dbt profile, the `coco-de-guide` plugin, `DEMO_PAT`, and the `feature/add-coco-plugin` branch.
""")

st.markdown("#### Section by section")
st.markdown(f"""
| Original guide section | This workshop | Status |
|---|---|---|
| Overview / What is Cortex Code? | Home | Condensed |
| Setup: fork and clone | Module 0, Step 1 | :orange-badge[Workshop change] Fork [the workshop copy]({REPO_URL}) of the guide repo |
| Setup: configure CoCo Desktop | Module 0, Step 3 | :green-badge[Same] |
| Setup: run `scripts/setup.sql` | Module 0, Step 4 | :orange-badge[Workshop change] Admin creates the shared role, warehouse and database once (`scripts/admin_setup.sql`); you set `MY_INITIALS` and run `setup.sql` to create your schema |
| Setup: create a PAT | Module 0, Step 5 | :green-badge[Same] The network-policy bypass moves to Module 4 and needs admin approval |
| Setup: configure dbt / `dbt debug` | Module 0, Steps 6–7 | :orange-badge[Workshop change] `schema: TPCH_<INITIALS>`; the app fills in your block |
| Create an AGENTS.md | Module 1, Prompts 1.1–1.2 | :green-badge[Same] with `schema (TPCH_<INITIALS>)` |
| Using CoCo Without a Skill | Module 2, Prompt 2.1 | :green-badge[Same] |
| Create a Custom Skill | Module 2, Prompts 2.2–2.3 | :green-badge[Same] |
| Create a Custom Plugin | Module 3, Prompts 3.1–3.5 | :green-badge[Same] One line added before `rm -rf .snowflake/` (cd to the repo root), plus an optional direct hook test |
| Publish to the Plugin Catalog | Module 4 | :green-badge[Same] Lands in each person's own `USER$<username>` database |
| Enforce Standards in CI/CD | Module 4, Prompt 4.1 | :green-badge[Same] Your fork, your secrets; bypass only with admin approval |
| — | Modules A1–A7 | :blue-badge[New] Tricon's automation list |
""")

st.markdown("#### What's added to the starter repo")
st.markdown("""
| Path | Purpose | Affects Part 1? |
|---|---|---|
| `scripts/setup.sql` | Per-person: `SET MY_INITIALS`, creates `DEMO_DB.TPCH_<INITIALS>` | Replaces the guide's version |
| `scripts/admin_setup.sql` | One-time shared setup for the workshop admin | No |
| `part2/resident_contacts.sql` | Synthetic PII for A2, loaded into your schema | No. dbt never reads `part2/`, so `dbt build` builds the same models as the guide |
| `part2/admin_optional.sql` | Optional reviewer role, email integration, Adaptive demo warehouse | No |
| `part2/solutions/coco-de-guide/` | Reference skills, subagents and hook | No. It isn't under `.cortex/plugins/`, so CoCo doesn't load it |
""")

st.info(":material/play_arrow: **On your own account?** Use the original repo and guide as written. The only thing this workshop changes is who creates which object, and the schema name.")
