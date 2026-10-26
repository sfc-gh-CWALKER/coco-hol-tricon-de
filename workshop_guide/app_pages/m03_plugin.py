import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_code, render_guide_change, render_new_for_tricon, render_expected, render_troubleshoot, render_before_you_start

render_session_header("Module 3", "Plugin, Hook & Subagent", "25 min", "The tricon-de plugin: skill + prod-safety hook + dbt-review subagent")

render_technologies_used([
    {"name": "Plugins", "description": "A versioned, validated, single installable unit that bundles skills, hooks, subagents, and MCP servers.", "icon": "extension"},
    {"name": "PreToolUse hooks", "description": "Shell commands that run before CoCo executes a tool. Use them as hard guardrails, for example blocking production deploys.", "icon": "security"},
    {"name": "Subagents", "description": "Markdown-defined agents that run autonomously to completion on a specific task. The same agent works locally and in CI.", "icon": "smart_toy"},
])

render_before_you_start([
    "Module 2 is done and committed (`git log --oneline` shows your Module 1 and 2 commits).",
    "**Windows:** Git for Windows is installed (Getting Started, Step 2). Hooks run with its `bash`.",
    "Start a **new chat** for this module.",
])

st.markdown("""
A skill alone only lives in one workspace, and it isn't versioned or installable alongside a hook or subagent. A **plugin** packages them together.

```
.cortex/plugins/tricon-de/
├── .cortex-plugin/
│   ├── plugin.json       # Manifest (required)
│   └── activation.md     # Shown when the plugin activates
├── skills/new-dbt-model/SKILL.md
├── agents/dbt-review.md
└── hooks/
    ├── hooks.json
    └── validate-bash.sh
```

Part 2 adds more skills and subagents to this same plugin.
""")

render_guide_change(
    "Plugin `coco-de-guide` in `.cortex/plugins/coco-de-guide/`.",
    "Plugin `tricon-de` in `.cortex/plugins/tricon-de/`; the manifest also has a `description`. Prompt 3.2 adds one line (bash and grep only). Step 1 removes only empty folders instead of `rm -rf .snowflake/`, and Step 4 adds a direct hook test. Prompts 3.3–3.5 are word-for-word.",
    "Tricon-branded, safe on every laptop (macOS and Windows), and it becomes the home for the Part 2 skills and subagents.")

st.markdown("#### Step 1: Move the skill into the plugin")
st.markdown("CoCo auto-discovers project plugins in `.cortex/plugins/`. Run these in the CoCo Desktop terminal (it opens in the project folder):")
tab_sh, tab_ps = st.tabs(["macOS / Git Bash", "Windows PowerShell"])
with tab_sh:
    render_code("""test -f dbt/dbt_project.yml || echo "STOP: cd into the coco-hol-tricon-de folder first"
mkdir -p .cortex/plugins/tricon-de/skills
mv .snowflake/cortex/skills/new-dbt-model .cortex/plugins/tricon-de/skills/
rmdir .snowflake/cortex/skills .snowflake/cortex .snowflake 2>/dev/null; ls .cortex/plugins/tricon-de/skills""")
with tab_ps:
    render_code("""if (-not (Test-Path dbt/dbt_project.yml)) { "STOP: cd into the coco-hol-tricon-de folder first" }
New-Item -ItemType Directory -Force .cortex/plugins/tricon-de/skills | Out-Null
Move-Item .snowflake/cortex/skills/new-dbt-model .cortex/plugins/tricon-de/skills/
Get-ChildItem .cortex/plugins/tricon-de/skills""", language="powershell")
render_expected("The last line prints `new-dbt-model`.")
st.caption("The original guide ends this step with `rm -rf .snowflake/`. We only remove *empty* folders instead: in the wrong terminal folder, `rm -rf .snowflake/` would delete your Snowflake connection settings in your home directory.")
render_troubleshoot([
    ("`STOP: cd into the coco-hol-tricon-de folder first`", "Run `cd` to the project folder (the one with `dbt/` in it), then run the block again."),
    ("*No such file or directory* on the `mv` line", "The skill isn't at `.snowflake/cortex/skills/new-dbt-model`. Check Module 2's Prompt 2.2, or copy the reference: `mkdir -p .cortex/plugins/tricon-de/skills && cp -R solutions/tricon-de-plugin/skills/new-dbt-model .cortex/plugins/tricon-de/skills/`."),
])

