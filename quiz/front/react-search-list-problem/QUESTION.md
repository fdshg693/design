---
summary: 検索ボックス付きの大量リスト画面で起きる再レンダリング・競合状態・Stale closure を、React の設計とフックの使い分けで解決する
topic: front
level: 中級
---

# 問題:検索付き商品一覧のパフォーマンスと正しさ(React 中級)

- 回答: `answer\front\react-search-list-problem.md`

## 背景

ECサイトの管理画面で、商品一覧(約 5,000 件)に**検索ボックス**・**カテゴリ絞り込み**・**お気に入りトグル**を持つ画面を React で作っている。
実装したところ、次の不具合・不満が出ている。

- 検索ボックスへの入力のたびに、一覧全体が再レンダリングされ**入力がカクつく**
- 素早く入力すると、**古いリクエストの結果が後から返ってきて**画面が古い検索結果に戻ることがある
- お気に入りを1件トグルしただけで、**全行の `ProductRow` が再レンダリング**される
- 一覧から詳細へ遷移して戻ると、検索条件がリセットされてしまう

## 現状のコード(抜粋)

```tsx
function ProductPage() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [products, setProducts] = useState<Product[]>([]);
  const [favorites, setFavorites] = useState<number[]>([]);

  useEffect(() => {
    fetch(`/api/products?q=${query}&category=${category}`)
      .then((res) => res.json())
      .then((data) => setProducts(data));
  }, [query, category]);

  const filtered = products.filter((p) => p.name.includes(query));

  const toggleFavorite = (id: number) => {
    setFavorites(
      favorites.includes(id)
        ? favorites.filter((f) => f !== id)
        : [...favorites, id]
    );
  };

  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <CategorySelect value={category} onChange={setCategory} />
      {filtered.map((p) => (
        <ProductRow
          key={p.id}
          product={p}
          isFavorite={favorites.includes(p.id)}
          onToggle={() => toggleFavorite(p.id)}
        />
      ))}
    </>
  );
}

const ProductRow = React.memo(function ProductRow({ product, isFavorite, onToggle }: Props) {
  return (
    <div>
      {product.name}
      <button onClick={onToggle}>{isFavorite ? "★" : "☆"}</button>
    </div>
  );
});
```

## 設問

1. このコードに含まれる問題点(競合状態、不要な state、`React.memo` が効かない理由など)を、原因とともにすべて挙げよ
2. 「古いリクエストの結果で上書きされる」問題を、`useEffect` のクリーンアップ(`AbortController` や無視フラグ)で直せ。さらに、ライブラリ(TanStack Query 等)を使うと何が楽になるかも述べよ
3. 入力のカクつきを解消する方法を、`useDeferredValue` / `useTransition` / デバウンスの3つで比較し、どれをどんな場面で選ぶか述べよ
4. `toggleFavorite` で全行が再レンダリングされないよう修正せよ。`useCallback`・関数型の state 更新・`Set` の利用がそれぞれ何に効くかを説明すること
5. 5,000 件を全件描画するのが重い場合の対策(仮想化、ページネーション等)と、その選択基準を述べよ
6. 「検索条件を詳細画面から戻っても保持する」ために、state をどこに持たせるべきか(URL の検索パラメータ、グローバルストア、ローカル state)を、トレードオフとともに述べよ

## ヒント

- `useEffect` 内の非同期処理は、**クリーンアップ関数**で何ができるか
- `query` から導出できる値を、state や effect で持つ必要があるか
- `React.memo` は props の**参照の同一性**で比較する。毎回新しく生成されるものは何か
- `setState(prev => ...)` は、どんな Stale closure を防ぐか
- 「入力の即時反映」と「重い結果の反映」は、優先度を分けられないか
