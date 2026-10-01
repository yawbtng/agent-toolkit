from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--curation", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.curation.read_text(encoding="utf-8"))
    baseline_root = args.repo / "skills"
    baseline_root.mkdir(exist_ok=True)
    moved = []
    for name in plan["baseline"]:
        matches = list((args.repo / "plugins").glob(f"*/skills/{name}"))
        if len(matches) != 1:
            raise RuntimeError(f"Expected one source for {name}, found {matches}")
        destination = baseline_root / name
        if destination.exists():
            raise FileExistsError(destination)
        shutil.move(str(matches[0]), destination)
        moved.append({"name": name, "source": str(matches[0].relative_to(args.repo))})
    output = args.repo / "inventory/curation-report.json"
    output.write_text(json.dumps({"baseline": moved}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"baseline_skills": len(moved)}, indent=2))


if __name__ == "__main__":
    main()