PROMPT_3_1 = """Consult the CoCo Desktop plugin
documentation at https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop/plugins
for the correct plugin.json schema and file structure.

Create a CoCo plugin manifest for this project at .cortex/plugins/tricon-de/.cortex-plugin/plugin.json.

The manifest must include all of the following fields:
- name: "tricon-de"
- description: "Tricon data engineering standards and operations automations"
- version: 1.0.0
- author: me
- skills: pointing to ./skills
- agents: pointing to ./agents
- hooks: pointing to ./hooks/hooks.json

Also create .cortex/plugins/tricon-de/.cortex-plugin/activation.md that briefly explains
what the plugin includes.

Do not use the cortex CLI — write the files directly."""

render_prompt("Prompt 3.1", "Create the Plugin Manifest", PROMPT_3_1)
render_expected("Two new files: `.cortex/plugins/tricon-de/.cortex-plugin/plugin.json` and `activation.md` next to it.")

render_explanation("Expected plugin.json", """
```json
{
  "name": "tricon-de",
  "description": "Tricon data engineering standards and operations automations",
  "version": "1.0.0",
  "author": { "name": "<YOUR_NAME>" },
  "skills": ["./skills"],
  "agents": ["./agents"],
  "hooks": "./hooks/hooks.json"
}
```

If CoCo tries to run `cortex plugin ...` commands, remind it: *"Do not use the cortex CLI — write the files directly."*
""")

st.markdown("#### Step 2: Add a production-safety hook")

PROMPT_3_2 = """Consult the CoCo Desktop hooks documentation at
https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop/hooks
for the correct hooks.json schema and shell script format.

Create a PreToolUse hook at .cortex/plugins/tricon-de/hooks/validate-bash.sh that blocks
any dbt command that includes --target prod. If the command is blocked, return a clear error
message explaining that direct production dbt runs are not allowed and to use the CI/CD
pipeline instead.
Use only bash and grep in the script (no jq or python) so it works on every laptop.
Also create .cortex/plugins/tricon-de/hooks/hooks.json that wires this script to the
PreToolUse event using the matcher value "bash" (lowercase)."""

render_prompt("Prompt 3.2", "Create the Prod-Safety Hook", PROMPT_3_2)
st.caption(":orange-badge[Adjusted for Tricon] One line added: *Use only bash and grep (no jq or python)*. Many laptops don't have `jq`, and Windows often has no `python3`; a hook that can't parse its input silently lets everything through.")
render_expected("Two new files: `hooks/validate-bash.sh` and `hooks/hooks.json` under `.cortex/plugins/tricon-de/`.")

render_explanation("Expected hooks.json", """
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "bash",
        "hooks": [
          { "type": "command", "command": "bash .cortex/plugins/tricon-de/hooks/validate-bash.sh", "timeout": 10 }
        ]
      }
    ]
  }
}
```

The script reads the tool input as JSON on stdin, extracts the command, and blocks it if it matches `dbt ... --target prod`.
""")

st.markdown("#### Step 3: Add a dbt-review subagent")

PROMPT_3_3 = """Consult the CoCo Desktop agents documentation at
https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop/agents
for the correct agent definition format and frontmatter schema.

Create a dbt-review subagent at .cortex/plugins/tricon-de/agents/dbt-review.md.
The subagent should:
- Find all changed dbt model files compared to origin/main
- For each changed model, run dbt build --select <model> --project-dir dbt/
- Verify that each convention from the new-dbt-model skill is met
- Produce a concise PASS/FAIL report per convention with specific remediation steps for any failures

It should use the bash, read, grep, and glob tools. Set the model to auto."""

render_prompt("Prompt 3.3", "Create the dbt-review Subagent", PROMPT_3_3)
render_expected("A new `.cortex/plugins/tricon-de/agents/dbt-review.md` with frontmatter (`name`, `description`, `tools`, `model: auto`) and the four review steps.")

st.markdown("#### Step 4: Activate and test")
st.markdown("""
1. Open **Settings** (gear icon, bottom of the left sidebar) → **Plugins**.
2. Find `tricon-de`. If it's toggled off, turn it on. If it's missing, click **↻**.
3. Open the plugin card and confirm the skill, hook, and subagent are listed.

:material/info: Project plugins only auto-activate in a **trusted** workspace.
""")
render_expected("The `tricon-de` card is **on** and lists 1 skill (`new-dbt-model`), 1 agent (`dbt-review`) and 1 hook (`PreToolUse`).")
render_troubleshoot([
    ("`tricon-de` isn't listed", "Click **↻**. Check the manifest path is exactly `.cortex/plugins/tricon-de/.cortex-plugin/plugin.json`. Still missing: compare with `solutions/tricon-de-plugin/.cortex-plugin/plugin.json`."),
    ("The card shows a validation error", "Ask CoCo: *Validate my plugin.json against the plugin docs and fix it.* Or copy the reference manifest from `solutions/`."),
    ("Hooks section is empty", "`hooks.json` path in `plugin.json` must be `./hooks/hooks.json`. Then toggle the plugin off and on."),
    ("The workspace isn't trusted", "Command Palette (`Cmd/Ctrl+Shift+P`) → *Manage Workspace Trust* → **Trust**."),
])

