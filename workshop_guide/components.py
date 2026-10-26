import streamlit as st

# Prompt ids per module; a module shows a check in the sidebar once all are done.
SESSION_PROMPTS = {
    "1": ["Prompt 1.1", "Prompt 1.2", "Prompt 1.3"],
    "2": ["Prompt 2.1", "Prompt 2.2", "Prompt 2.3"],
    "3": ["Prompt 3.1", "Prompt 3.2", "Prompt 3.3", "Prompt 3.4", "Prompt 3.5"],
    "4": ["Prompt 4.1"],
    "A1": ["Prompt A1.1", "Prompt A1.2", "Prompt A1.3"],
    "A2": ["Prompt A2.1", "Prompt A2.2", "Prompt A2.3"],
    "A3": ["Prompt A3.1", "Prompt A3.2"],
    "A4": ["Prompt A4.1", "Prompt A4.2", "Prompt A4.3"],
    "A5": ["Prompt A5.1", "Prompt A5.2"],
    "A6": ["Prompt A6.1", "Prompt A6.2", "Prompt A6.3"],
}

INITIALS_PLACEHOLDER = "<INITIALS>"
ACCOUNT_PLACEHOLDER = "<TRICON_ACCOUNT_IDENTIFIER>"
USER_PLACEHOLDER = "<YOUR_SNOWFLAKE_USERNAME>"
LOGIN_USUAL = "My usual Tricon Snowflake login"
LOGIN_TEMP = "A temporary lab login (TRICON_DE_...)"

# Sidebar values that are mirrored into the URL so a browser refresh keeps them.
PERSISTED_KEYS = ("initials", "login_type", "sf_user", "sf_account")


def attendee_initials() -> str:
    return "".join(c for c in st.session_state.get("initials", "") if c.isalnum()).upper()


def attendee_account() -> str:
    return st.session_state.get("sf_account", "").strip() or ACCOUNT_PLACEHOLDER


def uses_temp_login() -> bool:
    return st.session_state.get("login_type") == LOGIN_TEMP


def attendee_user() -> str:
    """Snowflake login name: typed by the attendee, or TRICON_DE_<INITIALS> for temporary lab logins."""
    typed = st.session_state.get("sf_user", "").strip().upper()
    if typed:
        return typed
    if uses_temp_login():
        return f"TRICON_DE_{attendee_initials() or INITIALS_PLACEHOLDER}"
    return USER_PLACEHOLDER


def setup_complete() -> bool:
    return bool(attendee_initials()) and attendee_account() != ACCOUNT_PLACEHOLDER and attendee_user() != USER_PLACEHOLDER


def profiles_yml(authenticator: str = "oauth_authorization_code") -> str:
    """Personalized dbt profile. Lives at the project root, so ~/.dbt/profiles.yml is never touched."""
    auth_lines = {
        "oauth_authorization_code": "      authenticator: oauth_authorization_code   # browser sign-in; nothing stored",
        "externalbrowser": "      authenticator: externalbrowser            # Tricon SSO in a browser pop-up",
        "username_password_mfa": "      authenticator: username_password_mfa\n      password: \"{{ env_var('SNOWFLAKE_PASSWORD') }}\"   # read from your terminal, never saved",
    }[authenticator]
    return f"""tricon_de:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{attendee_account()}"
      user: "{attendee_user()}"
{auth_lines}
      role: TRICON_DE_ROLE
      database: TRICON_DE
      warehouse: TRICON_DE_WH
      schema: {attendee_schema()}
      threads: 4
"""


def attendee_schema() -> str:
    """Per-attendee dbt schema in the shared TRICON_DE database, e.g. DBT_CW."""
    return f"DBT_{attendee_initials() or INITIALS_PLACEHOLDER}"


def personalize(text: str) -> str:
    initials = attendee_initials()
    if initials:
        text = text.replace(INITIALS_PLACEHOLDER, initials)
    if attendee_account() != ACCOUNT_PLACEHOLDER:
        text = text.replace(ACCOUNT_PLACEHOLDER, attendee_account())
    if attendee_user() != USER_PLACEHOLDER:
        text = text.replace(USER_PLACEHOLDER, attendee_user())
    return text


