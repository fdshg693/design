---
name: web-lookup
description: Looks up current web information via a bundled CLI covering grep.app (real GitHub code), Microsoft Learn (official Microsoft/Azure docs), Tavily (general web), and Context7 (library APIs). Use when you need Microsoft/Azure official docs, current library/framework API references, real-world public GitHub code examples, or general web research, and the plugin must run without installing tools/ CLIs.

# 前提: 起動は `uv run --project ${CLAUDE_SKILL_DIR} web-lookup`。`uv` 必須。
# グローバル `uv tool install` はしない。`tools/` の CLI は使わない。
# TAVILY_API_KEY / CONTEXT7_API_KEY が空なら該当バックエンドは unavailable。
# WEB_LOOKUP_OUTPUT_DIR は未設定時 temp/web-lookup。
# 同梱ファイル: ms.md / ctx.md / grep.md / tav.md（各系統の判断フロー）
# 設計意図・セットアップは同階層の README.md（人間のメンテナ向け）
allowed-tools: Bash(uv run *)
meta:
  tag: []
  requires_repo_tools: none
  requires_env: TAVILY_API_KEY, CONTEXT7_API_KEY, WEB_LOOKUP_OUTPUT_DIR
  dependencies: fastmcp, tavily-python, requests, python-dotenv
  requires_install: uv
  requires_hooks: none
  requires_skills: none
  status: experimental
  description: no description
  version: 1.2.0
---

## いま使えるバックエンド

設定（`.env` / 環境変数）だけの判定。ネットワークは叩かない。`unavailable` の系統は呼ばない。

```!
uv run --project ${CLAUDE_SKILL_DIR} web-lookup available
```

## 起動

完全修飾で呼ぶ。相対パスや PATH 上の `web-lookup` は使わない。以降の `ms fetch` などのサブコマンドは、次のプレフィックスに続ける。

```text
uv run --project ${CLAUDE_SKILL_DIR} web-lookup <subcommand>
```

オプションと終了コードは同じプレフィックスの `--help`（各サブコマンドの `--help`）を正本にする。表は転記しない。

## 振り分け

1. Microsoft/Azure/.NET/M365 の公式ドキュメント → `ms`。使うなら [ms.md](ms.md) を読み、その手順に従う
2. 外部ライブラリ / フレームワークの現行 API・セットアップ・移行 → `ctx`。使うなら [ctx.md](ctx.md) を読み、その手順に従う
3. 公開 GitHub の実コード（ドキュメントの例ではなく、実際の書き方） → `grep`。使うなら [grep.md](grep.md) を読み、その手順に従う
4. それ以外の Web（ニュース、製品比較、一次情報の裏取り） → `tav`。使うなら [tav.md](tav.md) を読み、その手順に従う

使いたい系統が `unavailable` なら呼ばない。`tav` が available なら Web で代替してよいか判断する。grep / ms はキー不要で通常 available。

## 結果の読み方

`grep` / `ms` / `tav` の成功時 stdout は `index.md` のパスだけ。まず `index.md` を Read し、必要なファイルだけ読む。大きいファイルも他スキルに回さない。Read で足りるものだけ読む。空結果は stderr `No results.`。

`ctx` と `available` は stdout に本文を出す。
