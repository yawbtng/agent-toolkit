from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--taste-checkout", type=Path, required=True)
    parser.add_argument("--mattpocock-checkout", type=Path, required=True)
    args = parser.parse_args()
    checkouts = {
        "https://github.com/leonxlnx/taste-skill": args.taste_checkout,
        "https://github.com/mattpocock/skills": args.mattpocock_checkout,
    }
    records = json.loads(args.sources.read_text(encoding="utf-8"))
    imported = []
    for record in records:
        source = checkouts[record["source"]] / record["source_path"]
        destination = args.repo / "plugins" / record["category"] / "skills" / record["name"]
        if destination.exists():
            raise FileExistsError(destination)
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
        imported.append(str(destination.relative_to(args.repo)))
    print(json.dumps({"imported": imported}, indent=2))


if __name__ == "__main__":
    main()