def _done_store() -> dict:
    if "_done" not in st.session_state:
        st.session_state["_done"] = {}
    return st.session_state["_done"]


def _prompt_key(prompt_id: str) -> str:
    return prompt_id.replace(" ", "_").replace(".", "_")


def _on_toggle(prompt_id: str):
    key = _prompt_key(prompt_id)
    _done_store()[key] = st.session_state[f"_cb_{key}"]


def is_session_complete(session_key: str) -> bool:
    prompts = SESSION_PROMPTS.get(session_key, [])
    store = _done_store()
    return len(prompts) > 0 and all(
        store.get(_prompt_key(p), False) for p in prompts
    )


def render_prompt(prompt_id: str, title: str, prompt_text: str):
    key = _prompt_key(prompt_id)
    cb_key = f"_cb_{key}"
    store = _done_store()
    if cb_key not in st.session_state:
        st.session_state[cb_key] = store.get(key, False)
    with st.container(border=True):
        header_col, check_col = st.columns([5, 1])
        with header_col:
            st.markdown(f"#### :material/terminal: {prompt_id} - {title}")
        with check_col:
            st.checkbox(
                "Done",
                key=cb_key,
                on_change=_on_toggle,
                args=(prompt_id,),
            )
        st.caption("Copy this prompt and paste it into the Cortex Code Desktop chat panel")
        st.code(personalize(prompt_text), language="text", wrap_lines=True)


def render_explanation(title: str, body: str):
    with st.expander(f":material/school: {title}", expanded=False):
        st.markdown(personalize(body))


def render_technology_card(name: str, description: str, icon: str = "widgets"):
    with st.container(border=True):
        st.markdown(f":material/{icon}: **{name}**")
        st.caption(description)


def render_technologies_used(technologies: list[dict]):
    st.markdown("##### :material/build: Technologies used in this module")
    cols = st.columns(min(len(technologies), 3))
    for i, tech in enumerate(technologies):
        with cols[i % len(cols)]:
            render_technology_card(
                tech["name"], tech["description"], tech.get("icon", "widgets")
            )


def render_code(code: str, language: str = "bash"):
    st.code(personalize(code), language=language, wrap_lines=True)


def render_expected(text: str):
    """What a correct result looks like, so attendees can self-check every step."""
    st.success(personalize(f":material/check_circle: **You should see:** {text}"))


def render_troubleshoot(rows: list[tuple[str, str]], title: str = "Something different? Fixes"):
    """Symptom -> fix table in a collapsed expander."""
    with st.expander(f":material/build: {title}"):
        table = "| If you see | Do this |\n|---|---|\n" + "\n".join(
            f"| {symptom} | {fix} |" for symptom, fix in rows)
        st.markdown(personalize(table))


def render_before_you_start(items: list[str]):
    with st.container(border=True):
        st.markdown("##### :material/checklist: Before you start this module")
        for item in items:
            st.markdown(f"- {personalize(item)}")


def render_guide_change(original: str, tricon: str, why: str):
    """Callout marking a deliberate difference from Jeremiah Hansen's original guide."""
    with st.container(border=True):
        st.markdown(":orange-badge[:material/edit_note: Adjusted for Tricon]")
        st.markdown(personalize(f"**Original guide:** {original}  \n**This lab:** {tricon}  \n**Why:** {why}"))


def render_new_for_tricon(text: str):
    st.markdown(f":blue-badge[:material/add_circle: New for Tricon] {text}")


def render_guardrail(text: str):
    st.warning(f":material/verified_user: **Human approval required.** {text}")


def render_session_header(
    label: str,
    title: str,
    duration: str,
    building: str,
):
    st.title(f"{label}: {title}")
    col1, col2 = st.columns(2)
    col1.markdown(f":material/schedule: **{duration}**")
    col2.markdown(f":material/construction: **Building**: {building}")
    st.space("small")


def render_key_concepts(concepts: list[dict]):
    st.markdown("##### :material/lightbulb: Key concepts")
    for concept in concepts:
        with st.expander(f"**{concept['term']}**"):
            st.markdown(personalize(concept["definition"]))


def render_what_you_built(items: list[str]):
    st.markdown("##### :material/check_circle: What you built in this module")
    for item in items:
        st.markdown(f"- :green-badge[Done] {personalize(item)}")
