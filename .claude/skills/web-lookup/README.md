# web-lookup スキルについて

grep.app / Microsoft Learn / Tavily / Context7 を、スキルに同梱した1つの CLI で使うためのスキル。このファイルは人間のメンテナ向け。Claude が実行時に読むのは [SKILL.md](SKILL.md) と、振り分け先の詳細ファイルであり、こちらは参照しない。

## 各ファイルの役割分担

`SKILL.md` 本体は起動・available・4系統の振り分けに集中するルーター。系統ごとの判断フローは同階層の詳細ファイルに分離する（[writing-skill](../../../meta/skills/writing-skill/README.md) と同じ「1スキル+ルーター」構成）。

| ファイル   | 役割                                                                        | 読まれるタイミング      |
| ---------- | --------------------------------------------------------------------------- | ----------------------- |
| `SKILL.md` | 起動プレフィックス、available、4系統の振り分け。手順の本体は持たない        | 常にスキル呼び出し時    |
| `ms.md`    | Microsoft Learn（`ms search` / `ms fetch`）の判断フローとクエリのコツ       | `ms` に振り分けたとき   |
| `ctx.md`   | Context7（`ctx library` / `ctx docs`）の判断フローと候補選択                | `ctx` に振り分けたとき  |
| `grep.md`  | grep.app（`grep search`）のリテラルクエリ制約と絞り込み                     | `grep` に振り分けたとき |
| `tav.md`   | Tavily（`tav search` / `tav extract`）の判断フローとドメイン/チャンクの扱い | `tav` に振り分けたとき  |

## なぜこのスキルがあるか

- [my-tools](../../../my-tools/) の `grep-app` / `ms-learn` / `tav-cli` / `use-context` は、それぞれ `tools/` の汎用 CLI を PATH に入れて使う。プラグインだけをよそへ移しても動かない
- こちらはスキルフォルダに最小 CLI を同梱し、`uv run --project` だけで依存を揃える。グローバル `uv tool install` はしない
- `tools/` の4パッケージはコピーも import もしない。持ち出し先に `tools/` が無い前提で、日常利用のサブコマンドだけを再実装している

## 前提条件

- `uv` がインストール済みであること。起動は常に `uv run --project <このスキルディレクトリ> web-lookup <subcommand>`
- 任意: スキル直下の `.env` に `TAVILY_API_KEY` / `CONTEXT7_API_KEY` / `WEB_LOOKUP_OUTPUT_DIR`。実 `.env` はコミットしない（[`.env.example`](.env.example) のみ）
- grep / ms は API キー不要。tav は `TAVILY_API_KEY`、ctx は `CONTEXT7_API_KEY` が空なら `available` が unavailable を出す

## 汎用 CLI との差分（意図的）

最小再実装なので、元の4 CLI と出力・耐障害性は一致しない。

- ctx は 202 ポーリング / 429 バックオフ / 301 追従を移植していない。失敗したらエラーをそのまま出す（元 `ctx7` より失敗しやすい）
- 出力は `WEB_LOOKUP_OUTPUT_DIR`（未設定時 `temp/web-lookup`）配下の連番フォルダ + `index.md` だけ。Q&A 分離も `--topic` 役割フォルダも `--json` も無い
- `code-search` / `map` / `crawl` / `research` / MCP の `tools`/`call` は作っていない

## 情報源と保守

- サブコマンド面と `available` の出力契約は CLI（`scripts/web_lookup.py` / `scripts/env_check.py`）が正本。オプション表は SKILL.md と各詳細ファイルに転記せず `--help` に任せる
- 4系統の振り分けは SKILL.md 固有。各系統の判断フローは同階層の詳細ファイル固有（元の [ms-learn](../../../my-tools/skills/ms-learn/SKILL.md) / [use-context](../../../my-tools/skills/use-context/SKILL.md) / [grep-app](../../../my-tools/skills/grep-app/SKILL.md) / [tav-cli](../../../my-tools/skills/tav-cli/SKILL.md) の運用方針を、この CLI のサブセットに合わせて移植したもの）
- CLI のサブコマンド名・`available` の列・env 名を変えたら SKILL.md の起動例と振り分け、および該当する詳細ファイルを突き合わせる
- 元 CLI にあるがこちらに無いもの（`code-search` / `map` / `crawl` / `research` / `tools` / `call` / `--topic` / `--detail` / `--json` / `--timeout` 等）を、詳細ファイルへ書き戻さないこと
