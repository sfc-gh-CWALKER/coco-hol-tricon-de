import streamlit as st
from components import (
    LAB_ROLE,
    PLUGIN,
    REPO_NAME,
    attendee_user,
    render_code,
    render_expected,
    render_explanation,
    render_guide_change,
    render_key_concepts,
    render_prompt,
    render_same_as_guide,
    render_session_header,
    render_technologies_used,
    render_troubleshoot,
    render_what_you_built,
)

render_session_header("Module 4", "Plugin Catalog & CI/CD", "20 min", "Plugin published to the Plugins Catalog, and dbt-review running on every pull request")

render_technologies_used([
    {"name": "Plugins Catalog", "description": "Snowflake's registry for sharing plugins. Access is governed by Snowflake roles and grants, and consumers don't need GitHub access.", "icon": "storefront"},
    {"name": "CoCo CLI in CI", "description": "The terminal form of CoCo runs headlessly in GitHub Actions and auto-discovers the same .cortex/plugins/ folder.", "icon": "terminal"},
    {"name": "GitHub Actions", "description": "Runs the dbt-review subagent on every PR that touches dbt/models/** and posts the report as a comment.", "icon": "sync_alt"},
])

# ---------------------------------------------------------------- Catalog
st.markdown("#### Publish to the Plugin Catalog")
render_same_as_guide("Publish to the Plugin Catalog")
with st.container(border=True):
    st.markdown(f"""
1. **Settings** (gear icon, bottom of the left sidebar) → **Plugins** → open the `{PLUGIN}` card.
2. Click **Publish to Plugins Catalog** (cloud-upload icon).
3. A chat opens and the `share-skill-and-plugin` skill runs. Confirm the name and description, and choose who can access it.

CoCo creates a `CORTEX EXTENSION` object in **your personal database**, so everyone's plugin is separate even though they share a name:

```
USER$<YOUR_USERNAME>.SKILL_SHARING.COCO_DE_GUIDE
```

and reports the share URI:

```
snow://skill_catalog/USER$<YOUR_USERNAME>.SKILL_SHARING.COCO_DE_GUIDE/versions/version$1/
```
""")
render_expected(f"A `snow://skill_catalog/USER${attendee_user()}.SKILL_SHARING.COCO_DE_GUIDE/...` link.")
render_explanation("Installing a catalog plugin (the teammate's side)", f"""
1. **Settings → Plugins** → **+** → **Add from Plugins Catalog**
2. Paste the `snow://skill_catalog/...` URI → **Import**

The plugin appears with a **CATALOG** badge, and they can sync to newer versions from its detail view. Try it with a neighbour's URI, in a different folder from your own `{PLUGIN}` (you both built one).
""")
render_troubleshoot([
    ("*Insufficient privileges* / *personal database not enabled*", "Personal databases may be off on your account. The facilitator demos this step instead."),
    ("Neighbour sees *not available*", "By default the plugin isn't discoverable; it's reachable only with the URI. Check they pasted the whole URI, then wait a minute for the security scan."),
])

# ---------------------------------------------------------------- CI/CD
st.space("small")
st.markdown("#### Enforce standards automatically in CI/CD")
st.markdown("The same dbt-review subagent you ran in Module 3, now running on every pull request. This part uses the **CoCo CLI**, which runs headlessly in GitHub Actions and auto-discovers `.cortex/plugins/` just like Desktop.")
st.info(f":material/fork_right: You need **your own fork** of `{REPO_NAME}` (Module 0, Step 1). Pull requests and secrets live on your fork, so every attendee's CI is separate.")

st.markdown("##### Step 1: Configure GitHub secrets")
render_same_as_guide("Enforce Standards Automatically in CI/CD → Configure GitHub Secrets")
st.markdown(f"""
In **your fork** on GitHub: **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|---|---|
| `SNOWFLAKE_ACCOUNT` | `{st.session_state.get('sf_account') or '<YOUR_ACCOUNT>'}` |
| `SNOWFLAKE_USER` | `{attendee_user()}` |
| `SNOWFLAKE_PASSWORD` | Your `DEMO_PAT` from Module 0, Step 5 |
""")

