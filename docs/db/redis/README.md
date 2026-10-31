---
summary: インメモリで動く高速なデータ構造サーバー。キャッシュ・カウンタ・ランキング・ロック・軽量キューなどに使われる
category: db
level: 中級(キュー・キャッシュ・レプリケーションの一般概念は理解済み)
status: 未読
---

# Redis

## 一言でいうと

**「ネットワーク越しに使える、永続化もできるインメモリのデータ構造(String / Hash / List / Set / Sorted Set / Stream …)」**。
単なる KV キャッシュではなく、**データ構造ごとの原子的な操作**をサーバー側で提供するのが本質。

## 何を解決するか

- RDB では重い「高頻度・低レイテンシ」な読み書き(サブミリ秒)
- 複数アプリサーバー間での共有状態(セッション、レート制限カウンタ、分散ロック)
- 「読んで→計算して→書く」を **競合なしに** 行いたい処理(INCR、Sorted Set、Lua スクリプト)

## いつ使う / 使わない

| 使う | 使わない |
| --- | --- |
| キャッシュ、セッションストア | データ量がメモリに収まらない主データ |
| ランキング(Sorted Set)、カウンタ、レート制限 | 複雑な検索・JOIN・アドホック集計 |
| 分散ロック(単一障害で壊れても致命的でない用途) | 1 件のロストも許されない台帳・決済の正本 |
| 軽量なジョブキュー / イベントログ(Stream) | 長期保持・大量リプレイが前提のイベント基盤(→ Kafka) |

## 読む順番

1. [01-overview.md](01-overview.md): Redis の特徴の全体像(シングルスレッド、データ構造、永続化、レプリケーション、Sentinel、Eviction、Pub/Sub・Stream)
2. [02-cluster.md](02-cluster.md): Redis Cluster(ハッシュスロット、リダイレクト、ハッシュタグ、フェイルオーバー、制約)
3. [03-scripting.md](03-scripting.md): 原子性の道具箱(MULTI/EXEC、WATCH、Lua スクリプト、Redis Functions)
4. [QA.md](QA.md): 質問と回答のログ

## 前提バージョン

- 主に **Redis 7.x 〜 8.x(OSS)** を前提に書いている。バージョン依存の挙動は本文中で明記する
- ライセンス事情: 2024 年(7.4)にソース公開ライセンス(RSALv2 / SSPLv1)へ変更 → Linux Foundation 配下で OSS フォーク **Valkey** が誕生 → Redis 8 で AGPLv3 も選択肢に追加。AWS ElastiCache などは Valkey も提供している。コマンド・概念はほぼ共通(→ [../valkey/README.md](../valkey/README.md))