st.markdown("**Test the hook directly first.** This sends the hook exactly what CoCo would send, so you see it block without involving the AI:")
render_code("""echo '{"tool_input":{"command":"dbt build --target prod --project-dir dbt/"}}' | bash .cortex/plugins/tricon-de/hooks/validate-bash.sh; echo "exit code: $?"
echo '{"tool_input":{"command":"dbt build --project-dir dbt/"}}' | bash .cortex/plugins/tricon-de/hooks/validate-bash.sh; echo "exit code: $?\"""")
st.caption("Windows: run these in **Git Bash** (Start menu → Git Bash, then `cd` to the project folder).")
render_expected("First command: your *Blocked...* message and **`exit code: 2`**. Second command: **`exit code: 0`** (dev runs are allowed).")
render_troubleshoot([
    ("First command shows `exit code: 0`", "The hook didn't recognize the command. A common cause is a script that relies on `jq` or `python3` that isn't installed. Replace it with the reference: `cp solutions/tricon-de-plugin/hooks/validate-bash.sh .cortex/plugins/tricon-de/hooks/`, then rerun."),
    ("*No such file or directory*", "Check the script name and folder match the command above."),
    ("Second command shows `exit code: 2`", "The pattern is too broad. Ask CoCo to block only `--target prod`, then rerun."),
])

PROMPT_3_4 = """Run dbt build --target prod --project-dir dbt/"""

render_prompt("Prompt 3.4", "Test the Hook (should be blocked)", PROMPT_3_4)
st.caption("Paste this in the chat panel, not the terminal.")
render_expected("Either outcome is a pass: (a) CoCo tries the command and the **hook blocks it** with your message, or (b) CoCo **declines up front** because your `AGENTS.md` says never to use `--target prod`. That's two layers of protection. (Even if both were missing, there's no `prod` target in your `profiles.yml`, so dbt would just fail.)")

PROMPT_3_5 = """Use the dbt-review agent to review the changes in this branch."""

render_prompt("Prompt 3.5", "Run the Subagent Locally", PROMPT_3_5)
render_expected("CoCo starts the **dbt-review** subagent, builds each changed model (`orders_summary`, `supplier_performance`) and returns a PASS/FAIL table per convention, ending with an overall **PASS**.")
st.caption("First commit your Module 3 files so the subagent sees them: `git add -A && git commit -m \"Module 3: tricon-de plugin\"`.")

render_explanation("If dbt-review finds no changes", """
The subagent diffs your branch against `origin/main`. If it reports *no changes*, check you're on your feature branch and have committed:

```bash
git status                       # should say: On branch feature/add-tricon-de-plugin
git log --oneline origin/main..HEAD   # should list your commits
```

If you're still on `main`, create the branch and commit:

```bash
git checkout -b feature/add-tricon-de-plugin
git add -A && git commit -m "Add AGENTS.md, tests, skill, and plugin"
```

Then rerun Prompt 3.5. If it says `origin/main` is unknown (you downloaded a ZIP instead of cloning), ask: *Review all models in dbt/models instead of diffing.*
""")

render_key_concepts([
    {"term": "Why hooks matter", "definition": "Agents generate content dynamically, and that non-determinism doesn't belong in a production pipeline. A hook enforces the boundary no matter what the agent decides."},
    {"term": "Hooks are one layer, not the only one", "definition": "This hook only checks shell commands. The real backstop is the lab role, which can't touch anything outside the TRICON_DE database. (All attendees share one role, so it can still write to other attendees' DBT_* schemas; AGENTS.md is what keeps CoCo in yours. In production you'd use a role per schema.) Use hooks *and* least-privilege roles."},
    {"term": "Skill vs. subagent", "definition": "A skill guides an interactive session. A subagent runs to completion on its own, which makes it the right shape for CI and scheduled automations."},
])

render_what_you_built([
    "tricon-de plugin with a versioned manifest and activation notes",
    "PreToolUse hook that blocks dbt --target prod",
    "dbt-review subagent producing a PASS/FAIL report per convention",
])
