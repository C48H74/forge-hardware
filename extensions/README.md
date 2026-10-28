# Forge Hardware extension library

Use the same editable CAD workflow in different coding agents. These packages
share [one canonical skill](../skills/forge-hardware/SKILL.md), the Forge CLI,
and its local browser viewer. They do not add an embedded CAD tab to a host app.

## Choose your platform

| Platform | Package | Install route |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` + marketplace | Claude plugin commands below |
| Codex | Portable `plugin.json`, Codex overlay and `.agents/plugins/marketplace.json` | Add the repo marketplace, then install in the plugin browser |
| Cursor | `.cursor-plugin/plugin.json` + marketplace | Local plugin checkout or repository marketplace |
| Gemini CLI | `gemini-extension.json` | Gemini extension command below |
| Other agents with Agent Plugins support | Root `plugin.json` | Use the host's Agent Plugins installer |
| Other agents with Agent Skills support | `skills/forge-hardware/` | Copy the complete skill folder into the host's documented skill location |

Install one route per agent. Installing both a plugin and a standalone copy of
the skill can show duplicate skills.

## Set up the CAD runtime

The extension supplies agent instructions. Actual modeling needs a separate
stable checkout and Python 3.11–3.13 with build123d/OpenCascade dependencies.
No published PyPI release of Forge Hardware is assumed.

```bash
git clone https://github.com/C48H74/forge-hardware.git
cd forge-hardware
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
python -m forge_hardware --help
python -m forge_hardware build examples/fixture.py -o build/fixture
python -m forge_hardware view build/fixture
```

Tell the agent the absolute checkout path and virtual environment Python path.
The skill can guide setup if the runtime is absent. Always use that interpreter
for CAD commands. The local viewer URL must be opened on the machine running it.

## Claude Code

```bash
claude plugin marketplace add C48H74/forge-hardware
claude plugin install forge-hardware@forge-hardware
```

Update the marketplace with `claude plugin marketplace update forge-hardware`,
then the plugin with `claude plugin update forge-hardware@forge-hardware`.
Remove with `claude plugin uninstall forge-hardware@forge-hardware`.
For a local development checkout, use `claude --plugin-dir /absolute/forge-hardware`.

## Codex

```bash
codex plugin marketplace add C48H74/forge-hardware --ref main
```

Open `/plugins` in Codex CLI, choose the **Forge Hardware** marketplace and
install **Forge Hardware**. The repo marketplace is separate from OpenAI's public
directory. This repository has not been submitted to that directory.

For Codex environments using standalone local skills instead:

```bash
python scripts/install_agent_skill.py --agent codex
```

This copies the complete skill to `~/.agents/skills/forge-hardware`. A terminal
copy does not install a personal skill in a separate ChatGPT web account.

## Cursor

Local plugin installation:

```bash
git clone https://github.com/C48H74/forge-hardware.git ~/.cursor/plugins/local/forge-hardware
```

Load the plugin using Cursor's local-plugin workflow. Alternatively, import
`C48H74/forge-hardware` as a repository marketplace in Customize and install its
Forge Hardware entry. Update a local checkout with
`git -C ~/.cursor/plugins/local/forge-hardware pull --ff-only`.

Standalone skill alternative: `python scripts/install_agent_skill.py --agent cursor`.

## Gemini CLI

```bash
gemini extensions install https://github.com/C48H74/forge-hardware
gemini extensions list
```

Verify that the extension and its `forge-hardware` skill are enabled with the
host's `/extensions` and `/skills` controls. For local development, run
`gemini extensions link /absolute/forge-hardware`.

Update with `gemini extensions update forge-hardware`; remove with
`gemini extensions uninstall forge-hardware`.

Standalone skill alternative: `python scripts/install_agent_skill.py --agent gemini`.

## Install only the skill

From this checkout, the portable installer supports four documented locations:

```bash
python scripts/install_agent_skill.py --agent claude --dry-run
python scripts/install_agent_skill.py --agent claude
python scripts/install_agent_skill.py --agent codex --project /absolute/hardware-project
```

| Agent | User location | Project location |
|---|---|---|
| Codex | `~/.agents/skills/forge-hardware` | `.agents/skills/forge-hardware` |
| Claude Code | `~/.claude/skills/forge-hardware` | `.claude/skills/forge-hardware` |
| Cursor | `~/.cursor/skills/forge-hardware` | `.cursor/skills/forge-hardware` |
| Gemini CLI | `~/.gemini/skills/forge-hardware` | `.gemini/skills/forge-hardware` |

The installer needs Python 3.11+, uses only the standard library, copies all
references and assets, and refuses to overwrite an existing installation.
To update, move the old skill folder aside, rerun the installer, then compare any
local customizations before removing the backup. It does not install packages,
edit host configuration, or register servers.

## First request and smoke test

Ask your agent:

> Use Forge Hardware from /absolute/forge-hardware and its virtual environment.
> Create a 90 × 60 × 8 mm fixture plate with four 5.5 mm mounting holes,
> 10 mm from each edge. Keep the Python source, export STEP and STL, and show
> the local preview. Then enlarge only the front-left hole to 6.5 mm.

Confirm skill discovery, runtime import, exported file creation and viewer
operation in each target app. Plugins need an agent with local command execution;
an instruction-only host cannot run the CAD kernel itself.

## Validation and compatibility

Automated checks cover manifest generation/version consistency, existing skill
paths, complete installation into isolated directories, dry-run behavior,
collision refusal and dangling-symlink preservation. Run:

```bash
python scripts/build_extensions.py --check
python -m unittest discover -s tests -p test_extensions.py -v
```

Interactive installation and end-to-end modeling inside Claude, Codex, Cursor
and Gemini have **not** been exercised by these packaging tests. Host versions
and enterprise policies may affect installation. These are ready-to-test
packages, not a claim of app-store publication or host certification.

The current integrations use the CLI workflow. The existing optional legacy MCP
server remains described in [agent setup](../docs/agents.md); these packages do
not register or launch it automatically.

## Maintain and extend the library

Edit the package version in `pyproject.toml`, then run
`python scripts/build_extensions.py` to regenerate platform manifests.
Keep platform-specific metadata in that generator and shared modeling behavior
in the canonical skill. Add a platform only after confirming its official
package format; include installation, update, removal and a smoke test.

Packaging approach inspired by [text-to-cad](https://github.com/earthtojake/text-to-cad).
Forge Hardware uses its own runtime and does not depend on cadgen.

Format references:

- [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Cursor plugins reference](https://cursor.com/docs/reference/plugins)
- [Gemini extension reference](https://geminicli.com/docs/extensions/reference/)
