# Tavily (`tav`)

一般 Web（ニュース、製品比較、一次情報の裏取り）を取るときの手順。起動プレフィックスは [SKILL.md](SKILL.md) と同じ。以降は `tav search` / `tav extract` だけ書く。オプションは `--help` を正本にする。表は転記しない。

`TAVILY_API_KEY` が空なら `unavailable`。呼ばない。この CLI にあるのは `search` と `extract` だけ。`map` / `crawl` / `research` / `search-extract` / `map-extract` / `--topic` / `--detail` / `--json` は無い。

## 判断フロー

```text
1. Microsoft/Azure/.NET/M365 の公式ドキュメントか?
   Yes -> 系統を `ms` に切り替える（[SKILL.md](SKILL.md) の振り分け）
   外部ライブラリの現行 API か? -> `ctx`
   公開 GitHub の実コードか?    -> `grep`

2. 対象 URL が分かっているか?
   Yes -> tav extract <url> [url ...]
   No  -> tav search "<query>"

3. search の抜粋で足りるか?
   足りる -> そのまま使う
   全文が要る -> 結果ファイルの `URL:` 行を tav extract に渡す
```

迷ったら URL 起点は `extract`、キーワード起点は `search`。サイト全体の一覧やクロール、AI 調査レポートは無い。必要なページだけ `search` → `extract` で足す。

## クエリとドメイン

- `query` は日本語でよい。製品名・機能名・正式ドキュメント名は英語の方が強いことがある。弱ければ英語または日英混在で再実行する
- `--include-domain` は優先・許可の強い絞り込みであり、完全一致の隔離フィルタではない。広い host（`microsoft.com`）より狭い host（`techcommunity.microsoft.com`）を優先する。想定外 URL は結果を見て捨てる
- `--exclude-domain` も繰り返し指定できる

`extract` に `--query` を付けると、本文全体ではなく関連チャンクだけが返る。出力の `[...]` はチャンク境界であり、抽出失敗ではない。**全文が欲しいときは `--query` を付けない。**

## 結果の読み方

成功時 stdout は `index.md` のパスだけ。本文は出ない。

1. `index.md` を Read する（各行末に文字数がある）
2. タイトルから読むファイルを選ぶ。Read で足りるものだけ読む。他スキルには回さない
3. 各結果ファイルは先頭付近に `URL:` がある。search には `Score:` もある。深掘りするときはその URL を `tav extract` に渡す
4. 空結果は stderr `No results.`

同じクエリ/URL を再実行しても上書きされず、連番フォルダが増えるだけ。`--topic` の役割フォルダは無い。
