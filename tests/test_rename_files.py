from pathlib import Path

import pytest

from src.rename_files import (
    RenameFilesError,
    RenamePlan,
    apply_rename_plan,
    create_rename_plan,
    main,
)


def write_sample(path: Path) -> None:
    path.write_text("sample\n", encoding="utf-8")


def test_dry_run_outputs_plan_without_renaming(tmp_path, capsys):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    write_sample(input_dir / "intro.pdf")
    write_sample(input_dir / "chapter-final.pdf")
    write_sample(input_dir / "memo.txt")
    write_sample(input_dir / "sample.pdf")

    exit_code = main(
        [
            "--input",
            str(input_dir),
            "--ext",
            ".pdf",
            "--prefix",
            "lecture",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[dry-run] 以下のようにリネームします:" in captured.out
    assert "chapter-final.pdf -> lecture_01.pdf" in captured.out
    assert "intro.pdf -> lecture_02.pdf" in captured.out
    assert "sample.pdf -> lecture_03.pdf" in captured.out
    assert (input_dir / "chapter-final.pdf").exists()
    assert not (input_dir / "lecture_01.pdf").exists()


def test_apply_renames_only_matching_extension(tmp_path, capsys):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    write_sample(input_dir / "b.pdf")
    write_sample(input_dir / "a.pdf")
    write_sample(input_dir / "memo.txt")

    exit_code = main(
        [
            "--input",
            str(input_dir),
            "--ext",
            ".pdf",
            "--prefix",
            "lecture",
            "--apply",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "リネームを実行しました:" in captured.out
    assert "a.pdf -> lecture_01.pdf" in captured.out
    assert "b.pdf -> lecture_02.pdf" in captured.out
    assert (input_dir / "lecture_01.pdf").exists()
    assert (input_dir / "lecture_02.pdf").exists()
    assert (input_dir / "memo.txt").exists()
    assert not (input_dir / "a.pdf").exists()
    assert not (input_dir / "b.pdf").exists()


def test_existing_target_file_is_error_even_in_dry_run(tmp_path, capsys):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    write_sample(input_dir / "a.pdf")
    write_sample(input_dir / "lecture_01.pdf")

    exit_code = main(
        [
            "--input",
            str(input_dir),
            "--ext",
            ".pdf",
            "--prefix",
            "lecture",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "エラー: 変更先のファイルが既に存在します: lecture_01.pdf" in captured.err
    assert "既存ファイルを上書きしないため、処理を中止しました。" in captured.err
    assert (input_dir / "a.pdf").exists()
    assert (input_dir / "lecture_01.pdf").exists()


def test_no_target_files_is_error(tmp_path, capsys):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    write_sample(input_dir / "memo.txt")

    exit_code = main(
        [
            "--input",
            str(input_dir),
            "--ext",
            ".pdf",
            "--prefix",
            "lecture",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "エラー: 対象ファイルが見つかりません。" in captured.err


@pytest.mark.parametrize(
    "prefix",
    ["", "   ", "bad/name", "bad\\name", "..", "../bad", "bad..name"],
)
def test_invalid_prefix_is_error(tmp_path, capsys, prefix):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    write_sample(input_dir / "a.pdf")

    exit_code = main(
        [
            "--input",
            str(input_dir),
            "--ext",
            ".pdf",
            "--prefix",
            prefix,
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "エラー: --prefix" in captured.err
    assert (input_dir / "a.pdf").exists()


@pytest.mark.parametrize(
    "ext",
    ["", "   ", "pdf", ".", ".pdf/evil", ".pdf\\evil", ".pdf..bak"],
)
def test_invalid_ext_is_error(tmp_path, capsys, ext):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    write_sample(input_dir / "a.pdf")

    exit_code = main(
        [
            "--input",
            str(input_dir),
            "--ext",
            ext,
            "--prefix",
            "lecture",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "エラー: --ext" in captured.err
    assert (input_dir / "a.pdf").exists()


def test_missing_input_directory_is_error(tmp_path, capsys):
    input_dir = tmp_path / "missing"

    exit_code = main(
        [
            "--input",
            str(input_dir),
            "--ext",
            ".pdf",
            "--prefix",
            "lecture",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "エラー: 対象フォルダが存在しません:" in captured.err


def test_input_file_is_error(tmp_path, capsys):
    input_file = tmp_path / "input.pdf"
    write_sample(input_file)

    exit_code = main(
        [
            "--input",
            str(input_file),
            "--ext",
            ".pdf",
            "--prefix",
            "lecture",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "エラー: --input にはフォルダを指定してください:" in captured.err


def test_uppercase_extension_is_not_matched_by_lowercase_ext(tmp_path, capsys):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    write_sample(input_dir / "report.PDF")

    exit_code = main(
        [
            "--input",
            str(input_dir),
            "--ext",
            ".pdf",
            "--prefix",
            "lecture",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "エラー: 対象ファイルが見つかりません。" in captured.err
    assert (input_dir / "report.PDF").exists()


def test_apply_rechecks_existing_target_before_renaming(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    write_sample(input_dir / "a.pdf")
    plan = create_rename_plan(input_dir, ".pdf", "lecture")
    write_sample(input_dir / "lecture_01.pdf")

    with pytest.raises(RenameFilesError) as error:
        apply_rename_plan(plan)

    assert "エラー: 変更先のファイルが既に存在します: lecture_01.pdf" in str(
        error.value
    )
    assert (input_dir / "a.pdf").exists()
    assert (input_dir / "lecture_01.pdf").exists()


def test_apply_reports_rename_oserror(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    source = input_dir / "a.pdf"
    target = input_dir / "lecture_01.pdf"
    write_sample(source)
    plan = [RenamePlan(source=source, target=target)]

    def fail_rename(self, target_path):
        raise OSError("permission denied")

    monkeypatch.setattr(type(source), "rename", fail_rename)

    with pytest.raises(RenameFilesError) as error:
        apply_rename_plan(plan)

    message = str(error.value)
    assert "エラー: ファイル名の変更に失敗しました: a.pdf -> lecture_01.pdf" in message
    assert "原因: permission denied" in message


def test_number_width_expands_for_100_or_more_files(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    for index in range(100):
        write_sample(input_dir / f"file-{index:03d}.pdf")

    plan = create_rename_plan(input_dir, ".pdf", "lecture")

    assert plan[0].target.name == "lecture_001.pdf"
    assert plan[-1].target.name == "lecture_100.pdf"
