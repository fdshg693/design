---
summary: Redis OSS 7.2.4 から分岐した、Linux Foundation 管理の BSD ライセンスのインメモリ KV ストア。Redis とコマンド互換
category: db
level: 中級(Redis の基本を読んだ前提)
status: 未読
---

# Valkey

## 一言でいうと

**「ライセンス変更前の Redis を引き継いだ、オープンソース版の Redis」**。
2024 年 3 月に Redis OSS 7.2.4 から分岐(フォーク)し、Linux Foundation の下で BSD 3-Clause ライセンスのまま開発が続いている。
コマンド・プロトコル(RESP)・データ構造・Cluster・Lua は Redis と共通なので、**Redis の知識がほぼそのまま使える**。

## 何を解決するか

- Redis が 7.4 からソース公開ライセンス(RSALv2 / SSPLv1)に変わり、クラウド事業者や企業が自由に使い続けにくくなった問題
- 「Redis 互換のまま、特定企業に依存しない」インメモリ KV ストアがほしい、という需要
- 加えて、分岐後は性能(マルチスレッド I/O)・メモリ効率・Cluster 運用で独自の改良が入っている

## いつ使う / 使わない

| 使う | 使わない(または Redis を検討) |
| --- | --- |
| Redis の用途全般(キャッシュ、カウンタ、レート制限、ロック、ランキング) | Redis 8 の組み込み機能(Query Engine、Vector Sets、Time Series)を中心に使いたい |
| ライセンス上 BSD 系の OSS にしておきたい | Redis Ltd. の商用サポート・Redis Cloud を使う前提 |
| AWS ElastiCache / Google Memorystore で安く使いたい | — |

主データにしない、メモリに収まらない量を置かない、などの注意点は Redis と同じ([../redis/README.md](../redis/README.md))。

## 読む順番

1. [01-overview.md](01-overview.md): Valkey の全体像(誕生の経緯、Redis との互換性と違い、バージョンごとの改良、マネージドサービス)
2. [QA.md](QA.md): 質問と回答のログ

Valkey の土台(シングルスレッド実行、データ構造、永続化、Cluster、Lua)は Redis と共通なので、先に Redis のドキュメントを読むとよい。

- [../redis/01-overview.md](../redis/01-overview.md)
- [../redis/02-cluster.md](../redis/02-cluster.md)
- [../redis/03-scripting.md](../redis/03-scripting.md)

## 前提バージョン

- **Valkey 9.1(2026 年 5 月 GA、2026-10 時点の最新は 9.1.3)** を前提に書いている。バージョン依存の挙動は本文中で明記する
- 保守されているリリース系列: 9.1 / 9.0 / 8.1 / 8.0 / 7.2

## 関連

- [../../readings/system/rate-limiter/aws/DESIGN.md](../../readings/system/rate-limiter/aws/DESIGN.md): ElastiCache Serverless for Valkey をレート制限のカウンタに使う設計
