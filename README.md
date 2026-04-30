# file-renamer

指定フォルダ内のファイル名を、連番付きの分かりやすい形式に整理するPython CLIツールです。

ファイル名変更は誤操作の影響が大きいため、デフォルトではdry-runで変更予定だけを表示し、`--apply` を指定した場合のみ実際にリネームする安全設計にしています。

## 概要

`file-renamer` は、指定したフォルダ内のファイル名を連番付きの分かりやすい名前に整理するCLIツールです。

たとえば、フォルダ内のPDFファイルを `lecture_01.pdf`, `lecture_02.pdf`, `lecture_03.pdf` のような名前にまとめて変更できます。

Python 3.10以上を想定しています。本体はPython標準ライブラリのみで動作します。

## 特徴

- `--input` で対象フォルダを指定できる
- `--ext` で対象拡張子を指定できる
- `--prefix` で出力ファイル名の接頭辞を指定できる
- デフォルトは dry-run で、変更予定だけを表示する
- `--apply` を付けた場合だけ実際にリネームする
- 既存ファイルを上書きしない
- サブフォルダ内のファイルは対象外にする
- エラー時は日本語メッセージを表示する

## Quick Start

まずはサンプルファイルを `/tmp` にコピーして試します。`examples/input/` に直接 `--apply` するとサンプルファイル名が変わるため、コピー先で試すのがおすすめです。

```bash
cp -R examples/input /tmp/file-renamer-demo
```

dry-runで変更予定を確認します。

```bash
python3 src/rename_files.py --input /tmp/file-renamer-demo --ext .pdf --prefix lecture
```

出力例:

```text
[dry-run] 以下のようにリネームします:
chapter-final.pdf -> lecture_01.pdf
intro.pdf -> lecture_02.pdf
sample.pdf -> lecture_03.pdf

実際に変更するには --apply を付けて実行してください。
```

内容を確認して問題なければ、`--apply` を付けて実行します。

```bash
python3 src/rename_files.py --input /tmp/file-renamer-demo --ext .pdf --prefix lecture --apply
```

`examples/input/` の `.pdf` ファイルは動作確認用のダミーファイルです。実際のPDF文書ではありません。

## 使い方

基本形:

```bash
python3 src/rename_files.py --input 対象フォルダ --ext 対象拡張子 --prefix 接頭辞
```

実際にファイル名を変更する場合:

```bash
python3 src/rename_files.py --input 対象フォルダ --ext 対象拡張子 --prefix 接頭辞 --apply
```

例:

```bash
python3 src/rename_files.py --input ./docs --ext .pdf --prefix lecture
```

対象フォルダに以下のファイルがある場合:

```text
docs/
├── intro.pdf
├── chapter-final.pdf
├── memo.txt
└── sample.pdf
```

dry-runでは、次のように変更予定だけを表示します。

```text
[dry-run] 以下のようにリネームします:
chapter-final.pdf -> lecture_01.pdf
intro.pdf -> lecture_02.pdf
sample.pdf -> lecture_03.pdf

実際に変更するには --apply を付けて実行してください。
```

`--apply` を付けて実行すると、対象フォルダは次のようになります。

```text
docs/
├── lecture_01.pdf
├── lecture_02.pdf
├── lecture_03.pdf
└── memo.txt
```

## オプション

| オプション | 必須 | 説明 | 例 |
| --- | --- | --- | --- |
| `--input` | 必須 | 対象フォルダを指定する | `--input ./docs` |
| `--ext` | 必須 | 対象拡張子を指定する | `--ext .pdf` |
| `--prefix` | 必須 | 出力される名前の接頭辞を指定する | `--prefix lecture` |
| `--apply` | 任意 | 実際にファイル名を変更する | `--apply` |

`--prefix` には、空文字、空白のみ、`/`、`\`、`..` を含む値は使えません。

`--ext` には、空文字、空白のみ、`.` だけの値、`/`、`\`、`..` を含む値は使えません。必ず `.pdf` のようにドット付きで指定します。

## 安全設計

- デフォルトでは dry-run として動作し、実際のリネームは行わない
- `--apply` が指定された場合だけファイル名を変更する
- リネーム前に変更先のファイルが既に存在しないか確認する
- `--apply` 実行直前にも、変更先のファイルが既に存在しないか再確認する
- 既存ファイルを上書きしない
- `--prefix` と `--ext` にパス区切りや `..` を含む値を指定できない
- 対象ファイルは元のファイル名の昇順で処理する

変更先と同じ名前のファイルが既にある場合は、上書きせずエラーにします。

```text
エラー: 変更先のファイルが既に存在します: lecture_01.pdf
既存ファイルを上書きしないため、処理を中止しました。
```

## 制限事項

- ロールバック機能はありません
- サブフォルダ内のファイルは対象外です
- 拡張子は大文字小文字を区別します
  - 例: `--ext .pdf` を指定した場合、`.PDF` のファイルは対象外です
- `--apply` の途中でエラーが起きた場合、一部のファイルだけ変更済みになる可能性があります
- 実行前に dry-run の結果を確認することを推奨します
- 大事なファイルを扱う場合は、事前にバックアップを取ってください

## テスト方法

テストには `pytest` を使います。`pytest` は開発・テスト用依存であり、ツール本体の実行には不要です。

プロジェクト内の仮想環境を使う例:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```

すでに `pytest` が入っている環境では、次のコマンドでも実行できます。

```bash
python3 -m pytest
```

## 開発メモ

ファイル構成:

```text
file-renamer/
├── README.md
├── AGENTS.md
├── requirements-dev.txt
├── src/
│   └── rename_files.py
├── examples/
│   └── input/
│       ├── chapter-final.pdf
│       ├── intro.pdf
│       ├── memo.txt
│       └── sample.pdf
└── tests/
    └── test_rename_files.py
```

- `src/rename_files.py`: CLI本体
- `tests/test_rename_files.py`: pytestによるテスト
- `examples/input/`: 動作確認用のダミーファイル
- `requirements-dev.txt`: 開発・テスト用依存

実装では、CLI引数の解析に `argparse`、ファイルやパスの操作に `pathlib` を使っています。外部サービスや有料APIは使っていません。
