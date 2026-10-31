---
summary: ドメインごとの礼儀を守りながらページを集め、HTML を保存するクローラ
topic: system
---

# Web クローラ

シード URL からリンクを辿り、HTML を保存する。検索インデックスの構築はここには含めない。

## バリアント

まず `base/` を読み、その後に興味のあるバリアントへ進む。

| フォルダ | 内容 | level | status |
| --- | --- | --- | --- |
| [base](base/README.md) | 基礎となる構成(特定クラウドに依存しない) | 初級〜中級 | 未読 |
| [aws](aws/README.md) | AWS(SQS FIFO / ElastiCache Valkey の Bloom filter / S3 / Fargate / Lambda)で具体化。FIFO の制約・料金を学ぶ | 中級 | 未読 |
