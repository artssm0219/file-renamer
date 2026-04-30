from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class RenameFilesError(Exception):
    """ユーザーに表示するための分かりやすいエラー。"""


@dataclass(frozen=True)
class RenamePlan:
    source: Path
    target: Path


def normalize_ext(ext: str) -> str:
    if not ext or not ext.strip():
        raise RenameFilesError(
            "エラー: --ext には空でない拡張子を指定してください。"
        )
    if not ext.startswith(".") or ext == ".":
        raise RenameFilesError(
            "エラー: --ext は .pdf のようにドット付きで指定してください。"
        )
    if "/" in ext or "\\" in ext or ".." in ext:
        raise RenameFilesError(
            "エラー: --ext に /, \\, .. は使えません。"
        )
    return ext


def validate_prefix(prefix: str) -> str:
    if not prefix or not prefix.strip():
        raise RenameFilesError("エラー: --prefix には空でない文字列を指定してください。")
    if "/" in prefix or "\\" in prefix or ".." in prefix:
        raise RenameFilesError(
            "エラー: --prefix に /, \\, .. は使えません。"
        )
    return prefix


def validate_input_dir(input_dir: Path) -> Path:
    if not input_dir.exists():
        raise RenameFilesError(f"エラー: 対象フォルダが存在しません: {input_dir}")
    if not input_dir.is_dir():
        raise RenameFilesError(f"エラー: --input にはフォルダを指定してください: {input_dir}")
    return input_dir


def collect_target_files(input_dir: Path, ext: str) -> list[Path]:
    input_dir = validate_input_dir(input_dir)

    files = sorted(
        (
            path
            for path in input_dir.iterdir()
            if path.is_file() and path.suffix == ext
        ),
        key=lambda path: path.name,
    )
    if not files:
        raise RenameFilesError(
            "エラー: 対象ファイルが見つかりません。\n"
            f"フォルダ: {input_dir}, 拡張子: {ext}"
        )
    return files


def create_rename_plan(input_dir: Path, ext: str, prefix: str) -> list[RenamePlan]:
    ext = normalize_ext(ext)
    prefix = validate_prefix(prefix)
    files = collect_target_files(input_dir, ext)
    number_width = max(2, len(str(len(files))))

    plan = [
        RenamePlan(
            source=source,
            target=input_dir / f"{prefix}_{index:0{number_width}d}{ext}",
        )
        for index, source in enumerate(files, start=1)
    ]
    validate_no_collisions(plan)
    return plan


def validate_no_collisions(plan: Sequence[RenamePlan]) -> None:
    for item in plan:
        ensure_target_does_not_exist(item)


def ensure_target_does_not_exist(item: RenamePlan) -> None:
    if item.target.exists() and item.target != item.source:
        raise RenameFilesError(
            f"エラー: 変更先のファイルが既に存在します: {item.target.name}\n"
            "既存ファイルを上書きしないため、処理を中止しました。"
        )


def apply_rename_plan(plan: Sequence[RenamePlan]) -> None:
    validate_no_collisions(plan)
    for item in plan:
        if item.source == item.target:
            continue
        ensure_target_does_not_exist(item)
        try:
            item.source.rename(item.target)
        except OSError as error:
            raise RenameFilesError(
                f"エラー: ファイル名の変更に失敗しました: "
                f"{item.source.name} -> {item.target.name}\n"
                f"原因: {error}"
            ) from error


def print_plan(plan: Sequence[RenamePlan], should_apply: bool) -> None:
    if should_apply:
        print("リネームを実行しました:")
    else:
        print("[dry-run] 以下のようにリネームします:")

    for item in plan:
        print(f"{item.source.name} -> {item.target.name}")

    if not should_apply:
        print()
        print("実際に変更するには --apply を付けて実行してください。")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="指定したフォルダ内のファイル名を連番付きの名前に整理します。"
    )
    parser.add_argument("--input", required=True, help="対象フォルダ")
    parser.add_argument("--ext", required=True, help="対象拡張子。例: .pdf")
    parser.add_argument("--prefix", required=True, help="出力される名前の接頭辞")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="実際にファイル名を変更する。指定しない場合はdry-run",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        input_dir = Path(args.input)
        plan = create_rename_plan(input_dir, args.ext, args.prefix)
        if args.apply:
            apply_rename_plan(plan)
        print_plan(plan, args.apply)
        return 0
    except RenameFilesError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
