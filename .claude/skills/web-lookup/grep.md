# grep.app (`grep`)

公開 GitHub の実コード（ドキュメントの例ではなく、実際の書き方）を取るときの手順。起動プレフィックスは [SKILL.md](SKILL.md) と同じ。以降は `grep search` だけ書く。オプションは `--help` を正本にする。表は転記しない。

提供ツールは `search` だけ。`tools` / `call` / `--json` / `--timeout` は無い。タイムアウトは CLI 側で 45 秒固定。

## 判断フロー

```text
1. 探しているのは「本物のプロジェクトが実際にどう書いているか」か?
   Yes -> grep search "<リテラルなコードパターン>"
   No（概念・手順の説明） -> 系統を `ms` / `ctx` / `tav` に切り替える
     （[SKILL.md](SKILL.md) の振り分け）

2. 0件、または想定と違う言語/リポジトリばかりか?
   -> `--language` / `--repo` / `--path` で絞るか、query をより具体的なリテラルにする
     （キーワードのままになっていないか疑う）
```

結果は最大 10 件固定で、ページングは無い。1 クエリで全件網羅は期待しない。`--language`（複数回可）/ `--repo`（`vercel/` のような部分一致可）/ `--path`（`/route.ts` 等）を先に付ける。

## クエリ

`query` はキーワードや自然文ではなく、コードに現れるリテラル。

- ❌ `"how to use useState hook"` → ✅ `"useState("`
- ❌ `"React import"` → ✅ `"import React from"`
- 複数行を正規表現で探すときだけ `--use-regexp` を付け、先頭に `(?s)` を付ける
  （例: `"(?s)class .+ extends React.Component"`）
- `--match-case` / `--match-whole-words` は必要なときだけ

## 結果の読み方

成功時 stdout は `index.md` のパスだけ。本文は出ない。

1. `index.md` を Read する（各行末に文字数がある。タイトルは `<owner/repo> — <path>`）
2. タイトルから読むファイルを選ぶ。Read で足りるものだけ読む。他スキルには回さない
3. 空結果は stderr `No results.`

同じクエリを再実行しても上書きされず、連番フォルダが増えるだけ。

## 既知のリスク

- 初回はコールドスタートで遅い。504 やタイムアウトが出たら **1 回だけ** やり直す。`--timeout` は無いので伸ばせない。連続リトライはしない
- 429 のリトライ・バックオフも無い。連続で叩きすぎない
