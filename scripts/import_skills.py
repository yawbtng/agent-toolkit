from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

EXCLUDED_NAMES = {
    "devin-cli",
}
EXCLUDED_PARTS = {
    ".git",
    ".DS_Store",
    "__pycache__",
    "node_modules",
}


def ignore(_: str, names: list[str]) -> set[str]:
    return {name for name in names if name in EXCLUDED_PARTS}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    imported = []
    skipped = []
    for record in inventory["canonical"]:
        name = record["name"]
        if name in EXCLUDED_NAMES:
            skipped.append({"name": name, "reason": "built-in skill"})
            continue
        source = Path(record["path"]).parent
        category = record["category"]
        destination = args.repo / "plugins" / category / "skills" / name
        if destination.exists():
            skipped.append({"name": name, "reason": "destination exists"})
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, ignore=ignore, symlinks=False)
        imported.append(
            {
                "name": name,
                "category": category,
                "source": str(source),
                "destination": str(destination.relative_to(args.repo)),
                "sha256": record["sha256"],
            }
        )
    report = {"imported": imported, "skipped": skipped}
    output = args.repo / "inventory/import-report.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"imported": len(imported), "skipped": len(skipped)}, indent=2))


if __name__ == "__main__":
    main()
