"""Tests for Logic Lab MCP path handling."""

# ruff: noqa: I001

import pytest
from logic_lab.mcp import logic_lab_server as server


def setup_function() -> None:
    server._load_manifest.cache_clear()


def test_search_result_path_can_be_read() -> None:
    result = server.search_algorithms("wave", limit=1)[0]

    algorithm = server.get_algorithm(result["path"], max_chars=120)

    assert algorithm["path"] == result["path"]
    assert "content" in algorithm
    assert algorithm["content"]


def test_source_prefixed_path_normalizes_to_manifest_path() -> None:
    path = "physics/additive_wave/additive_wave.py"

    algorithm = server.get_algorithm(f"src/logic_lab/{path}", max_chars=80)
    summary = server.get_algorithm_summary(f"src/logic_lab/{path}")

    assert algorithm["path"] == path
    assert summary["path"] == path
    assert summary["title"] == "Additive wave"


def test_rejects_paths_outside_repository() -> None:
    with pytest.raises(server.AccessError):
        server.get_algorithm("../outside.py")
