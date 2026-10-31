---
summary: キューと Pub/Sub トピックを提供する、Azure のフルマネージドなエンタープライズ向けメッセージブローカー
category: メッセージング
status: 着手
---

# Azure Service Bus

## 学習の進め方

1. `scenarios/` のシナリオを順番に解く(`回答` 欄に書く)
2. AI が `レビュー` を書き、学んだことを `ポイント` にまとめる
3. 機能マップの未着手の機能や、出てきた疑問から次のシナリオを作る

## シナリオ一覧

| # | シナリオ | 機能 | 種類 | レベル | 状態 |
| --- | --- | --- | --- | --- | --- |
| 01 | [注文処理キューの基本設計](scenarios/01-order-queue-basics.md) | queues, peek-lock, dead-letter | design | 初級 | 出題済 |

## 機能マップ

### 基本

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| キュー | 1対1、競合コンシューマー、負荷平準化 | [01](scenarios/01-order-queue-basics.md) |
| トピック/サブスクリプション | 1対多(Pub/Sub)、サブスクリプションごとの独立した配信 | - |
| フィルターとアクション | SQL / 相関フィルター、サブスクリプションルール | - |
| 受信モード | Peek-Lock と Receive-and-Delete、ロック期間とロックの更新 | [01](scenarios/01-order-queue-basics.md) |
| メッセージの処理結果(Settlement) | Complete / Abandon / Dead-letter / Defer | - |
| 配信不能キュー(DLQ) | 最大配信回数、TTL 切れ、再投入の運用 | [01](scenarios/01-order-queue-basics.md) |
| TTL / 有効期限 | メッセージの有効期限と、期限切れ時の DLQ 移動 | - |

### 高度な機能

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| セッション | FIFO、順序保証、セッション状態、要求-応答パターン | - |
| 重複検出 | 送信側の再試行による重複、検出期間 | - |
| スケジュール配信 | 指定した時刻に処理させる | - |
| 遅延(Deferral) | 受信したが今は処理できないメッセージを後回しにする | - |
| トランザクション | 受信→送信→完了を1つのアトミックな処理にする | - |
| 自動転送(Auto-forwarding) | エンティティの連結、ファンアウト | - |
| アイドル時の自動削除 | 一時的なエンティティの後片付け | - |
| バッチ削除 | 不要メッセージの一括削除 | - |

### 性能・制限

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| Tier(Basic / Standard / Premium) | 機能差、共有か専用か、課金モデル | - |
| Messaging Unit(Premium) | サイジング、オートスケール | - |
| パーティション | スループット、Tier による違い | - |
| 大きいメッセージ | Standard 256 KB / Premium 100 MB、Claim Check パターン | - |
| プリフェッチとバッチ処理 | スループットとロック期限切れのトレードオフ | - |
| スロットリング | クォータ超過時の挙動 | - |

### 運用・セキュリティ・DR

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| 認証・認可 | SAS、Entra ID RBAC、マネージド ID | - |
| ネットワーク | IP ファイアウォール、Private Endpoint(Premium) | - |
| 暗号化 | Microsoft 管理キー / CMK(Premium) | - |
| 可用性 | 可用性ゾーン | - |
| DR | Geo-Replication、Geo-DR(メタデータのみ) | - |
| 監視 | メトリクス(アクティブメッセージ数、DLQ 数、サーバーエラーなど)、診断ログ | - |
| プロトコル・SDK | AMQP 1.0、SBMP の廃止(2026-09-30)、JMS | - |
| Azure Functions との連携 | Service Bus トリガーの完了処理と再試行の挙動 | - |

## 似たサービス・競合サービス

| サービス | 一言でいうと | 比較シナリオ |
| --- | --- | --- |
| [Azure Storage Queues](../azure-storage-queue/README.md) | シンプルで安価な大容量キュー。順序保証・DLQ・トピックなどの高度な機能はない | - |
| Azure Event Grid | イベント通知(何かが起きたこと)を push 型で配信する | - |
| Azure Event Hubs | 大量のイベントストリームを取り込む。ログ型で、読み直しができる | - |
| RabbitMQ / ActiveMQ | 自前で運用する AMQP / JMS ブローカー | - |
| Amazon SQS / SNS | AWS のキュー / Pub/Sub | - |

## 調査結果(resource)

- [概要と Tier の違い](resource/overview-and-tiers.md)
- [デッドレターキュー(DLQ)](resource/dead-letter-queue.md)

## 関連

- [projects/ec-order-processing](../../projects/ec-order-processing/README.md)
- [quiz/system/queue-notification-problem/resource](../../quiz/system/queue-notification-problem/resource/README.md)
