from pathlib import Path

import streamlit as st

from components import attendee_schema, is_session_complete

_DIR = Path(__file__).parent


def _title(key: str, label: str) -> str:
    check = " :green[:material/check_circle:]" if is_session_complete(key) else ""
    return f"{key}. {label}{check}"


st.set_page_config(
    page_title="Tricon Data Engineering with CoCo",
    page_icon=":material/engineering:",
    layout="wide",
)

st.logo(
    str(_DIR / "static" / "snowflake_full_logo.png"),
    icon_image=str(_DIR / "static" / "snowflake_logo.png"),
)

with st.sidebar:
    st.text_input(
        "Your initials",
        key="initials",
        max_chars=4,
        placeholder="e.g. CW",
        help="Personalizes every prompt with your own dbt schema. Press Enter to apply.",
    )
    st.caption(f"Your dbt schema: `TRICON_DE.{attendee_schema()}`")

page = st.navigation(
    {
        "": [
            st.Page("app_pages/home.py", title="Home", icon=":material/home:"),
            st.Page("app_pages/getting_started.py", title="Getting Started", icon=":material/rocket_launch:"),
            st.Page("app_pages/agenda.py", title="Agenda", icon=":material/calendar_today:"),
            st.Page("app_pages/guide_mapping.py", title="Guide Mapping", icon=":material/compare_arrows:"),
        ],
        "Part 1: Engineering Standards (from the guide)": [
            st.Page("app_pages/m01_agents_md.py", title=_title("1", "AGENTS.md"), icon=":material/description:"),
            st.Page("app_pages/m02_skill.py", title=_title("2", "Tests & Custom Skill"), icon=":material/auto_fix_high:"),
            st.Page("app_pages/m03_plugin.py", title=_title("3", "Plugin, Hook & Subagent"), icon=":material/extension:"),
            st.Page("app_pages/m04_share_cicd.py", title=_title("4", "Share & CI/CD"), icon=":material/sync_alt:"),
        ],
        "Part 2: Automation Workflows (new for Tricon)": [
            st.Page("app_pages/a1_dbt_upkeep.py", title=_title("A1", "dbt Upkeep"), icon=":material/build_circle:"),
            st.Page("app_pages/a2_classification.py", title=_title("A2", "Classification Sweep"), icon=":material/policy:"),
            st.Page("app_pages/a3_access_review.py", title=_title("A3", "Access Review"), icon=":material/admin_panel_settings:"),
            st.Page("app_pages/a4_kpi_report.py", title=_title("A4", "KPI Report"), icon=":material/summarize:"),
            st.Page("app_pages/a5_anomaly.py", title=_title("A5", "Anomaly Explanation"), icon=":material/troubleshoot:"),
            st.Page("app_pages/a6_warehouses.py", title=_title("A6", "Warehouse Right-Sizing"), icon=":material/speed:"),
            st.Page("app_pages/a7_schedule.py", title="A7. Put It on a Schedule", icon=":material/event_repeat:"),
        ],
    },
    position="sidebar",
    expanded=True,
)

page.run()
