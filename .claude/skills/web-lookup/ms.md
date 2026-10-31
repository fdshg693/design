# Microsoft Learn (`ms`)

Microsoft/Azure/.NET/M365 の公式ドキュメントを取るときの手順。起動プレフィックスは [SKILL.md](SKILL.md) と同じ。以降は `ms search` / `ms fetch` だけ書く。オプションは `--help` を正本にする。表は転記しない。

この CLI にあるのは `search` と `fetch` だけ。`code-search` / `tools` / `call` / `--json` は無い。

## 判断フロー

```text
1. 対象ページの Learn URL が分かっている、または定番パスから推測できるか?
   Yes -> ms fetch <url>（search は飛ばす）
   No  -> 2 へ

2. ms search "<query>"
   抜粋で足りる -> そのまま使う
   途中で切れている / 表面的 / 手順の全体像が要る
     -> 結果ファイルの `URL:` 行を ms fetch に渡す

3. 公式ページでも足りず、非 Microsoft の二次情報や製品比較が要る
   -> 系統を `tav` に切り替える（[SKILL.md](SKILL.md) の振り分け）
```

`search` はチャンク化された抜粋（おおよそ最大 500 トークン/件、最大 10 件）しか返さない。抜粋そのものは浅いので、実質 **公式ページの URL を見つける** 用途が主になる。当たりがついている領域（既知の Learn セクション、前回の検索で得た URL、製品ドキュメントの定番パス）では search を省略して `fetch` する方が速い。

公式コードサンプルが欲しいときも `code-search` は無い。クエリに言語名・`sample` / `quickstart` を入れて `search` → 該当ページを `fetch` する。ドキュメントではなく公開リポジトリの実コードが欲しいなら系統を `grep` に切り替える。

## クエリ

- ❌ `"Azure Functions"` → ✅ `"Azure Functions Python v2 programming model timeout"`
  製品名だけでなく機能名・バージョン・症状まで入れる
- ARM/Bicep のリソース型名まで入れると逆効果。
  ❌ `"Bicep Microsoft.Search searchServices Microsoft.CognitiveServices accounts"`
  は API バージョン違いの自動生成スキーマ参照で埋まる。
  ✅ `"Azure AI Search Bicep quickstart"` のようにチュートリアル語彙で引く
- 日本語クエリも通るが、製品名・API 名・エラーメッセージは英語の方が一致しやすい。弱ければ英語で再実行する

## 結果の読み方

成功時 stdout は `index.md` のパスだけ。本文は出ない。

1. `index.md` を Read する（各行末に文字数がある）
2. タイトルから読むファイルを選ぶ。Read で足りるものだけ読む。他スキルには回さない
3. 各結果ファイルは先頭付近に `URL: <出典>` がある。深掘りするときはその URL を `ms fetch` に渡す
4. 空結果は stderr `No results.`

同じクエリ/URL を再実行しても上書きされず、連番フォルダが増えるだけ。前回結果を捨てて取り直す必要は無い。

`ms fetch` に Learn 以外の URL を渡すと、MCP エラーにはならず「The provided URL is not a valid Microsoft documentation webpage link.」のような説明文が本文として返ることがある。終了コードは成功扱いなので、本文を見て無効 URL だと判断する。
