# CLAUDE.md

Graphica(https://github.com/STsuruga/Graphica)用プラグイン P-805 元素・同位体・物理定数テーブルのリポジトリ。

## 最初に読むもの
- 開発ハブ(Artifact): https://claude.ai/artifact/GZ3LTLJjbxj1LQsAhZFg2o
  Artifact ツールの action: "read" で読む。共通ルール・API 早見表・この項目の仕様と状態がある。
- 本体の CLAUDE.md「Plugin API」節と docs/plugin_development.md(本体リポジトリ)

## 作業の範囲
- このリポジトリ専用。ほかのプラグインのリポジトリと Graphica 本体は変更しない
  (本体への書き込みは docs/dev/PLUGIN_DEVELOPMENT_PROGRESS.md の表への1行だけ)。
- 新しいプラグインを始めるときは、新しいチャットでハブの引継ぎプロンプトから始める。

## このプラグイン
- 項目: P-805。使うフック: register_panel(選択中のデータセットを使わない参照ツールなので analyzer ではない)
- v1.2.0 の範囲(ユーザーと決めた内容): 元素(記号・番号・英語名・日本語名)、同位体(NIST の相対原子質量と
  天然存在比。元素名か核種表記 Fe-56 / 56Fe / 鉄56 で検索)、物理定数(scipy.constants の CODATA 値、日本語の呼び名)。
  空の検索語で一覧、元素のダブルクリックで同位体、Ctrl+C / 右クリックでタブ区切りコピー。
- 見送ったこと・次の版に回したこと: 周期表のボタン型画面、電子配置・電気陰性度などの追加物性。
- isotopes.py は scripts/generate_isotopes.py の生成物。手で編集せず、スクリプトを直して作り直す。
- 原子量の表(data.py)は手で持っている。NIST の標準原子量と全元素一致を確認済み。存在比で重み付けした質量との
  突き合わせがテストにある(Se と Pb は IUPAC の原子量改訂で NIST の代表組成と 0.01 以上ずれるので許容幅 0.02)。
- 版の番号: 1.0 / 1.1 は未リリースの内部版。最初の公開リリースが v1.2.0。

## コマンド
python -m venv .venv                  # 初回だけ。Python 3.11 以上
.venv\Scripts\activate               # macOS / Linux は source .venv/bin/activate
pip install "graphica-plot>=2.0,<3"   # 本体の未リリースの変更で試すときは pip install -e <PlotterApp>/Graphica_project
pip install -r requirements-dev.txt
pytest
graphica                               # 本体を起動(zip は 編集 ▸ 環境設定 ▸ プラグイン から入れる)
python scripts/build_zip.py --all      # dist/element_constants-<version>.zip
python scripts/generate_isotopes.py    # NIST から isotopes.py を作り直す

## ルール
- Graphica 本体のコードは変更しない。足りない拡張点は本体の Issue(ユーザーの了承を得て作成)とハブの note に記録する。
- 依存は本体同梱のパッケージのみ(PySide6 6.11 / matplotlib 3.11 / numpy / pandas / scipy / openpyxl / xlrd)。
- matplotlib の色は組で返ることがあるので、Qt に渡す前に matplotlib.colors.to_hex で #rrggbb にする。
- プラグイン内は相対 import。他プラグインは import できない。
- 受け取った Dataset は書き換えない。新しい Dataset は name / df / x_col_name / y_col_name 必須。
- 本体から import するのは graphica.plugin / graphica.plugin.testing だけ。本体の操作は窓口 ctx(PluginContext)で行う。
- リリースしたら plugin.json の version とタグを揃え、ハブの db(collection "plugins", doc_id "P-805")を更新する。

## 現状
- 2026-09-28: v1.2.0 を準備中(同位体・日本語名・一覧表示・コピーを追加、LICENSE / CLAUDE.md / CI を追加)。
