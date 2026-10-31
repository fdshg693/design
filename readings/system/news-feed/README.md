---
summary: フォロー中のテキスト投稿を新しい順にホームへ出すサービス
topic: system
---

# ホームタイムライン

テキストを投稿し、フォローしている人の投稿を新しい順にホームへ並べる。

## バリアント

まず `base/` を読み、その後に興味のあるバリアントへ進む。

| フォルダ | 内容 | level | status |
| --- | --- | --- | --- |
| [base](base/README.md) | 基礎となる構成(特定クラウドに依存しない) | 初級〜中級 | 読解中 |
| [aws](aws/README.md) | AWS(DynamoDB + Streams / Lambda / ElastiCache for Valkey / ECS)で具体化。二重書き込みの回避・メモリと転送料を学ぶ | 中級 | 未読 |
