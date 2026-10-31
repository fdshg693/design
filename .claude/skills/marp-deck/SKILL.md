---
name: marp-deck
description: ユーザーがパワーポイント・スライド・プレゼン資料(pptx)の作成を明示的に依頼したときだけ使う。題材フォルダ配下の deliverables/ にまず Markdown で構成案(OUTLINE.md)を書き、ユーザーの OK が出てから Marp で slides.md を作り pptx に変換する。このリポジトリでは anthropic-skills:pptx より優先する。依頼がないのに資料化を提案・実行しない。
# 前提: pnpm(mise 管理)と Edge が必要。marp-cli / mermaid-cli は pnpm dlx で都度実行(グローバルインストールしない)
# 同梱ファイル: outline-template.md(構成案の雛形) / puppeteer.json(mermaid-cli が Edge を使う設定)
allowed-tools: Bash(pnpm dlx *)
---

# Marp でパワーポイント資料を作る

**2 段階で進める。構成案(OUTLINE.md)にユーザーの OK が出るまで、slides.md と pptx は作らない。**

## 1. 置き場所を決める

題材のフォルダ直下に `deliverables/<資料名>/` を作る(資料名は英小文字のケバブケース、例: `design-review`)

| 題材 | 置き場所 |
| --- | --- |
| projects | `projects/<サービス名>/deliverables/<資料名>/` |
| quiz | `quiz/<トピック>/<問題名>/deliverables/<資料名>/` |
| services | `services/<サービス名>/deliverables/<資料名>/` |
| readings | `readings/<トピック>/<題材名>/deliverables/<資料名>/`(base / バリアントをまたいでも題材直下に 1 つ) |

- 対象の題材が会話や開いているファイルから特定できない場合だけ、ユーザーに聞く
- 同じ資料名のフォルダが既にあれば、上書きせず更新か別名かを確認する

最終的な構成:

```
deliverables/<資料名>/
  OUTLINE.md        # 構成案(ステップ 2)
  slides.md         # Marp ソース(ステップ 4)
  diagrams/*.mmd    # Mermaid 図のソース
  images/*.svg      # 図の変換結果
  <資料名>.pptx     # 完成品
```

## 2. 構成案を書く(OUTLINE.md)

[outline-template.md](outline-template.md) をコピーして埋める

- 元ネタは題材フォルダ内の既存ファイル(design/、DESIGN.md、ANSWER.md、scenarios/ など)。**書かれていない設計判断や数値を勝手に足さない**。足す場合は「追加提案」と明記する
- 聞き手・目的・時間が依頼から読み取れなければ、テンプレートの値を仮置きし、確認事項に挙げる
- 1 スライド 1 メッセージ。目安は発表時間 1 分 ≒ 1 枚
- 各スライドに「図」欄を設け、使う Mermaid 図(既存ファイルのどの図か、新規か)を書く
- フロントマターの `status` は `構成案`

書いたら、スライド一覧の要約と確認事項をユーザーに示し、**OK が出るまで止まる**。修正依頼があれば OUTLINE.md を直して再度確認する

## 3. OK が出たら、いったん止まる

OUTLINE.md の `status` を `OK` にする。以降、構成を変えたくなったら先に OUTLINE.md を直してユーザーに確認する

**`status: OK` にしたら、必ずそこで止まり、「このまま slides.md / pptx の作成に進むか」をユーザーに聞く。** 返事を待たずにステップ 4 に進まない

- ユーザーはここでセッションを分け、別のエージェントに構成案を見せて質問・修正することがある
- 続ける場合はステップ 4 へ。別セッションで再開する場合のために、OUTLINE.md のパスを伝えておく

### 別セッションで再開するとき

- 既存の `deliverables/<資料名>/OUTLINE.md` の `status` を見て、どこから再開するかを決める
    - `構成案`: ステップ 2 の確認から
    - `OK`: OUTLINE.md 以外に会話の前提がないので、まず OUTLINE.md と `source` のファイルを読み、ステップ 4 から進める
    - `作成済み`: 修正依頼への対応として扱う
- 前のセッション以降に OUTLINE.md が手で直されている可能性があるので、記憶ではなくファイルの内容に従う

## 4. Marp ソースを書く(slides.md)

```markdown
---
marp: true
theme: default
paginate: true
size: 16:9
title: <資料タイトル>
---

<!-- _class: lead -->
<!-- _paginate: false -->

# <資料タイトル>

<サブタイトル / 日付>

---

## <スライドタイトル>

- 箇条書きは 3〜5 行まで

![w:900](images/01-overview.svg)

<!--
発表者ノート: 話す内容をここに書く(pptx のノートになる)
-->
```

- スライド区切りは `---`。OUTLINE.md のスライド番号と順番を一致させる
- 発表者ノートは HTML コメントで書く(OUTLINE.md の「話すこと」を移す)
- 文字が溢れそうなら `<!-- _class: small -->` に頼らず、スライドを分けるか削る
- **Mermaid は Marp で描画されない**ので、次の手順で SVG にして画像として貼る

### Mermaid 図を SVG にする

図ごとに `diagrams/<番号>-<名前>.mmd` を書き、`deliverables/<資料名>/` で実行:

```bash
PUPPETEER_SKIP_DOWNLOAD=1 pnpm dlx --allow-build=puppeteer @mermaid-js/mermaid-cli \
  -p "${CLAUDE_SKILL_DIR}/puppeteer.json" -b white \
  -i diagrams/01-overview.mmd -o images/01-overview.svg
```

- 元の設計ファイルの Mermaid をそのまま流用してよいが、スライド用にノードを減らして簡略化するのが望ましい(横長の `flowchart LR` が収まりやすい)

## 5. pptx に変換して確認する

`deliverables/<資料名>/` で実行:

```bash
# 確認用 PNG(全スライド)
pnpm dlx @marp-team/marp-cli slides.md --images png --allow-local-files -o temp-preview/slide.png
# pptx
pnpm dlx @marp-team/marp-cli slides.md --pptx --allow-local-files -o <資料名>.pptx
```

- PNG を Read で目視し、文字の溢れ・図の潰れ・日本語の表示を確認して直す。確認後 `temp-preview/` は削除する
- pptx の各スライドは画像として埋め込まれるため、PowerPoint 上でテキスト編集はできない(編集が必要なら slides.md を直して再変換)。そのことをユーザーに伝える
- OUTLINE.md の `status` を `作成済み` にし、pptx のパスをユーザーに伝える

## 修正依頼への対応

- 文言・図の修正: slides.md / diagrams を直して再変換
- 構成(枚数・順番・主張)の変更: OUTLINE.md を直して確認を取ってから slides.md に反映
