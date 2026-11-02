import streamlit as st

# Prompt ids per module; a module shows a check in the sidebar once all are done.
SESSION_PROMPTS = {
    "1": ["Prompt 1.1", "Prompt 1.2"],
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

# Shared objects from the guide, created once by the workshop admin (scripts/admin_setup.sql).
LAB_ROLE = "DEMO_ROLE"
LAB_WH = "DEMO_WH"
LAB_DB = "DEMO_DB"
PLUGIN = "coco-de-guide"
REVIEWER_ROLE = "DEMO_REVIEWER"

# The workshop fork of Jeremiah Hansen's guide repo. Attendees fork this one.
REPO_OWNER = "sfc-gh-CWALKER"
REPO_NAME = "sfguide-data-engineering-with-coco"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
GUIDE_URL = "https://www.snowflake.com/en/developers/guides/data-engineering-with-coco/"

INITIALS_PLACEHOLDER = "<INITIALS>"
ACCOUNT_PLACEHOLDER = "<YOUR_ACCOUNT>"
USER_PLACEHOLDER = "<YOUR_USERNAME>"
GITHUB_PLACEHOLDER = "<YOUR_GITHUB_USERNAME>"

# Sidebar values that are mirrored into the URL so a browser refresh keeps them.
PERSISTED_KEYS = ("initials", "sf_user", "sf_account", "gh_user")


def attendee_initials() -> str:
    return "".join(c for c in st.session_state.get("initials", "") if c.isalpha()).upper()


def attendee_account() -> str:
    return st.session_state.get("sf_account", "").strip() or ACCOUNT_PLACEHOLDER


def attendee_user() -> str:
    return st.session_state.get("sf_user", "").strip().upper() or USER_PLACEHOLDER


def attendee_github() -> str:
    return st.session_state.get("gh_user", "").strip() or GITHUB_PLACEHOLDER


def setup_complete() -> bool:
    """Initials are the only required input; username and account are optional pre-fills."""
    return len(attendee_initials()) >= 2


def attendee_schema() -> str:
    """Per-attendee schema in the shared DEMO_DB; replaces the guide's TPCH_TRANSFORMED."""
    return f"TPCH_{attendee_initials() or INITIALS_PLACEHOLDER}"


def profiles_yml() -> str:
    """The guide's ~/.dbt/profiles.yml block with this attendee's values filled in."""
    return f"""coco_de_guide:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{attendee_account()}"
      user: "{attendee_user()}"
      password: "<YOUR_PERSONAL_ACCESS_TOKEN>"
      role: {LAB_ROLE}
      database: {LAB_DB}
      warehouse: {LAB_WH}
      schema: {attendee_schema()}
      threads: 4
"""


def personalize(text: str) -> str:
    initials = attendee_initials()
    if initials:
        text = text.replace(INITIALS_PLACEHOLDER, initials)
    if attendee_account() != ACCOUNT_PLACEHOLDER:
        text = text.replace(ACCOUNT_PLACEHOLDER, attendee_account())
    if attendee_user() != USER_PLACEHOLDER:
        text = text.replace(USER_PLACEHOLDER, attendee_user())
    if attendee_github() != GITHUB_PLACEHOLDER:
        text = text.replace(GITHUB_PLACEHOLDER, attendee_github())
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
        st.markdown(":orange-badge[:material/edit_note: Workshop change]")
        st.markdown(personalize(f"**Original guide:** {original}  \n**This workshop:** {tricon}  \n**Why:** {why}"))


def render_same_as_guide(section: str):
    """Marks a step that is word for word from the original guide (only your schema name is filled in)."""
    st.caption(f":green-badge[:material/check: Same as the guide] Guide section: *{section}*")


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
