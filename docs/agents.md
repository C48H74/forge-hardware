# Agent installation

For platform packages, installation commands and standalone skill locations,
see the [extension library](../extensions/README.md).

1. Clone the repository into a stable tools directory.
2. Create a clean virtual environment and install the toolkit with `python -m pip install -e /absolute/checkout`.
3. Copy `skills/forge-hardware` into the coding agent's skill directory, or include its `SKILL.md` as instructions.
4. Point the agent at your hardware project, use the installed environment's Python, and keep source/assets under version control.
5. Ask for a preview and regenerated exports on every geometry change.

The skill contains an executable launcher and a reference for the source/robot schema. It does not include or require API keys. Natural language is interpreted by your coding agent; this package itself is a deterministic CAD tool.

## Optional MCP stdio

The CLI provides the most portable interface. For a host supporting legacy MCP initialization (protocol 2024-11-05), configure a local stdio process using your host's documented mechanism:

- executable: `/absolute/checkout/.venv/bin/python` (on Windows: `.venv\Scripts\python.exe`)
- arguments: `-m forge_hardware mcp --workspace /absolute/hardware-project`

Tools: `build_design`, `inspect_design`, `preview_design`, `search_parts`, `download_part`.

The server uses newline-delimited JSON-RPC and reserves stdout for protocol messages. It does not implement the newer 2026 protocol era, remote HTTP MCP, OAuth, resources or interactive approval prompts. The host must enforce its own permissions. Review and trust this server before registering it; registration is not performed automatically by installation.

## Source trust

Only run model scripts created or reviewed in the local project. Geometry downloads must remain data. Model Python executes with the current user's file and network access. The MCP workspace restriction limits tool path arguments; it cannot restrict Python code inside a model script.
