"""Copy the complete Forge skill to a local agent, without installing runtime code."""
import argparse
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
AGENTS = {"codex": ".agents/skills", "claude": ".claude/skills",
          "cursor": ".cursor/skills", "gemini": ".gemini/skills"}


def install(agent, base, dry_run=False):
    source = ROOT / "skills/forge-hardware"
    target = Path(base).expanduser().absolute() / AGENTS[agent] / "forge-hardware"
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Already exists: {target}. Keep it, or move it aside before reinstalling.")
    if dry_run:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    # Stage the complete skill before publishing it, including references/assets.
    with tempfile.TemporaryDirectory(prefix=".forge-install-", dir=target.parent) as temp:
        staged = Path(temp) / "forge-hardware"
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if not (staged / "SKILL.md").is_file():
            raise FileNotFoundError("Source skill has no SKILL.md")
        staged.rename(target)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, choices=AGENTS)
    parser.add_argument("--project", type=Path, help="Install for this project instead of the current user")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        target = install(args.agent, args.project if args.project is not None else Path.home(), args.dry_run)
    except (OSError, shutil.Error) as error:
        parser.exit(1, str(error) + "\n")
    print(("Would install: " if args.dry_run else "Installed: ") + str(target))
    print("Set up the CAD runtime separately; see extensions/README.md.")


if __name__ == "__main__":
    main()
