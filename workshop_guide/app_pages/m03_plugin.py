import streamlit as st
from components import LAB_DB, render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_code, render_guide_change, render_same_as_guide, render_expected, render_troubleshoot, render_before_you_start

render_session_header("Module 3", "Plugin, Hook & Subagent", "25 min", "The coco-de-guide plugin: skill + prod-safety hook + dbt-review subagent")

render_technologies_used([
    {"name": "Plugins", "description": "A versioned, validated, single installable unit that bundles skills, hooks, subagents, and MCP servers.", "icon": "extension"},
    {"name": "PreToolUse hooks", "description": "Shell commands that run before CoCo executes a tool. Use them as hard guardrails, for example blocking production deploys.", "icon": "security"},
    {"name": "Subagents", "description": "Markdown-defined agents that run autonomously to completion on a specific task. The same agent works locally and in CI.", "icon": "smart_toy"},
])

render_before_you_start([
    "Module 2 is done: `supplier_performance` built with the `new-dbt-model` skill.",
    "**Windows:** Git for Windows is installed (Module 0, Step 2). Hooks run with its `bash`.",
    "Start a **new chat** for this module.",
])

st.markdown("""
A skill alone only lives in one workspace, and it isn't versioned or installable alongside a hook or subagent. A **plugin** packages them together.

```
.cortex/plugins/coco-de-guide/
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

render_same_as_guide("Create a Custom Plugin (all prompts word for word)")

st.markdown("#### Step 1: Move the skill into the plugin")
st.markdown("CoCo auto-discovers project plugins in `.cortex/plugins/`. Run these in the CoCo Desktop terminal:")
tab_sh, tab_ps = st.tabs(["macOS / Git Bash", "Windows PowerShell"])
with tab_sh:
    render_code("""cd "$(git rev-parse --show-toplevel)"
mkdir -p .cortex/plugins/coco-de-guide/skills
mv .snowflake/cortex/skills/new-dbt-model .cortex/plugins/coco-de-guide/skills/
rm -rf .snowflake/""")
with tab_ps:
    render_code("""cd (git rev-parse --show-toplevel)
New-Item -ItemType Directory -Force .cortex/plugins/coco-de-guide/skills | Out-Null
Move-Item .snowflake/cortex/skills/new-dbt-model .cortex/plugins/coco-de-guide/skills/
Remove-Item -Recurse -Force .snowflake""", language="powershell")
render_expected("The skill is now at `.cortex/plugins/coco-de-guide/skills/new-dbt-model/SKILL.md`, and the Explorer no longer shows a `.snowflake` folder in the project.")
render_guide_change(
    "Starts with `mkdir -p ...`.",
    "One line added first: `cd` to the repository root.",
    "`rm -rf .snowflake/` must run in the project. In your home folder it would delete `~/.snowflake`, which holds your Snowflake connections.")
render_troubleshoot([
    ("*not a git repository*", "The terminal isn't in the project. **File → Open Folder** on the project, open a new terminal, and run the block again."),
    ("*No such file or directory* on the `mv` line", "The skill isn't at `.snowflake/cortex/skills/new-dbt-model`. Check Module 2's Prompt 2.2, or copy the reference: `mkdir -p .cortex/plugins/coco-de-guide/skills && cp -R part2/solutions/coco-de-guide/skills/new-dbt-model .cortex/plugins/coco-de-guide/skills/`."),
])

PROMPT_3_1 = """Consult the CoCo Desktop plugin
documentation at https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop/plugins
for the correct plugin.json schema and file structure.

Create a CoCo plugin manifest for this project at .cortex/plugins/coco-de-guide/.cortex-plugin/plugin.json.

The manifest must include all of the following fields:
- name: "coco-de-guide"
- version: 1.0.0
- author: me
- skills: pointing to ./skills
- agents: pointing to ./agents
- hooks: pointing to ./hooks/hooks.json

Also create .cortex/plugins/coco-de-guide/.cortex-plugin/activation.md that briefly explains
what the plugin includes.

Do not use the cortex CLI — write the files directly."""

render_prompt("Prompt 3.1", "Create the Plugin Manifest", PROMPT_3_1)
render_expected("Two new files: `.cortex/plugins/coco-de-guide/.cortex-plugin/plugin.json` and `activation.md` next to it.")

render_explanation("Expected plugin.json", """
```json
{
  "name": "coco-de-guide",
  "description": "dbt/Snowflake data engineering plugin for the CoCo DE Guide",
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

Create a PreToolUse hook at .cortex/plugins/coco-de-guide/hooks/validate-bash.sh that blocks
any dbt command that includes --target prod. If the command is blocked, return a clear error
message explaining that direct production dbt runs are not allowed and to use the CI/CD
pipeline instead.
Also create .cortex/plugins/coco-de-guide/hooks/hooks.json that wires this script to the
PreToolUse event using the matcher value "bash" (lowercase)."""

render_prompt("Prompt 3.2", "Create the Prod-Safety Hook", PROMPT_3_2)
render_expected("Two new files: `hooks/validate-bash.sh` and `hooks/hooks.json` under `.cortex/plugins/coco-de-guide/`.")

render_explanation("Expected hooks.json", """
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "bash",
        "hooks": [
          { "type": "command", "command": "bash .cortex/plugins/coco-de-guide/hooks/validate-bash.sh", "timeout": 10 }
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

Create a dbt-review subagent at .cortex/plugins/coco-de-guide/agents/dbt-review.md.
The subagent should:
- Find all changed dbt model files compared to origin/main
- For each changed model, run dbt build --select <model> --project-dir dbt/
- Verify that each convention from the new-dbt-model skill is met
- Produce a concise PASS/FAIL report per convention with specific remediation steps for any failures

It should use the bash, read, grep, and glob tools. Set the model to auto."""

render_prompt("Prompt 3.3", "Create the dbt-review Subagent", PROMPT_3_3)
render_expected("A new `.cortex/plugins/coco-de-guide/agents/dbt-review.md` with frontmatter (`name`, `description`, `tools`, `model: auto`) and the four review steps.")

st.markdown("#### Step 4: Activate and test")
st.markdown("""
1. Open **Settings** (gear icon, bottom of the left sidebar) → **Plugins**.
2. Find `coco-de-guide`. If it's toggled off, turn it on. If it's missing, click **↻**.
3. Open the plugin card and confirm the skill, hook, and subagent are listed.

:material/info: Project plugins only auto-activate in a **trusted** workspace.
""")
render_expected("The `coco-de-guide` card is **on** and lists 1 skill (`new-dbt-model`), 1 agent (`dbt-review`) and 1 hook (`PreToolUse`).")
render_troubleshoot([
    ("`coco-de-guide` isn't listed", "Click **↻**. Check the manifest path is exactly `.cortex/plugins/coco-de-guide/.cortex-plugin/plugin.json`. Still missing: compare with `part2/solutions/coco-de-guide/.cortex-plugin/plugin.json`."),
    ("The card shows a validation error", "Ask CoCo: *Validate my plugin.json against the plugin docs and fix it.* Or copy the reference manifest from `solutions/`."),
    ("Hooks section is empty", "`hooks.json` path in `plugin.json` must be `./hooks/hooks.json`. Then toggle the plugin off and on."),
    ("The workspace isn't trusted", "Command Palette (`Cmd/Ctrl+Shift+P`) → *Manage Workspace Trust* → **Trust**."),
])

st.markdown("**Optional: test the hook directly first.** This sends the hook exactly what CoCo would send, so you see it block without involving the AI:")
render_code("""echo '{"tool_input":{"command":"dbt build --target prod --project-dir dbt/"}}' | bash .cortex/plugins/coco-de-guide/hooks/validate-bash.sh; echo "exit code: $?"
echo '{"tool_input":{"command":"dbt build --project-dir dbt/"}}' | bash .cortex/plugins/coco-de-guide/hooks/validate-bash.sh; echo "exit code: $?\"""")
st.caption("Windows: run these in **Git Bash** (Start menu → Git Bash, then `cd` to the project folder).")
render_expected("First command: your *Blocked...* message and **`exit code: 2`**. Second command: **`exit code: 0`** (dev runs are allowed).")
render_troubleshoot([
    ("First command shows `exit code: 0`", "The hook didn't recognize the command. A common cause is a script that relies on `jq` or `python3` that isn't installed. Ask CoCo: *Rewrite validate-bash.sh using only bash and grep*, or copy the reference: `cp part2/solutions/coco-de-guide/hooks/validate-bash.sh .cortex/plugins/coco-de-guide/hooks/`, then rerun."),
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
st.info(""":material/info: **If it says there are no changes:** that's expected at this point. The subagent compares with `origin/main`, and you haven't committed anything yet (that's Module 4). Send this instead:

*Use the dbt-review agent to review the changes in this branch, including uncommitted and untracked files.*""")
st.caption("If it says `origin/main` is unknown (you downloaded a ZIP instead of cloning), ask: *Review all models in dbt/models instead of diffing.*")

render_key_concepts([
    {"term": "Why hooks matter", "definition": "Agents generate content dynamically, and that non-determinism doesn't belong in a production pipeline. A hook enforces the boundary no matter what the agent decides."},
    {"term": "Hooks are one layer, not the only one", "definition": f"This hook only checks shell commands. The real backstop is the role: DEMO_ROLE can only create objects in {LAB_DB}. Everyone in this workshop shares that role, so it could write to a neighbour's schema; AGENTS.md and your `profiles.yml` are what keep CoCo in yours. In production, give each team or environment its own role. Use hooks *and* least-privilege roles."},
    {"term": "Skill vs. subagent", "definition": "A skill guides an interactive session. A subagent runs to completion on its own, which makes it the right shape for CI and scheduled automations."},
])

render_what_you_built([
    "coco-de-guide plugin with a versioned manifest and activation notes",
    "PreToolUse hook that blocks dbt --target prod",
    "dbt-review subagent producing a PASS/FAIL report per convention",
])
