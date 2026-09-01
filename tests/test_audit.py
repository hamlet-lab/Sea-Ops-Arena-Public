from pathlib import Path

from sea_ops_arena.audit import audit_repository


def test_current_repository_passes_generic_public_audit():
    assert audit_repository(Path(".")) == ()


def test_audit_flags_environment_and_key_files(tmp_path):
    (tmp_path / ".env").write_text("EXAMPLE=value\n", encoding="utf-8")
    (tmp_path / "secret.key").write_text("not-a-real-key\n", encoding="utf-8")

    findings = audit_repository(tmp_path)
    codes = {finding.code for finding in findings}

    assert "environment-file" in codes
    assert "credential-file" in codes


def test_audit_flags_blocked_directory_path(tmp_path):
    directory = tmp_path / "internal"
    directory.mkdir()
    (directory / "note.txt").write_text("example\n", encoding="utf-8")

    findings = audit_repository(tmp_path)
    assert any(finding.code == "blocked-directory" for finding in findings)
