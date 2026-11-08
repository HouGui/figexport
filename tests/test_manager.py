from pathlib import Path

import pytest

from figexport.config import ExportConfig
from figexport.errors import ConfigError
from figexport.export_manager import ExportManager


def manager(root, **settings):
    return ExportManager(ExportConfig({"export_format": "svg", **settings}, root))


def test_recursive_output_pruning_and_nested_directories(svg_file):
    root = svg_file.parent
    nested = root / "nested"
    nested.mkdir()
    (nested / "UPPER.SVG").write_bytes(svg_file.read_bytes())
    old = root / "_export/old"
    old.mkdir(parents=True)
    (old / "generated.svg").write_bytes(svg_file.read_bytes())
    report = manager(root).run()
    assert report.to_dict()["exported"] == 2
    assert (root / "_export/nested/UPPER.svg").exists()
    assert len(manager(root).plan()) == 2


def test_exclusions_cover_children(svg_file):
    root = svg_file.parent
    nested = root / "skip/sub"
    nested.mkdir(parents=True)
    (nested / "hidden.svg").write_bytes(svg_file.read_bytes())
    report = manager(root, excluded_paths=["skip"]).run()
    assert report.to_dict()["exported"] == 1


def test_discovery_ignores_unsupported_files_and_environment(svg_file):
    root = svg_file.parent
    (root / "notes.txt").write_text("ignored")
    (root / ".venv").mkdir()
    (root / ".venv/internal.svg").write_bytes(svg_file.read_bytes())
    assert len(manager(root).plan()) == 1
    with pytest.raises(ConfigError, match="Unsupported"):
        ExportManager(ExportConfig({}, root, root / "notes.txt")).plan()


def test_same_stem_collision_prevents_any_write(svg_file):
    root = svg_file.parent
    (root / "drawing.tex").write_text("source")
    with pytest.raises(ConfigError, match="collision"):
        manager(root, export_format="pdf").run()
    assert not (root / "_export").exists()


def test_source_overwrite_is_rejected(svg_file):
    original = svg_file.read_bytes()
    with pytest.raises(ConfigError, match="overwrite an input"):
        manager(svg_file.parent, export_dir=".").run()
    assert svg_file.read_bytes() == original


def test_overlap_mappings_deduplicate_sources(svg_file):
    mappings = [{"source": ".", "target": "."}, {"source": "drawing.svg", "target": "."}]
    assert len(manager(svg_file.parent, directory_mappings=mappings).plan()) == 1


def test_keep_going_and_fail_fast(svg_file):
    bad = svg_file.parent / "a-bad.svg"
    bad.write_text("broken")
    exporter = manager(svg_file.parent, export_format="png")
    report = exporter.run(keep_going=True)
    assert [result.status for result in report.results] == ["failed", "exported"]
    assert report.failed == 1
    assert len(exporter.run().results) == 1


def test_invalid_drawio_reports_file_but_other_files_can_export(svg_file):
    (svg_file.parent / "bad.drawio").write_text("<broken")
    report = manager(svg_file.parent).run(keep_going=True)
    assert report.failed == 1
    assert report.to_dict()["exported"] == 1


def test_dry_run_and_constructor_have_no_side_effects(svg_file):
    exporter = manager(svg_file.parent)
    assert not (svg_file.parent / "_export").exists()
    assert exporter.run(dry_run=True).to_dict()["planned"] == 1
    assert not (svg_file.parent / "_export").exists()


def test_symlink_loop_and_file_are_not_followed(svg_file):
    root = svg_file.parent
    try:
        (root / "loop").symlink_to(root, target_is_directory=True)
        (root / "linked.svg").symlink_to(svg_file)
    except OSError:
        pytest.skip("Creating symlinks requires privileges on this platform.")
    assert len(manager(root).plan()) == 1


def test_no_overwrite_skips_entire_drawio_source(tmp_path):
    source = tmp_path / "diagram.drawio"
    source.write_text('<mxfile><diagram name="A"/><diagram name="B"/></mxfile>')
    output = tmp_path / "_export"
    output.mkdir()
    (output / "diagram_A.svg").write_text("existing")
    report = manager(tmp_path).run(overwrite=False)
    assert report.to_dict()["skipped"] == 1
    assert not (output / "diagram_B.svg").exists()


def test_separate_mapping_targets(svg_file):
    mappings = [{"source": "drawing.svg", "target": "A"}, {"source": "drawing.svg", "target": "B"}]
    report = manager(svg_file.parent, directory_mappings=mappings).run()
    assert report.to_dict()["exported"] == 2
    assert all(Path(result.outputs[0]).is_file() for result in report.results)


def test_new_backend_uses_shared_planning_and_execution(tmp_path):
    from figexport.export.fig_exporter import FigExporter
    from figexport.export.registry import EXPORTERS

    class TextExporter(FigExporter):
        def _convert(self, source, outputs):
            outputs[0].write_text(source.read_text().upper())

    source = tmp_path / "figure.custom"
    source.write_text("custom backend")
    factories = {**EXPORTERS, ".custom": lambda config: TextExporter(config.export_format)}
    exporter = ExportManager(ExportConfig({}, tmp_path), exporters=factories)
    assert exporter.run(dry_run=True).to_dict()["planned"] == 1
    assert not (tmp_path / "_export").exists()
    assert exporter.run().to_dict()["exported"] == 1
    assert (tmp_path / "_export/figure.pdf").read_text() == "CUSTOM BACKEND"
