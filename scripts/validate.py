from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:[-.][a-z0-9]+)*$")
SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{24,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{24,}\b"),
    re.compile(r"\bsbp_[A-Za-z0-9]{24,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{32,}\b"),
]


def metadata(text: str) -> dict[str, str]:
    if not text.startswith("---\n") or text.count("---") < 2:
        return {}
    block = text.split("---", 2)[1]
    values = {}
    active_key = None
    for line in block.splitlines():
        match = re.match(r"^([A-Za-z][\w-]*):\s*[\"']?(.*?)[\"']?\s*$", line)
        if match:
            active_key = match.group(1)
            values[active_key] = match.group(2)
        elif active_key and line.startswith((" ", "\t")):
            values[active_key] = f"{values[active_key]} {line.strip()}".strip()
        else:
            active_key = None
    return values


def main() -> int:
    errors = []
    warnings = []
    manifests = [ROOT / ".devin-plugin/plugin.json", *ROOT.glob("plugins/*/.devin-plugin/plugin.json")]
    plugin_names = set()
    for path in manifests:
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid manifest: {exc}")
            continue
        name = manifest.get("name", "")
        if not NAME_PATTERN.fullmatch(name):
            errors.append(f"{path}: invalid plugin name {name!r}")
        if name in plugin_names:
            errors.append(f"{path}: duplicate plugin name {name}")
        plugin_names.add(name)

    names: dict[str, list[Path]] = defaultdict(list)
    categories = Counter()
    skill_paths = [*ROOT.glob("skills/*/SKILL.md"), *ROOT.glob("plugins/*/skills/*/SKILL.md")]
    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        values = metadata(text)
        name = values.get("name", "")
        description = values.get("description", "")
        if not name:
            errors.append(f"{path}: missing frontmatter name")
            continue
        if not description:
            errors.append(f"{path}: missing frontmatter description")
        if not NAME_PATTERN.fullmatch(name):
            errors.append(f"{path}: invalid skill name {name!r}")
        if path.parent.name != name:
            warnings.append(f"{path}: directory {path.parent.name!r} differs from name {name!r}")
        names[name].append(path)
        relative = path.relative_to(ROOT)
        category = "baseline" if relative.parts[0] == "skills" else relative.parts[1]
        categories[category] += 1
        if "/Users/yawbt" in text:
            errors.append(f"{path}: contains an absolute local home path")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            errors.append(f"{path}: contains a value resembling a secret")
    for name, paths in names.items():
        if len(paths) > 1:
            errors.append(f"duplicate skill name {name}: {', '.join(map(str, paths))}")
    report = {
        "plugins": len(manifests),
        "skills": len(names),
        "categories": dict(sorted(categories.items())),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
