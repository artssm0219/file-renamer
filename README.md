# file-renamer

指定したフォルダ内のファイル名を、連番付きの分かりやすい名前に整理するCLIツールです。

例として、PDFファイルを `lecture_01.pdf`, `lecture_02.pdf` のような名前にまとめて変更できます。

このREADMEは、実装方針と使い方を整理したものです。

## 実装方針

- Pythonで実装する
- 標準ライブラリを優先して使う
- CLI引数の解析には `argparse` を使う
- ファイルやパスの操作には `pathlib` を使う
- 対象フォルダ直下のファイルだけを対象にする
- 対象ファイルはファイル名の昇順で並べる
- デフォルトは dry-run とし、実際のリネームは行わない
- `--apply` が指定された場合だけファイル名を変更する
- リネーム前に変更先の名前が衝突しないか確認する
- 既存ファイルを上書きしない
- エラー時は初心者にも分かる日本語メッセージを表示する
- 実装後は `pytest` で動作確認する

## ファイル構成

```text
file-renamer/
├── README.md
├── AGENTS.md
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

- `src/rename_files.py`: CLI本体。引数解析、対象ファイル取得、リネーム計画作成、衝突チェック、実行処理を含める
- `examples/input/`: 動作確認用のサンプルファイルを置く
- `tests/test_rename_files.py`: dry-run、実リネーム、衝突エラー、対象拡張子の絞り込みなどのテストを書く

将来的に処理が大きくなった場合は、CLI部分とリネームロジックを別ファイルに分けることも検討します。

## 使い方

デフォルトでは dry-run として、変更予定だけを表示します。

```bash
python3 src/rename_files.py --input 対象フォルダ --ext 対象拡張子 --prefix 接頭辞
```

実際にファイル名を変更する場合は、`--apply` を付けます。

```bash
python3 src/rename_files.py --input 対象フォルダ --ext 対象拡張子 --prefix 接頭辞 --apply
```

## CLIオプション

| オプション | 必須 | 説明 | 例 |
| --- | --- | --- | --- |
| `--input` | 必須 | 対象フォルダを指定する | `--input ./docs` |
| `--ext` | 必須 | 対象拡張子を指定する | `--ext .pdf` |
| `--prefix` | 必須 | 出力される名前の接頭辞を指定する | `--prefix lecture` |
| `--apply` | 任意 | 実際にファイル名を変更する | `--apply` |

## 入力例

対象フォルダ `docs/` に以下のファイルがあるとします。

```text
docs/
├── intro.pdf
├── chapter-final.pdf
├── memo.txt
└── sample.pdf
```

次のコマンドを実行します。

```bash
python3 src/rename_files.py --input ./docs --ext .pdf --prefix lecture
```

## 出力例

デフォルトでは dry-run のため、実際には変更せず、変更予定だけ表示します。

```text
[dry-run] 以下のようにリネームします:
chapter-final.pdf -> lecture_01.pdf
intro.pdf -> lecture_02.pdf
sample.pdf -> lecture_03.pdf

実際に変更するには --apply を付けて実行してください。
```

実際に変更する場合:

```bash
python3 src/rename_files.py --input ./docs --ext .pdf --prefix lecture --apply
```

出力例:

```text
リネームを実行しました:
chapter-final.pdf -> lecture_01.pdf
intro.pdf -> lecture_02.pdf
sample.pdf -> lecture_03.pdf
```

実行後のフォルダ:

```text
docs/
├── lecture_01.pdf
├── lecture_02.pdf
├── lecture_03.pdf
└── memo.txt
```

## ファイル名ルール

- ファイル名は `prefix_01.pdf`, `prefix_02.pdf` のようにする
- 連番は `01` から始める
- 桁数は最低2桁にする
- 対象ファイル数が100件以上ある場合は、必要に応じて桁数を増やす
  - 例: 100件ある場合は `lecture_001.pdf`, `lecture_002.pdf` のようにする
- 拡張子は `--ext` で指定したものを使う
- 対象ファイルの並び順は、元のファイル名の昇順にする

## エラー例

変更先と同じ名前のファイルが既にある場合は、上書きせずエラーにします。

例:

```text
docs/
├── intro.pdf
├── sample.pdf
└── lecture_01.pdf
```

この状態で次を実行した場合:

```bash
python3 src/rename_files.py --input ./docs --ext .pdf --prefix lecture --apply
```

出力例:

```text
エラー: 変更先のファイルが既に存在します: lecture_01.pdf
既存ファイルを上書きしないため、処理を中止しました。
```

dry-runの場合も、衝突が見つかったら同じようにエラーとして表示します。

## サンプルで試す

`examples/input/` にサンプルファイルがあります。まずは dry-run で変更予定だけを確認します。

```bash
python3 src/rename_files.py --input examples/input --ext .pdf --prefix lecture
```

実際にリネームする場合は `--apply` を付けます。

```bash
python3 src/rename_files.py --input examples/input --ext .pdf --prefix lecture --apply
```

## テスト方法

`pytest` が入っている環境では、次のコマンドでテストできます。

```bash
python3 -m pytest
```

プロジェクト内の仮想環境を使う場合:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pytest
.venv/bin/python -m pytest
```

## 注意点

- デフォルトでは dry-run なので、ファイル名は変更されません
- 実際に変更するには必ず `--apply` を指定します
- 既存ファイルは上書きしません
- 対象になるのは、`--ext` で指定した拡張子のファイルだけです
- `--ext` は `.pdf` のようにドット付きで指定します
- サブフォルダ内のファイルは対象外にします
- 実行前に dry-run の結果を確認してください
- 大事なファイルを扱う場合は、事前にバックアップを取ってください
