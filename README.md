# graphica-plugin-element-constants

[Graphica](https://github.com/STsuruga/Graphica) 用のプラグイン。
**元素周期表(118 元素)・同位体・物理定数**を検索できる常設パネルを追加します(Graphica のプラグイン項目 P-805)。

## できること

パネル上部で「元素」「同位体」「物理定数」を切り替えて検索します。検索語が空のときは一覧を表示します。

- **元素**: 元素記号(`Fe`)・原子番号(`26`)・英語名(`Iron`、部分一致可)・日本語名(`鉄`、部分一致可)で検索。
  原子番号・元素記号・英語名・日本語名・原子量を表示します。行をダブルクリックすると、その元素の同位体を表示します。
- **同位体**: 元素(`Fe`、`鉄`)ならその元素の同位体すべて、核種(`Fe-56`、`56Fe`、`鉄56`)ならその1件。
  相対原子質量と天然存在比を、NIST の表記のまま(括弧内は末尾の桁の不確かさ)表示します。
  天然に存在しない元素(Tc、Pm、Po 以降の多く)は、代表的な長寿命核種を存在比「—」で表示します。
- **物理定数**: 日本語の呼び名(`光速`、`ボーア`、部分一致可)か英語名(`electron mass`)で、CODATA 値の全件から検索。
  検索語が空のときは、よく使う 23 個の定数を表示します。

表のセルを選んで **Ctrl+C**(または右クリック ▸ コピー)すると、タブ区切りのテキストとしてコピーでき、Excel などにそのまま貼り付けられます。

### データの出典

- 物理定数: `scipy.constants.physical_constants`(CODATA 推奨値)をそのまま使っています。
- 同位体: NIST [Atomic Weights and Isotopic Compositions](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl)
  から `scripts/generate_isotopes.py` で生成しています。
- 原子量: IUPAC 標準原子量(2021)の略値。安定同位体を持たない元素は最も安定な同位体の質量数です。
  NIST の標準原子量と全元素で突き合わせ、同位体の存在比で重み付けした質量とも一致することをテストで確かめています。

## インストール(利用者向け)

1. [Releases](https://github.com/STsuruga/graphica-plugin-element-constants/releases) から
   `element_constants-<version>.zip` をダウンロード
2. Graphica(v2.0 以降)を起動し、**編集 ▸ 環境設定 ▸「プラグイン」タブ ▸ プラグインをインストール...** から
   その zip を選択
3. Graphica を再起動し、「プラグイン」メニューから「元素・物理定数テーブル」パネルを表示

> プラグインは `%LOCALAPPDATA%\Graphica\plugins` に展開されます。
> Graphica を `Program Files` 配下にインストールしていても、このフォルダは常に書き込めます。

## 開発環境の準備

Python 3.11 以上で、リポジトリごとの仮想環境を作ります。

```bash
python -m venv .venv
.venv\Scripts\activate                 # macOS / Linux は source .venv/bin/activate
pip install "graphica-plot>=2.0,<3"     # PyPI の Graphica(プラグイン API 2.x)
pip install -r requirements-dev.txt
pytest
```

Graphica 本体が入っていない場合、本体を必要とするテストは理由付きで skip されます
(`tests/conftest.py` の `requires_graphica`)。`graphica` コマンドで本体を起動できます。

## 配布用 zip のビルド

```bash
python scripts/build_zip.py --all      # dist/element_constants-<version>.zip
```

zip はリポジトリにコミットせず、GitHub Releases に添付します。中身は Graphica のインストーラが受け付ける
「単一のトップレベルフォルダ(`element_constants/`)」の形で、`__pycache__` と `.pyc` は含みません。

## このリポジトリの構成

```
element_constants/        ← プラグイン本体(このフォルダ名がインストール先のフォルダ名になる)
  __init__.py             ← register(api)
  plugin.json             ← マニフェスト(name / version / api_version)
  data.py                 ← 元素・同位体・定数の検索(GUI・本体に依存しない)
  isotopes.py             ← 同位体データ(scripts/generate_isotopes.py が生成)
  panel.py                ← 検索パネルのウィジェット
tests/                    ← pytest
scripts/build_zip.py      ← 配布用 zip のビルド
scripts/generate_isotopes.py ← NIST のデータから isotopes.py を作り直す
```

## 他のプラグインから使う場合

`data.py` と `isotopes.py` は GUI にも Graphica 本体にも依存しない素の Python モジュールです。
ただし Graphica のプラグインは互いを import できない(各プラグインは `graphica_plugin_<フォルダ名>` という
動的なモジュール名で読み込まれる)ので、使いたいプラグインにこの2ファイルをコピーして同梱してください。

## ライセンス

MIT([LICENSE](LICENSE))。同位体データの出典である NIST のデータは米国政府の著作物です。
