import importlib
from pathlib import Path

import streamlit as st

import components

# Streamlit Cloud hot-reloads this file on each push but keeps imported modules cached;
# reload so pages never see an older components.py than this file expects.
importlib.reload(components)

from components import (
    LOGIN_TEMP,
    LOGIN_USUAL,
    PERSISTED_KEYS,
    attendee_schema,
    attendee_user,
    is_session_complete,
    setup_complete,
)

_DIR = Path(__file__).parent


def _title(key: str, label: str) -> str:
    check = " :green[:material/check_circle:]" if is_session_complete(key) else ""
    return f"{key}. {label}{check}"


def _sync_to_url():
    for k in PERSISTED_KEYS:
        v = st.session_state.get(k)
        if v:
            st.query_params[k] = v
        elif k in st.query_params:
            del st.query_params[k]


# Restore sidebar values after a browser refresh (they're kept in the URL, never anything secret).
for _k in PERSISTED_KEYS:
    if _k not in st.session_state and _k in st.query_params:
        st.session_state[_k] = st.query_params[_k]


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
    st.markdown("**Your lab details** · from the row your admin sent you")
    st.caption("Only used to fill in the commands and prompts on these pages, so you can copy them as-is. Nothing is sent or saved: this app isn't connected to Snowflake. Never type a password here.")
    st.text_input(
        "Your initials",
        key="initials",
        max_chars=4,
        placeholder="e.g. CW",
        help="Use the initials in your admin's list. They name your personal schema. Press Enter to apply.",
        on_change=_sync_to_url,
    )
    st.radio(
        "How do you sign in to Snowflake?",
        [LOGIN_USUAL, LOGIN_TEMP],
        key="login_type",
        on_change=_sync_to_url,
        help="Your admin's list shows your login_type: A = your usual login, B or C = a temporary lab login.",
    )
    st.text_input(
        "Snowflake username",
        key="sf_user",
        placeholder="TRICON_DE_<initials>" if st.session_state.get("login_type") == LOGIN_TEMP else "e.g. JSMITH",
        help="The 'username' column in your admin's list. Temporary lab logins can leave this blank.",
        on_change=_sync_to_url,
    )
    st.text_input(
        "Account identifier",
        key="sf_account",
        placeholder="e.g. tricon-prod",
        help="The 'account_identifier' column in your admin's list (orgname-accountname).",
        on_change=_sync_to_url,
    )
    if setup_complete():
        st.success(f"Every command and prompt now uses **{attendee_user()}** and **`TRICON_DE.{attendee_schema()}`**.", icon=":material/check_circle:")
    else:
        st.warning("Fill in all four so every command on these pages is ready to copy as-is.", icon=":material/edit:")

page = st.navigation(
    {
        "": [
            st.Page("app_pages/home.py", title="Home", icon=":material/home:"),
            st.Page("app_pages/getting_started.py", title="Getting Started", icon=":material/rocket_launch:"),
            st.Page("app_pages/agenda.py", title="Agenda", icon=":material/calendar_today:"),
            st.Page("app_pages/help.py", title="Help & Troubleshooting", icon=":material/support:"),
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
