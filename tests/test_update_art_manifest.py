"""Tests for manifest updater source-root discovery."""

import importlib.util
from pathlib import Path


def load_update_module():
    module_path = Path(__file__).resolve().parents[1] / ".agents" / "update_art_manifest.py"
    spec = importlib.util.spec_from_file_location("update_art_manifest_test", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_update_manifest_discovers_src_logic_lab_paths(tmp_path, monkeypatch) -> None:
    module = load_update_module()
    source_root = tmp_path / "src" / "logic_lab"
    sketch_dir = source_root / "physics" / "new_wave"
    sketch_dir.mkdir(parents=True)
    (sketch_dir / "README.md").write_text("# New Wave\n", encoding="utf-8")
    (sketch_dir / "new_wave.py").write_text("import py5\n", encoding="utf-8")

    manifest_path = tmp_path / ".agents" / "art_manifest.json"
    baseline_path = tmp_path / ".agents" / "art_manifest_baseline.json"
    manifest_path.parent.mkdir()
    manifest_path.write_text('{"schema_version": 1, "entries": []}\n', encoding="utf-8")
    baseline_path.write_text('{"paths": []}\n', encoding="utf-8")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "SOURCE_ROOT", source_root)
    monkeypatch.setattr(module, "MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(module, "BASELINE_PATH", baseline_path)

    files = module.discover_algorithm_files()
    result = module.update_manifest(write=True)
    manifest = module.load_manifest()

    assert [path.relative_to(source_root).as_posix() for path in files] == [
        "physics/new_wave/new_wave.py"
    ]
    assert result == 0
    assert manifest["entries"][0]["path"] == "physics/new_wave/new_wave.py"
    assert manifest["entries"][0]["category"] == "physics"
