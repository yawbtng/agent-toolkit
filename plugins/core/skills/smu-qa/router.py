#!/usr/bin/env python3
"""
SMU Q&A Router — Universal topic routing for the SMU wiki.
Handles: topic detection, keyword matching, follow-up resolution, session memory.
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

WIKI_ROOT = Path(os.environ["SMU_WIKI_ROOT"])
INDEX_FILE = WIKI_ROOT / "index.md"
MEMORY_FILE = WIKI_ROOT / ".qa_memory.json"
MEMORY_LIMIT = 10  # Keep last 10 Q&A pairs

# ── Topic keywords ───────────────────────────────────────────────────────────────
TOPIC_KEYWORDS = {
    "lyle": {
        "keywords": ["lyle", "engineering school", "lyle school", "bobby lyle", "deans office", "lyle departments", "engineering faculty", "lyle faculty"],
        "category": "lyle",
        "priority": 10,
    },
    "admission": {
        "keywords": ["admission", "apply", "deadline", "gpa", "sat", "act", "transfer", "freshman", "undergraduate admission", "graduate admission", "application fee", "scholarship", "financial aid", "tuition", "cost", "housing", "dorm", "room and board", "enrollment"],
        "category": "admission",
        "priority": 9,
    },
    "academics": {
        "keywords": ["academic", "major", "minor", "degree", "program", "course", "class", "curriculum", "credit", "gpa requirement", "abt accreditation", "abet", "dual degree", "accelerated pathway", "pre-med", "pre-law"],
        "category": "academics",
        "priority": 7,
    },
    "abroad": {
        "keywords": ["abroad", "study abroad", "exchange", "international", "summer abroad", "semester abroad", "study away", "foreign country", "visa", "i-20", "cpt", "opt"],
        "category": "abroad",
        "priority": 8,
    },
    "student_affairs": {
        "keywords": ["student life", "student affair", "club", "organization", "fraternity", "sorority", "health", "counseling", "career center", "internship", "job", "housing", "residential", "dining", "food", "mustang", "athletics", "sport", "fitness", "wellbeing", "safety", "police", "mental health"],
        "category": "student-affairs",
        "priority": 6,
    },
    "research": {
        "keywords": ["research", "surge", "fellowship", "phd", "doctoral", "graduate research", "lab", "publication", "semiconductor", "quantum", "cybersecurity", "ai", "machine learning", "manufacturing", "innovation"],
        "category": "research",
        "priority": 7,
    },
    "aboutsmu": {
        "keywords": ["about smu", "about southern", "history", "president", "administr", "mission", "vision", "campus", "location", "dallas", "address", "building", "parking", "map", "directions", "fact", "ranking", "r1", "research university", "private", "public university", "size", "enrollment", "founded", "ranking", "ranked", "student body", "student population", "dallas location", "near dallas", "smu is a", "southern methodist"],
        "category": "aboutsmu",
        "priority": 6,
    },
    "schools": {
        "keywords": ["cox", "business school", "meadows", "arts school", "dedman", "law school", "perkins", "theology", "simmons", "education school", "moody", "graduate school", "guildhall", "game design", "cape"],
        "category": "schools",
        "priority": 6,
    },
    "libraries": {
        "keywords": ["library", "libraries", "fondren", "bridwell", "hamon", "research resource", "database", "journal"],
        "category": "libraries",
        "priority": 6,
    },
    "online": {
        "keywords": ["online", "distance learning", "remote", "lync", "remote learning", "flexible", "weekend program", "executive education"],
        "category": "online",
        "priority": 7,
    },
    "general": {
        "keywords": [],
        "category": "general",
        "priority": 1,
    },
}

CATEGORY_DIRS = {
    "lyle": WIKI_ROOT / "lyle-wiki",
    "aboutsmu": WIKI_ROOT / "aboutsmu",
    "admission": WIKI_ROOT / "admission",
    "academics": WIKI_ROOT / "academics",
    "abroad": WIKI_ROOT / "abroad",
    "student-affairs": WIKI_ROOT / "student-affairs",
    "research": WIKI_ROOT / "research",
    "libraries": WIKI_ROOT / "libraries",
    "schools": WIKI_ROOT / "schools",
    "online": WIKI_ROOT / "online",
    "bushcenter": WIKI_ROOT / "bushcenter",
    "general": WIKI_ROOT / "general",
}

CATEGORY_LABELS = {
    "lyle": "Lyle School of Engineering",
    "aboutsmu": "About SMU",
    "admission": "Admission",
    "academics": "Academics",
    "abroad": "Study Abroad",
    "student-affairs": "Student Affairs",
    "research": "Research",
    "libraries": "Libraries",
    "schools": "Other SMU Schools",
    "online": "Online Learning",
    "bushcenter": "Bush Center",
    "general": "General",
}


# ── Session memory ─────────────────────────────────────────────────────────────

def load_memory() -> dict:
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text())
        except Exception:
            pass
    return {"history": [], "session_start": datetime.now().isoformat()}


def save_memory(memory: dict):
    # Keep only last MEMORY_LIMIT entries
    memory["history"] = memory["history"][-MEMORY_LIMIT:]
    memory["last_updated"] = datetime.now().isoformat()
    try:
        MEMORY_FILE.write_text(json.dumps(memory, indent=2))
    except Exception:
        pass


def add_to_memory(memory: dict, question: str, answer: str, sources: list[dict]):
    memory["history"].append({
        "question": question,
        "answer": answer[:300],  # Truncate for space
        "sources": [{"title": s.get("title", ""), "file": s.get("file", "")} for s in sources],
        "timestamp": datetime.now().isoformat(),
    })


def get_relevant_history(memory: dict, question: str) -> list[dict]:
    """Return Q&A pairs that might be relevant to the current question."""
    if not memory.get("history"):
        return []
    q_lower = question.lower()
    relevant = []
    for entry in reversed(memory["history"][-5:]):  # Last 5 only
        # Check keyword overlap
        entry_words = set(entry["question"].lower().split())
        q_words = set(q_lower.split())
        overlap = entry_words & q_words
        if len(overlap) >= 2 or any(kw in q_lower for kw in entry["question"].lower().split()[:3]):
            relevant.append(entry)
    return relevant


# ── Topic routing ───────────────────────────────────────────────────────────────

def detect_topics(question: str) -> list[tuple[str, int]]:
    """Detect which topics the question relates to. Returns [(topic, score), ...]."""
    q_lower = question.lower()
    scores = []

    for topic, info in TOPIC_KEYWORDS.items():
        score = 0
        for kw in info["keywords"]:
            if kw in q_lower:
                score += 1
        if score > 0:
            scores.append((topic, score * info["priority"]))
        elif topic == "general":
            scores.append((topic, 1))

    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def find_matching_files(question: str, topics: list[tuple[str, int]], top_k: int = 8) -> list[dict]:
    """Find the most relevant wiki files for the question."""
    q_lower = question.lower()
    q_words = set(re.findall(r'\b\w+\b', q_lower))
    q_words -= {
        "smu", "the", "and", "for", "are", "does", "what", "how", "when", "where",
        "can", "you", "all", "any", "some", "much", "many", "about", "from", "with",
        "this", "that", "than", "them", "they", "have", "has", "had", "was", "were",
        "will", "would", "could", "should", "is", "it", "its", "or", "to", "of", "in",
        "on", "at", "by", "not", "be", "but", "do", "if", "so", "as", "your", "i",
    }
    results = []

    # Always search the primary (top-scoring) topic first, plus general
    topics_to_search = topics[:3] if topics else [("general", 1)]

    for topic, _ in topics_to_search:
        cat_dir = CATEGORY_DIRS.get(topic)
        if not cat_dir or not cat_dir.exists():
            continue

        for md_file in cat_dir.rglob("*.md"):
            if md_file.is_file():
                # Read title from frontmatter or first heading
                try:
                    content = md_file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                # Extract title
                title = extract_title(content, md_file)

                # Extract description from frontmatter
                desc = extract_description(content)

                # Score by keyword overlap with title + description
                score = score_file(q_words, title, desc, content, q_lower, topic)

                if score > 0:
                    results.append({
                        "file": str(md_file),
                        "title": title,
                        "description": desc[:200] if desc else "",
                        "category": topic,
                        "category_label": CATEGORY_LABELS.get(topic, topic),
                        "score": score,
                        "size": len(content),
                    })

    # Dedupe and sort
    seen = {}
    for r in results:
        key = r["file"]
        if key not in seen or r["score"] > seen[key]["score"]:
            seen[key] = r
    results = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def extract_title(content: str, path: Path) -> str:
    """Extract title from frontmatter or first heading."""
    # Try frontmatter title
    m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Try first heading
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return path.stem.replace("-", " ").replace("_", " ").title()


def extract_description(content: str) -> str:
    """Extract description from frontmatter."""
    m = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return ""


def score_file(q_words: set, title: str, desc: str, content: str, q_lower: str, topic: str = "general") -> float:
    """Score how relevant a file is to the question."""
    score = 0.0
    title_lower = title.lower()
    desc_lower = desc.lower()
    content_lower = content.lower()

    # Title exact match bonus
    for word in q_words:
        if len(word) < 3:
            continue
        if word in title_lower:
            score += 10
        if word in desc_lower:
            score += 3
        if word in content_lower:
            score += 0.5

    # Specific number/date patterns
    if re.search(r'\b(gpa|sat|act|\d{4})\b', q_lower) and re.search(r'\b(gpa|sat|act|\d{4})\b', content_lower):
        score += 5

    # Admission/deadline keywords
    if any(kw in q_lower for kw in ["deadline", "due date", "apply by"]):
        if any(kw in content_lower for kw in ["deadline", "due date", "apply by", "priority"]):
            score += 8

    # Cost/tuition keywords → admission category content bonus
    if any(kw in q_lower for kw in ["cost", "tuition", "fee", "price"]):
        if any(kw in content_lower for kw in ["tuition", "cost", "fee", "price", "room and board"]):
            score += 25
    if any(kw in q_lower for kw in ["scholarship", "scholarships", "financial", "aid"]):
        if any(kw in content_lower for kw in ["scholarship", "grant", "aid", "award", "merit"]):
            score += 25

    # Category-match bonus: primary topic files get a modest boost to rise above
    # the "general" noise. Not a knockout bonus — content relevance still wins.
    if topic not in ("general",):
        score += 5

    return score


# ── CLI Interface ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: router.py <question> [--history] [--save <answer>]")
        sys.exit(1)

    question = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else None

    memory = load_memory()

    if action == "--history":
        # Return conversation history
        history = get_relevant_history(memory, question)
        print(json.dumps({"history": history}, indent=2))
        return

    if action == "--save":
        # Save Q&A to memory
        sources_json = sys.argv[3] if len(sys.argv) > 3 else "[]"
        try:
            sources = json.loads(sources_json)
        except Exception:
            sources = []
        add_to_memory(memory, question, sys.stdin.read() if sys.stdin.isatty() else "", sources)
        save_memory(memory)
        print("Saved to memory.")
        return

    # Normal routing: detect topic + find files
    topics = detect_topics(question)
    files = find_matching_files(question, topics)

    # Determine primary category
    primary_cat = topics[0][0] if topics else "general"
    primary_label = CATEGORY_LABELS.get(primary_cat, primary_cat)

    result = {
        "question": question,
        "topics_detected": [{"topic": t, "label": CATEGORY_LABELS.get(t, t), "score": s} for t, s in topics[:5]],
        "primary_category": primary_cat,
        "primary_label": primary_label,
        "matching_files": files[:8],
        "history": get_relevant_history(memory, question)[-3:],
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
