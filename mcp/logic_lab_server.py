from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


SERVER_NAME = "logic-lab"
DEFAULT_MAX_CHARS = 12_000
ABSOLUTE_MAX_CHARS = 20_000

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / ".agents" / "art_manifest.json"

mcp = FastMCP(SERVER_NAME)


class AccessError(ValueError):
    pass


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _entries() -> list[dict[str, Any]]:
    manifest = _load_manifest()
    entries = manifest.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("Manifest must contain an entries array")
    return entries


def _manifest_paths() -> set[str]:
    return {entry["path"] for entry in _entries() if isinstance(entry.get("path"), str)}


def _safe_repo_path(path: str) -> tuple[Path, str]:
    if not path or Path(path).is_absolute():
        raise AccessError("Path must be a relative repository path")

    resolved = (REPO_ROOT / path).resolve()
    try:
        rel_path = resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise AccessError("Path outside the repository is not allowed") from exc

    return resolved, rel_path


def _allowed_algorithm_path(path: str) -> tuple[Path, str]:
    resolved, rel_path = _safe_repo_path(path)
    manifest_paths = _manifest_paths()

    is_manifest_path = rel_path in manifest_paths
    is_python = resolved.suffix == ".py"
    is_readme = resolved.name == "README.md"

    if not is_manifest_path and not (is_python or is_readme):
        raise AccessError("Only manifest entries, .py files, and README.md files can be read")
    if not resolved.is_file():
        raise AccessError("Path does not point to a readable file")
    return resolved, rel_path


def _clamp_max_chars(max_chars: int | None) -> int:
    if max_chars is None:
        return DEFAULT_MAX_CHARS
    return max(1, min(int(max_chars), ABSOLUTE_MAX_CHARS))


def _search_text(entry: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("title", "category", "visual_use"):
        value = entry.get(key)
        if isinstance(value, str):
            values.append(value)
    for key in ("concepts", "good_for"):
        value = entry.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value)
    return " ".join(values).lower()


def _score_entry(entry: dict[str, Any], query: str) -> int:
    query = query.lower().strip()
    if not query:
        return 1

    haystack = _search_text(entry)
    score = 0
    if query in haystack:
        score += 8
    for token in query.split():
        if token in haystack:
            score += 2
        if token == str(entry.get("category", "")).lower():
            score += 3
        if token in [str(item).lower() for item in entry.get("concepts", [])]:
            score += 4
    return score


def _entry_for_path(path: str) -> dict[str, Any] | None:
    _, rel_path = _safe_repo_path(path)
    for entry in _entries():
        if entry.get("path") == rel_path:
            return entry
    return None


@mcp.tool()
def get_manifest() -> dict[str, Any]:
    """Return the Logic Lab art algorithm manifest."""
    return _load_manifest()


@mcp.tool()
def search_algorithms(query: str, category: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
    """Search manifest entries by title, category, concepts, visual_use, and good_for."""
    normalized_category = category.lower().strip() if category else None
    max_results = max(1, min(int(limit), 50))

    results: list[tuple[int, dict[str, Any]]] = []
    for entry in _entries():
        entry_category = str(entry.get("category", "")).lower()
        if normalized_category and entry_category != normalized_category:
            continue
        score = _score_entry(entry, query)
        if score > 0:
            results.append((score, entry))

    results.sort(key=lambda item: (-item[0], item[1].get("path", "")))
    return [entry for _, entry in results[:max_results]]


@mcp.tool()
def get_algorithm(path: str, max_chars: int = DEFAULT_MAX_CHARS) -> dict[str, Any]:
    """Return read-only source text for a safe repository .py or README.md path."""
    resolved, rel_path = _allowed_algorithm_path(path)
    limit = _clamp_max_chars(max_chars)
    text = resolved.read_text(encoding="utf-8", errors="replace")

    truncated = len(text) > limit
    if truncated:
        text = text[:limit]

    return {
        "path": rel_path,
        "content": text,
        "truncated": truncated,
        "notice": (
            f"Content truncated to {limit} characters. Increase max_chars up to {ABSOLUTE_MAX_CHARS}."
            if truncated
            else None
        ),
    }


@mcp.tool()
def get_algorithm_summary(path: str) -> dict[str, Any]:
    """Return a short summary from the manifest entry and nearby README when available."""
    resolved, rel_path = _allowed_algorithm_path(path)
    entry = _entry_for_path(rel_path)

    readme_path = resolved if resolved.name == "README.md" else resolved.parent / "README.md"
    readme_excerpt = None
    if readme_path.exists() and readme_path.is_file():
        lines = [
            line.strip()
            for line in readme_path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.strip().startswith("```")
        ]
        readme_excerpt = "\n".join(lines[:6])[:1200] if lines else None

    if entry:
        summary = {
            "path": rel_path,
            "title": entry.get("title"),
            "category": entry.get("category"),
            "concepts": entry.get("concepts", []),
            "visual_use": entry.get("visual_use"),
            "good_for": entry.get("good_for", []),
            "complexity": entry.get("complexity"),
            "dependencies": entry.get("dependencies", []),
            "readme_excerpt": readme_excerpt,
        }
    else:
        summary = {
            "path": rel_path,
            "title": resolved.parent.name.replace("_", " ").title(),
            "category": rel_path.split("/", 1)[0],
            "readme_excerpt": readme_excerpt,
        }
    return summary


if __name__ == "__main__":
    mcp.run()
