---
summary: 遅いクライアント側フェッチだらけの管理ダッシュボードを、Server/Client Components の境界設計・Suspense によるストリーミング・Server Actions で作り直す
topic: front
level: 中級〜上級
---

# 問題:Server Components で作り直す管理ダッシュボード(React 中級〜上級)

## 背景

SaaS の管理画面にある**ダッシュボード**を React(Next.js App Router / React 19)で作っている。
画面は次の 4 つのパネルで構成される。

| パネル | データ取得元 | 応答時間の目安 | 備考 |
| --- | --- | --- | --- |
| ヘッダー(ログインユーザー名・テナント名) | 認証 API | 50ms | 全パネルで同じユーザー情報を使う |
| 売上サマリー(今月の売上・前月比) | 集計 API | 200ms | 数字だけ。操作なし |
| 売上グラフ(期間を切り替えられる折れ線) | 集計 API | 300ms | 期間切り替え・ホバーでツールチップ |
| 最近の注文一覧 + 「メモを追加」フォーム | 注文 API | 1,500ms(遅い) | フォーム送信後、一覧に反映したい |

現状はすべて Client Component で、次の不満が出ている。

- 初回表示で**真っ白な時間が長く**、その後スピナーが 4 つ並び、ばらばらに表示される
- Lighthouse で **JavaScript バンドルが大きい**と指摘される(グラフライブラリ・日付ライブラリ・Markdown パーサー全部入り)
- 注文 API が遅いせいで、**速いはずの売上サマリーまで表示が遅れる**ことがある
- 注文 API がエラーになると、**ダッシュボード全体が壊れて真っ白**になる
- メモを追加しても、**ページをリロードするまで一覧に出てこない**

## 現状のコード(抜粋)

```tsx
// app/dashboard/page.tsx
"use client";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [orders, setOrders] = useState<Order[] | null>(null);

  useEffect(() => {
    (async () => {
      const u = await fetch("/api/me").then((r) => r.json());
      setUser(u);
      const o = await fetch(`/api/orders?tenant=${u.tenantId}`).then((r) => r.json());
      setOrders(o);
      const s = await fetch(`/api/summary?tenant=${u.tenantId}`).then((r) => r.json());
      setSummary(s);
    })();
  }, []);

  if (!user) return <Spinner />;

  return (
    <Layout>
      <Header user={user} />
      {summary ? <SummaryPanel summary={summary} /> : <Spinner />}
      <SalesChart tenantId={user.tenantId} /> {/* 内部で useEffect + fetch */}
      {orders ? <OrderList orders={orders} /> : <Spinner />}
      <AddMemoForm
        onSubmit={async (text) => {
          await fetch("/api/memos", { method: "POST", body: JSON.stringify({ text }) });
        }}
      />
    </Layout>
  );
}

// OrderList.tsx — 各注文の備考欄を Markdown → HTML に変換して表示
import { marked } from "marked";
import { format } from "date-fns";
export function OrderList({ orders }: { orders: Order[] }) { /* ... */ }
```

## 設問

1. 現状のコードの問題点を、**ネットワーク(ウォーターフォール)**・**バンドルサイズ**・**エラーの影響範囲**・**データの鮮度**の観点で整理せよ
2. 4 つのパネル(とその中の部品)を **Server Component / Client Component** に振り分けよ。`"use client"` をどこに置くか、その判断基準(state・イベントハンドラ・ブラウザ API の有無など)を説明すること
3. Client Component の境界を**できるだけ葉(下の方)に寄せる**とよい理由を述べよ。また、Client Component の中に Server Component を表示したいときはどうするか(`children` / props で渡すパターン)を説明せよ
4. 「遅い注文 API が速いパネルの表示を巻き込む」問題を、`<Suspense>` によるストリーミングで解決せよ。どの単位で `<Suspense>` 境界を切るか、フォールバックをどう設計するか(レイアウトシフトへの配慮を含む)を述べよ
5. データ取得の**ウォーターフォール**を解消せよ。ユーザー情報のように複数コンポーネントが使うデータを、props のバケツリレーをせずに重複リクエストなく取得する方法(リクエスト単位のメモ化など)も述べること
6. 「注文パネルだけエラーにして、他は表示し続ける」ための**エラー境界**の設計を述べよ。どの粒度で置くか、再試行 UI をどう提供するか
7. 「メモを追加」を **Server Actions** で実装する方針を述べよ。送信後に一覧へ反映する方法(再検証)、送信中・失敗時の UI(`useActionState` / `useFormStatus` / `useOptimistic` など)、セキュリティ上の注意点(認可・入力検証)を含めること
8. この構成にしたことで**失うもの・難しくなるもの**(サーバー負荷、キャッシュの複雑さ、Server/Client 間で渡せる値の制約など)を挙げ、どんな画面なら従来の Client Component 中心の構成のほうが向いているか述べよ

## ヒント

- `await` を順番に並べると、各リクエストはいつ始まるか
- Server Component でだけ使うライブラリは、ブラウザに送られるか
- `"use client"` を付けたファイルが import しているコンポーネントは、どちら側として扱われるか
- Server Component から Client Component に渡す props は、どんな形式に変換されて送られるか(関数や `Date` は渡せるか)
- `<Suspense>` 境界が 1 つしかないと、ストリーミングの単位はどうなるか
- エラー境界は、どのフェーズのエラーを捕まえられて、どれを捕まえられないか(イベントハンドラ内のエラーなど)
- Server Action は「ただの関数呼び出し」に見えるが、実体は何か。誰でも呼び出せるとしたら何を確認すべきか
