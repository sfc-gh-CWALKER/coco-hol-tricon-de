import streamlit as st
from components import (
    LAB_ROLE,
    PLUGIN,
    REPO_NAME,
    attendee_schema,
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
    {"name": "CoCo CLI (headless)", "description": "The terminal form of CoCo. With --print it runs one prompt without a chat window, in GitHub Actions or on your laptop, loading the same .cortex/plugins/ folder.", "icon": "terminal"},
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
st.markdown("The same dbt-review subagent you ran in Module 3, now running on every pull request. This part uses the **CoCo CLI** in headless mode: one prompt, no chat window, the same `.cortex/plugins/` folder.")
st.info(f":material/fork_right: You need **your own fork** of `{REPO_NAME}` (Module 0, Step 1). Pull requests and secrets live on your fork, so every attendee's CI is separate.")

with st.container(border=True):
    st.markdown("""
:material/alt_route: **Your facilitator tells you which path to follow.** GitHub's runners connect from outside your company network, so on an account with a network policy they only get in if your admin allowed them before the lab.

| Path | When | What you do |
|---|---|---|
| **A. Hands-on CI** | Your admin ran `scripts/admin_setup.sql` with `CI_PATH_A = 'YES'`, or the account has no network policy | Steps 1–4 below |
| **B. Laptop fallback** | GitHub's runners aren't allowed in | Steps 2 and 4 (to see the workflow and open the PR), then **Step 5**: the same review, run headless from your laptop |
""")

st.markdown("##### Step 1: Configure GitHub secrets")
st.markdown(f"""
In **your fork** on GitHub: **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|---|---|
| `SNOWFLAKE_ACCOUNT` | `{st.session_state.get('sf_account') or '<YOUR_ACCOUNT>'}` |
| `SNOWFLAKE_USER` | `{attendee_user()}` |
| `SNOWFLAKE_PASSWORD` | Your `DEMO_PAT` from Module 0, Step 5 |
| `SNOWFLAKE_SCHEMA` | `{attendee_schema()}` |
""")
render_guide_change(
    "Three secrets.",
    "A fourth, `SNOWFLAKE_SCHEMA`, so CI's `dbt build` uses your own schema.",
    "The guide's workflow never installs dbt, but dbt-review runs `dbt build`. The workshop workflow adds dbt and a profile.")
render_explanation("The guide's 60-minute PAT bypass", f"""
Only for accounts with **no** network policy. It skips the *requirement* to have one; it doesn't get you past a policy that exists.

```sql
ALTER USER {attendee_user()} MODIFY PROGRAMMATIC ACCESS TOKEN DEMO_PAT
  SET MINS_TO_BYPASS_NETWORK_POLICY_REQUIREMENT = 60;
```
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
- Install dbt (pip install dbt-core dbt-snowflake) and write ~/.dbt/profiles.yml with
  profile coco_de_guide, target dev, type snowflake, account/user/password from the
  same three secrets, role DEMO_ROLE, database DEMO_DB, warehouse DEMO_WH, and
  schema from the SNOWFLAKE_SCHEMA secret.
- Install the CoCo CLI:
    curl -LsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh
  and add $HOME/.local/bin to PATH.
- Run the dbt-review agent, writing its final answer to review.md:
    cortex --print "Use the dbt-review agent to review the changes in this PR against origin/main. Output only the final Markdown table and the overall PASS/FAIL." \\
      --plugin-dir .cortex/plugins/coco-de-guide \\
      --allowed-tools "Bash" "Read" "Grep" "Glob" \\
      --max-turns 40 -o review.md
  Then print review.md, and fail the step if it doesn't contain "Overall" followed
  by PASS or FAIL. Don't hide errors.

Post the contents of review.md as a comment on the pull request, even if the review
step failed."""

render_prompt("Prompt 4.1", "Create the PR Review Workflow", PROMPT_4_1)
render_expected("A new `.github/workflows/pr-review.yml` with `fetch-depth: 0`, the connections.toml step, a dbt install + profiles.yml step, the CoCo CLI install, the `cortex --print ... --plugin-dir ... --allowed-tools ...` step with a PASS/FAIL check, and a comment step with `if: always()`. Click **Keep**. If it looks different, compare it with the tested copy in `part2/solutions/github-workflows/pr-review.yml`.")
render_guide_change(
    "`cortex --print \"...\" > review.md 2>/dev/null || true`, with the plugin auto-discovered.",
    "Adds `--plugin-dir`, `--allowed-tools`, a dbt install, and a step that fails without a verdict.",
    "Tested: headless CoCo CLI didn't find the dbt-review agent and blocked `git diff`/`dbt build`, and `|| true` turned that into a green run with an empty comment.")

render_explanation("Why allowing Bash in CI is OK here", f"""
Headless runs can't ask for approval, so tools must be allowed up front. What CI can do is still bounded: your `DEMO_PAT` only works as **{LAB_ROLE}** (Module 0, Step 5), and your plugin's hook blocks prod commands.
The role isn't in connections.toml for the same reason: the PAT picks it. `fetch-depth: 0` is essential, because the subagent diffs against `origin/main`.
""")

st.markdown("##### Step 3: Enable GitHub Actions (path A)")
st.markdown("Actions are disabled on forks by default. In your fork: **Actions** tab → **I understand my workflows, go ahead and enable them**.")

st.markdown("##### Step 4: Test the workflow")
st.markdown("""
1. **Create a branch:** click the branch name in the bottom status bar → **Create new branch...** → `feature/add-coco-plugin`.
2. **Stage and commit:** Source Control panel (`Cmd/Ctrl+Shift+G`) → **+** next to **Changes** → message below → **Commit**.
""")
render_code("Add AGENTS.md, custom skill, plugin, and CI workflow", language="text")
st.markdown("""
3. **Push:** click **Publish Branch**.
4. **Open a pull request** on GitHub from `feature/add-coco-plugin` into **your fork's** `main`.

   :red[**Change the base repository.**] GitHub defaults it to the workshop repo you forked from. Set *base repository* to `<YOUR_GITHUB_USERNAME>/sfguide-data-engineering-with-coco`, or your PR lands in everyone's shared repo.
5. **Path A:** watch the **Actions** tab. After about 2–3 minutes the dbt-review PASS/FAIL report is in the logs and posted as a PR comment. **Path B:** go to Step 5.
""")
render_expected("Path A: a green run **and** a PR comment with a table for `orders_summary` and `supplier_performance`, ending **Overall: PASS**. A **red** run with *IP ... is not allowed to access Snowflake* means GitHub's runners aren't allowed in: switch to path B.")
render_guide_change(
    "Open the PR against your fork of `Snowflake-Labs/sfguide-data-engineering-with-coco`.",
    "Your fork's upstream is the workshop repo, so GitHub defaults the base to the workshop repo. Change the base to your own fork the same way.",
    "Keeps every attendee's PR and CI run in their own fork.")
render_troubleshoot([
    ("No workflow run appears", "Actions aren't enabled on your fork (Step 3), or the PR doesn't touch `dbt/models/**`. Use **Run workflow** on the Actions tab to trigger it manually."),
    ("Red run: *IP ... is not allowed to access Snowflake*", "The network policy blocks GitHub's runner. Your admin needs to run `scripts/admin_setup.sql` with `CI_PATH_A = 'YES'` and your username in `ATTENDEES`; until then, use path B (Step 5)."),
    ("Red run: *No PASS/FAIL verdict*, review says Bash is blocked or no dbt-review agent", "The `cortex` step is missing `--plugin-dir .cortex/plugins/coco-de-guide` or `--allowed-tools`. Compare with `part2/solutions/github-workflows/pr-review.yml`."),
    ("Green run but the comment is just the heading", "You have the guide's original workflow (`2>/dev/null || true` hides errors). Re-run Prompt 4.1 or copy the tested workflow."),
    ("dbt build fails in CI with *profile not found* or *schema*", "The `SNOWFLAKE_SCHEMA` secret is missing or misspelled (Step 1)."),
    ("*Resource not accessible by integration* when posting the comment", "The workflow needs `pull-requests: write`. Ask CoCo to add it to `permissions:`."),
    ("The PR opened against the workshop repo", "Close it, and open a new one with base repository = your fork."),
])

# ---------------------------------------------------------------- Fallback
st.markdown("##### Step 5: Laptop fallback (path B)")
st.markdown("""
Run exactly what CI runs, from your laptop. Your laptop is on the company network, so the network policy lets it through, and you get the same PASS/FAIL table to paste into the PR.

1. **Install the CoCo CLI** once, in CoCo Desktop's terminal (`` Ctrl+` ``):
""")
render_code("curl -LsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh")
st.markdown("""
2. **Sign in:** run `cortex` once, follow the browser sign-in to your Snowflake account, then type `/exit`.
3. **From the repo folder, on your feature branch, run the review:**
""")
render_code("""cortex --print "Use the dbt-review agent to review the changes in this branch against origin/main. Output only the final Markdown table and the overall PASS/FAIL." \\
  --plugin-dir .cortex/plugins/coco-de-guide \\
  --allowed-tools "Bash" "Read" "Grep" "Glob" \\
  --max-turns 40 -o review.md
cat review.md""")
st.markdown("""
4. Paste `review.md` into your PR as a comment. It uses your own `~/.dbt/profiles.yml` from Module 0, so nothing else needs setting up.
""")
render_expected("After 1–2 minutes, the same table as CI: both changed models PASS on source() references, primary key tests and dbt build, ending **Overall: PASS**.")
render_troubleshoot([
    ("*command not found: cortex*", "Open a new terminal, or run `export PATH=\"$HOME/.local/bin:$PATH\"`."),
    ("Review says *No model changes*", "Run it on your feature branch after you committed (Step 4), and run `git fetch origin` first."),
    ("Review says Bash is blocked", "Keep the `--allowed-tools \"Bash\" ...` line; headless CoCo can't ask you to approve commands."),
], title="Fallback fixes")

render_key_concepts([
    {"term": "Same agent, three contexts", "definition": "Desktop chat, GitHub Actions, or a headless run on your laptop: the dbt-review subagent does the same review. CI makes it *consistent* on every PR."},
    {"term": "Fail loudly", "definition": "A CI check that can't run must go red. A green run with an empty comment looks like a pass."},
    {"term": "Catalog vs. GitHub install", "definition": "Catalog installs are governed by Snowflake grants and need no Git credentials. GitHub installs suit teams already working out of one repo."},
])

render_what_you_built([
    f"{PLUGIN} published to the Plugins Catalog",
    "GitHub Actions workflow that posts dbt-review results on every pull request, or the same review run headless from your laptop",
])
