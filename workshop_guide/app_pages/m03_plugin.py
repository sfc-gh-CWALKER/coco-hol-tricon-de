import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built, render_code, render_guide_change, render_new_for_tricon

render_session_header("Module 3", "Plugin, Hook & Subagent", "25 min", "The tricon-de plugin: skill + prod-safety hook + dbt-review subagent")

render_technologies_used([
    {"name": "Plugins", "description": "A versioned, validated, single installable unit that bundles skills, hooks, subagents, and MCP servers.", "icon": "extension"},
    {"name": "PreToolUse hooks", "description": "Shell commands that run before CoCo executes a tool. Use them as hard guardrails, for example blocking production deploys.", "icon": "security"},
    {"name": "Subagents", "description": "Markdown-defined agents that run autonomously to completion on a specific task. The same agent works locally and in CI.", "icon": "smart_toy"},
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
    "Plugin `tricon-de` in `.cortex/plugins/tricon-de/`; the manifest also has a `description`. Prompts 3.2–3.5 are otherwise word-for-word.",
    "Tricon-branded, and it becomes the home for the Part 2 skills and subagents.")

st.markdown("#### Step 1: Move the skill into the plugin")
st.markdown("CoCo auto-discovers project plugins in `.cortex/plugins/`. Run these in the terminal:")
render_code("""mkdir -p .cortex/plugins/tricon-de/skills
mv .snowflake/cortex/skills/new-dbt-model .cortex/plugins/tricon-de/skills/
rm -rf .snowflake/""")

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
Also create .cortex/plugins/tricon-de/hooks/hooks.json that wires this script to the
PreToolUse event using the matcher value "bash" (lowercase)."""

render_prompt("Prompt 3.2", "Create the Prod-Safety Hook", PROMPT_3_2)

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

st.markdown("#### Step 4: Activate and test")
st.markdown("""
1. Open **Settings** (gear icon, bottom of the left sidebar) → **Plugins**.
2. Find `tricon-de`. If it's toggled off, turn it on. If it's missing, click **↻**.
3. Open the plugin card and confirm the skill, hook, and subagent are listed.

:material/info: Project plugins only auto-activate in a **trusted** workspace.
""")

PROMPT_3_4 = """Run dbt build --target prod --project-dir dbt/"""

render_prompt("Prompt 3.4", "Test the Hook (should be blocked)", PROMPT_3_4)
st.caption("Paste this in the chat panel, not the terminal. The hook should block it before it runs.")

PROMPT_3_5 = """Use the dbt-review agent to review the changes in this branch."""

render_prompt("Prompt 3.5", "Run the Subagent Locally", PROMPT_3_5)

render_explanation("If dbt-review finds no changes", """
The subagent diffs against `origin/main`. If you haven't committed anything yet, create a branch and commit first:

```bash
git checkout -b feature/add-tricon-de-plugin
git add -A && git commit -m "Add AGENTS.md, tests, skill, and plugin"
```

Then rerun Prompt 3.5.
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