st.warning(f"""
:material/lock: **GitHub's runners connect from outside your company network.** If your account has a network policy, the PAT is blocked from GitHub unless the policy allows it.
The guide uses a 60-minute bypass:

```sql
ALTER USER {attendee_user()} MODIFY PROGRAMMATIC ACCESS TOKEN DEMO_PAT
  SET MINS_TO_BYPASS_NETWORK_POLICY_REQUIREMENT = 60;
```

**Run this only if your Snowflake admin approves it.** Otherwise the workflow runs but the review step can't connect, and the facilitator demos a working run. The long-term setup is a CI service user with a network policy that allows GitHub's runners, or a self-hosted runner inside your network.
""")

st.markdown("##### Step 2: Create the GitHub Actions workflow")
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

render_same_as_guide("Enforce Standards Automatically in CI/CD → Create the GitHub Actions Workflow")
render_prompt("Prompt 4.1", "Create the PR Review Workflow", PROMPT_4_1)
render_expected("A new `.github/workflows/pr-review.yml` with `fetch-depth: 0`, a step writing `~/.snowflake/connections.toml` from the three secrets, the CoCo CLI install, the `cortex --print` step, and a step posting `review.md` as a PR comment. Click **Keep**.")

render_explanation("Why the role isn't in connections.toml", f"""
The guide's workflow doesn't set a role. It doesn't need to: your `DEMO_PAT` is restricted to the single role **{LAB_ROLE}** (Module 0, Step 5), so that's the role CI runs as.
`fetch-depth: 0` is essential: the subagent diffs against `origin/main`, which needs full history.
""")

st.markdown("##### Step 3: Enable GitHub Actions")
render_same_as_guide("Enforce Standards Automatically in CI/CD → Enable GitHub Actions")
st.markdown("Actions are disabled on forks by default. In your fork: **Actions** tab → **I understand my workflows, go ahead and enable them**.")

st.markdown("##### Step 4: Test the workflow")
render_same_as_guide("Enforce Standards Automatically in CI/CD → Test the Workflow")
st.markdown("""
1. **Create a branch:** click the branch name in the bottom status bar → **Create new branch...** → `feature/add-coco-plugin`.
2. **Stage and commit:** Source Control panel (`Cmd/Ctrl+Shift+G`) → **+** next to **Changes** → message below → **Commit**.
""")
render_code("Add AGENTS.md, custom skill, plugin, and CI workflow", language="text")
st.markdown("""
3. **Push:** click **Publish Branch**.
4. **Open a pull request** on GitHub from `feature/add-coco-plugin` into **your fork's** `main`. GitHub defaults the base to the upstream repository; change it to your fork.
5. Watch the **Actions** tab. When it finishes, the dbt-review PASS/FAIL report is in the logs and posted as a PR comment.
""")
render_guide_change(
    "Open the PR against your fork of `Snowflake-Labs/sfguide-data-engineering-with-coco`.",
    "Your fork's upstream is the workshop repo, so GitHub defaults the base to the workshop repo. Change the base to your own fork the same way.",
    "Keeps every attendee's PR and CI run in their own fork.")
render_troubleshoot([
    ("No workflow run appears", "Actions aren't enabled on your fork (Step 3), or the PR doesn't touch `dbt/models/**`. Use **Run workflow** on the Actions tab to trigger it manually."),
    ("The PR comment says *No review output produced*", "The CLI couldn't connect. Most often the network policy blocks GitHub's runners (see the warning in Step 1), or a secret has a typo. Check the *Run Cortex Code* step's log."),
    ("*Resource not accessible by integration* when posting the comment", "The workflow needs `pull-requests: write`. Ask CoCo to add it to `permissions:`."),
    ("The PR opened against the workshop repo", "Close it, and open a new one with base repository = your fork."),
])

render_key_concepts([
    {"term": "Same agent, two contexts", "definition": "The dbt-review subagent doesn't get smarter in CI. It becomes *consistent*: the same review on every PR, from everyone."},
    {"term": "Catalog vs. GitHub install", "definition": "Catalog installs are governed by Snowflake grants and need no Git credentials. GitHub installs suit teams already working out of one repo."},
])

render_what_you_built([
    f"{PLUGIN} published to the Plugins Catalog",
    "GitHub Actions workflow that posts dbt-review results on every pull request",
])
