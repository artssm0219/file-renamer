from pathlib import Path

from src.rename_files import create_rename_plan, main


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


def test_number_width_expands_for_100_or_more_files(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    for index in range(100):
        write_sample(input_dir / f"file-{index:03d}.pdf")

    plan = create_rename_plan(input_dir, ".pdf", "lecture")

    assert plan[0].target.name == "lecture_001.pdf"
    assert plan[-1].target.name == "lecture_100.pdf"
