# Context7 (`ctx`)

外部ライブラリ / フレームワークの現行 API・セットアップ・移行を取るときの手順。起動プレフィックスは [SKILL.md](SKILL.md) と同じ。以降は `ctx library` / `ctx docs` だけ書く。オプションは `--help` を正本にする。表は転記しない。

`CONTEXT7_API_KEY` が空なら `unavailable`。呼ばない。202 ポーリング / 429 バックオフ / 301 追従は無い。失敗したらエラーをそのまま出し、リトライループは組まない。`--fast` / `--json` / `--type` も無い。

## 判断フロー

```text
1. Microsoft/Azure/.NET/M365 の公式ドキュメントが対象か?
   Yes -> 系統を `ms` に切り替える（[SKILL.md](SKILL.md) の振り分け）
   No  -> 2 へ

2. 公式 context7-mcp / docs-researcher / /context7:docs が、同じセッションで同じ対象を既に処理済みか?
   Yes -> 再度呼ばない
   No  -> 3 へ

3. lockfile / manifest / import / エラーメッセージからパッケージ名と版を見る
   （package.json, pyproject.toml, uv.lock, go.mod, Cargo.toml, *.csproj 等）。
   ユーザーが版を書いていればそれを優先する。最新版を推測で前提にしない。

4. ライブラリ ID が既知か?
   Yes -> ctx docs <library-id> "<focused query>"
   No  -> ctx library <name> "<task>" で候補を選ぶ
           -> ctx docs <selected-id> "<focused query>"

5. query は1論点。複数論点は同じ ID で `ctx docs` を呼び分ける。
```

バージョンが分からないまま「最新」を前提にしない。取得結果に含まれる版を回答に明示する。

## 候補の選び方

`ctx library <name> "<task>"` の task には、ライブラリ名、やりたい操作、ランタイム、分かっている版・エラー・制約を入れる。

stdout に ID・title・description・trustScore・snippets・stars・state が並ぶ。名前一致 → 公式性（`trustScore`）→ コード例の量（`snippets`）→ 版の一致、の順で一つ選ぶ。選んだ ID はその問い合わせの間は保持し、途中で `ctx library` を呼び直さない。候補が無いときは stderr `No matching libraries.`。未登録なら系統を `tav` に切り替える。

## `ctx docs` のクエリ

検索語ではなく「実装したいこと」を自然言語で書く。

- ❌ `auth` / `Next.js`
- ✅ `Next.js 15 App Router で HttpOnly cookie のセッションを middleware で検証し、未認証を login に飛ばす方法`

含める要素: 目的、対象 API、言語/ランタイム、版、欲しい答え（署名・例・制約・移行）。独立した論点を1クエリに詰め込まない。

返ってきたら、ID と版が意図どおりか、import/API が今のコードと合うか、非推奨や制約が欠けていないかを見てから実装する。浅いときは同じ ID でクエリを狭めて再実行する。ID 解決のやり直しは、候補選択が間違っていたときだけ。結果に無い API を推測で補わない。
