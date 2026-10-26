import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header("Module 4", "Share & CI/CD", "15 min · optional", "Plugin published to the Plugins Catalog, and dbt-review running on every pull request")

render_technologies_used([
    {"name": "Plugins Catalog", "description": "Snowflake's registry for sharing plugins. Access is governed by Snowflake roles and grants, and consumers don't need GitHub access.", "icon": "storefront"},
    {"name": "CoCo CLI in CI", "description": "The terminal form of CoCo runs headlessly in GitHub Actions and auto-discovers the same .cortex/plugins/ folder.", "icon": "terminal"},
    {"name": "GitHub Actions", "description": "Runs the dbt-review subagent on every PR that touches dbt/models/** and posts the report as a comment.", "icon": "sync_alt"},
])

st.markdown("#### Option A: Publish to the Plugins Catalog")
with st.container(border=True):
    st.markdown("""
1. **Settings → Plugins** → open the `tricon-de` card.
2. Click **Publish to Plugins Catalog** (cloud-upload icon).
3. Confirm the name and description, and choose who can access it.

CoCo creates a `CORTEX EXTENSION` object at `USER$<YOUR_USERNAME>.SKILL_SHARING.TRICON_DE` and returns a share URI:

```
snow://skill_catalog/USER$<YOUR_USERNAME>.SKILL_SHARING.TRICON_DE/versions/version$1/
```

A teammate installs it with **Plugins → + → Add from Plugins Catalog** and pastes the URI. This is how Tricon's dbt standards reach the India team without a repo copy.

:material/info: Publishing requires the `CREATE CORTEX EXTENSION` privilege in your account. Check with your admin if the button fails.
""")

st.space("small")
st.markdown("#### Option B: Run dbt-review in GitHub Actions")

st.warning("""
:material/lock: **Authentication on Tricon's account.** The original guide uses a Personal Access Token and a 60-minute network-policy bypass. **Don't use the bypass here.** For CI, have Tricon's admin create a dedicated service user (key-pair auth or a PAT) with a minimal role, plus a network policy that allows GitHub-hosted runners. You can also use a Tricon self-hosted runner. Until that's approved, run Option B in a trial account or skip it.
""")

st.markdown("Add these repository secrets in your fork (**Settings → Secrets and variables → Actions**): `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD` (the service user's PAT).")

PROMPT_4_1 = """Create a GitHub Actions workflow at .github/workflows/pr-review.yml.
Trigger on pull requests that touch dbt/models/** and also allow manual dispatch.
Grant permissions: contents read and pull-requests write.

For the CoCo steps:
- Configure a Snowflake connection by writing ~/.snowflake/connections.toml with a
  [default] profile using keys account, user, and password sourced from the
  SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD secrets. Set file
  permissions to 600.
- Install the CoCo CLI:
    curl -LsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh
  and add $HOME/.local/bin to PATH. No plugin install step is needed — the plugin
  in .cortex/plugins/ is auto-discovered.
- Run the dbt-review agent:
    cortex --print "Use the dbt-review agent to review the changes in this PR" \\
      > review.md 2>/dev/null || true

Post the contents of review.md as a comment on the pull request."""

render_prompt("Prompt 4.1", "Create the PR Review Workflow", PROMPT_4_1)

render_explanation("Test it", """
1. Commit to `feature/add-tricon-de-plugin` in the **Source Control** panel (`Cmd/Ctrl+Shift+G`), then click **Publish Branch**.
2. On GitHub, enable Actions in your fork (**Actions** tab → *I understand my workflows...*).
3. Open a PR into **your fork's** `main`. GitHub defaults to the upstream repo, so change the base.
4. Watch the **Actions** tab. The PASS/FAIL report is posted as a PR comment.

Note that `fetch-depth: 0` is required so the agent can diff against `origin/main`. All the logic lives in the subagent; the workflow is just plumbing.
""")

render_key_concepts([
    {"term": "Same agent, two contexts", "definition": "The dbt-review subagent doesn't get smarter in CI. It becomes *consistent*: the same review on every PR, from everyone."},
    {"term": "Catalog vs. GitHub install", "definition": "Catalog installs are governed by Snowflake grants and need no Git credentials. GitHub installs suit teams already working out of one repo."},
])

render_what_you_built([
    "tricon-de published to the Plugins Catalog (Option A)",
    "GitHub Actions workflow that posts dbt-review results on PRs (Option B)",
])
