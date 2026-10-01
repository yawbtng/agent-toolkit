from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

DEFAULT_ROOTS = [
    Path.home() / ".config/devin/skills",
    Path.home() / ".agents/skills",
    Path.home() / ".claude/skills",
    Path.home() / ".cursor/skills",
    Path.home() / ".github/skills",
]
SKIP_PARTS = {"cache", "marketplaces", "plugins", "synced"}
SKIP_PREFIXES = ("gstack.bak-",)
CATEGORY_TERMS = {
    "design": {
        "accessibility", "adapt", "animate", "animation", "arrange", "audit", "bolder",
        "canvas", "color", "critique", "delight", "design", "figma", "frontend-design",
        "hallmark", "motion", "onboard", "polish", "responsive", "typography", "typeset",
        "ui", "ux", "visual",
    },
    "frontend": {
        "component", "css", "d3", "html", "javascript", "next", "performance", "react",
        "remotion", "shadcn", "tailwind", "typescript", "vercel", "web", "webapp",
    },
    "knowledge": {
        "article", "context", "docs", "document", "epub", "extractor", "memory", "notion",
        "pdf", "recall", "research", "synthesis", "wiki", "xlsx",
    },
    "productivity": {
        "automation", "email", "meeting", "n8n", "organizer", "resume", "screenpipe",
        "slack", "worklog", "workflow",
    },
}


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    _, block, _ = text.split("---", 2)
    values: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^([A-Za-z][\w-]*):\s*[\"']?(.*?)[\"']?\s*$", line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def category(name: str, description: str) -> str:
    words = set(re.findall(r"[a-z0-9-]+", f"{name} {description}".lower()))
    scores = {key: len(words & terms) for key, terms in CATEGORY_TERMS.items()}
    winner = max(scores, key=scores.get)
    return winner if scores[winner] else "core"


def discover(roots: list[Path]) -> list[dict[str, object]]:
    records = []
    for precedence, root in enumerate(roots):
        if not root.exists():
            continue
        for path in sorted(root.glob("**/SKILL.md")):
            relative_parts = path.relative_to(root).parts
            if any(part in SKIP_PARTS or part.startswith(SKIP_PREFIXES) for part in relative_parts):
                continue
            text = path.read_text(encoding="utf-8")
            metadata = frontmatter(text)
            name = metadata.get("name") or path.parent.name
            description = metadata.get("description", "")
            records.append(
                {
                    "name": name,
                    "description": description,
                    "path": str(path),
                    "root": str(root),
                    "precedence": precedence,
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "category": category(name, description),
                    "bytes": len(text.encode()),
                }
            )
    return records


def summarize(records: list[dict[str, object]]) -> dict[str, object]:
    by_name: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_hash: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        by_name[str(record["name"])].append(record)
        by_hash[str(record["sha256"])].append(record)
    canonical = []
    for name, candidates in sorted(by_name.items()):
        selected = min(candidates, key=lambda item: (int(item["precedence"]), str(item["path"])))
        canonical.append(
            {
                **selected,
                "alternatives": [item["path"] for item in candidates if item["path"] != selected["path"]],
                "exact_duplicate_count": len(by_hash[str(selected["sha256"])]) - 1,
            }
        )
    return {
        "summary": {
            "files": len(records),
            "unique_names": len(by_name),
            "unique_contents": len(by_hash),
            "duplicate_names": sum(1 for values in by_name.values() if len(values) > 1),
            "exact_duplicate_groups": sum(1 for values in by_hash.values() if len(values) > 1),
        },
        "canonical": canonical,
        "duplicate_names": {
            name: [item["path"] for item in values]
            for name, values in sorted(by_name.items())
            if len(values) > 1
        },
        "exact_duplicates": [
            [item["path"] for item in values]
            for values in by_hash.values()
            if len(values) > 1
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("roots", nargs="*", type=Path)
    args = parser.parse_args()
    result = summarize(discover(args.roots or DEFAULT_ROOTS))
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
