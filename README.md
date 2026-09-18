# graphica-plugin-element-constants

[Graphica](https://github.com/STsuruga/Graphica) 用のプラグイン。
**元素周期表(118元素)と物理定数**を検索できる常設パネルを追加します。

バックログ上の項目番号は **P-805**。データセットを一切必要としない参照ツールなので、
`register_analyzer`(Dataset必須)ではなく `register_panel` で常設ドックパネルとして
提供します。

## できること

- **元素の検索**: 元素記号(`Fe`)・原子番号(`26`)・英名(`Iron`、部分一致可)のいずれでも引ける
- **物理定数の検索**: 日本語のよくある呼び名(`光速`、`プランク定数`)でも、
  英語名の部分一致(`electron mass`)でも引ける

物理定数は `scipy.constants.physical_constants` をそのまま使っています(手入力による
転記ミスが起きない)。元素データは、依存関係として承認できる既存パッケージに
118元素を網羅したものが無かったため、このリポジトリに同梱しています。

## インストール(利用者向け)

1. [Releases](https://github.com/STsuruga/graphica-plugin-element-constants/releases) から
   `element_constants-<version>.zip` をダウンロード
2. Graphica を起動し、**環境設定 → 「プラグインをインストール...」** から
   その zip を選択
3. Graphica を再起動すると、右側に「元素・物理定数テーブル」パネルが出ます

> プラグインは `%LOCALAPPDATA%\Graphica\plugins` に展開されます。
> このフォルダは Graphica を `Program Files` 配下にインストールしていても
> 常に書き込み可能です。

## 開発環境の準備

このリポジトリ単体でもデータ検索のテストは動きますが、**register() の配線や
本番と同じ読み込み経路のテストには Graphica 本体が必要**です。

```bash
# 1. Graphica 本体を editable install する
#    (PyPI には無いので、ソースを取得してローカルパスを指定する)
git clone https://github.com/STsuruga/Graphica.git
pip install -e Graphica/Graphica_project

# 2. テスト用の依存を入れる
pip install -r requirements-dev.txt

# 3. テスト実行
pytest
```

本体が入っていない場合、本体を必要とするテストは理由付きで skip されます
(`tests/conftest.py` の `requires_graphica` を参照)。

## 配布用 zip のビルド

```bash
python scripts/build_zip.py --all      # dist/element_constants-1.0.zip
```

`dist/` は `.gitignore` 済みです(zip はビルド成果物なので、リポジトリには
コミットせず Releases に添付します)。

出力する zip は、本体の `core/plugin_install.py` の `_find_plugin_root()` が
受け付ける「単一のトップレベルフォルダの中に `__init__.py` がある」形です。
`__pycache__` と `.pyc` は除外されます。

## このリポジトリの構成

```
element_constants/        ← プラグイン本体(この *フォルダ名* がプラグイン名になる)
  __init__.py             ← register(api) のエントリポイント
  plugin.json             ← マニフェスト(name / version / api_version)
  data.py                 ← 元素・定数データと検索ロジック(GUI非依存)
  panel.py                ← 検索パネルのウィジェット
tests/                    ← pytest
scripts/build_zip.py      ← 配布用zipのビルド
```

## 他のプラグインから再利用する場合

`data.py` は GUI にも Graphica 本体にも依存しない素の Python モジュールなので、
他のプラグインからも再利用できます(バックログ上「他パックの共通基盤」という
位置づけ)。ただし **プラグインは互いを import できません** — Graphica の
`PluginManager` は各プラグインを `graphica_plugin_<name>` という動的モジュール名で
読み込むため、`element_constants.data` という絶対パスは本番環境では解決しません。
再利用したい場合は `data.py` をコピーして同梱してください。

## API バージョン

`plugin.json` の `api_version` は **`2.0`** です。Graphica 本体の
`core/plugin_manifest.py` の `PLUGIN_API_VERSION` と一致しないと、プラグインの
コードは読み込まれません(本体側が破壊的変更を入れるとこの値が上がります)。

## ライセンス

Graphica 本体に準じます。
