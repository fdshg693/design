---
summary: ストレージアカウント上で動く、シンプルで安価な大容量メッセージキュー
category: メッセージング
status: 着手
---

# Azure Storage Queue

## 学習の進め方

1. `scenarios/` のシナリオを順番に解く(`回答` 欄に書く)
2. AI が `レビュー` を書き、学んだことを `ポイント` にまとめる
3. 機能マップの未着手の機能や、出てきた疑問から次のシナリオを作る

## シナリオ一覧

| # | シナリオ | 機能 | 種類 | レベル | 状態 |
| --- | --- | --- | --- | --- | --- |
| 01 | [レポート生成ジョブキューの基本設計](scenarios/01-report-generation-queue.md) | visibility-timeout, dequeue-count, update-message | design | 初級 | 出題済 |

## 機能マップ

### 基本

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| メッセージの送信・取得・削除 | Put / Get / Delete、`PopReceipt`、取得しただけでは消えない | [01](scenarios/01-report-generation-queue.md) |
| 可視性タイムアウト | 既定 30 秒・最大 7 日、処理時間を超えたときの重複処理 | [01](scenarios/01-report-generation-queue.md) |
| メッセージの更新(UpdateMessage) | リースの延長・解放、処理の進捗をメッセージに書き戻す | [01](scenarios/01-report-generation-queue.md) |
| DequeueCount と有害メッセージ | DLQ がないので、取得回数を見てアプリ側で退避する | [01](scenarios/01-report-generation-queue.md) |
| Peek | ロックせずに中身を確認する | - |
| TTL / 有効期限 | 既定 7 日、`-1` で無期限、期限切れは黙って消える | - |
| 送信時の初期非表示 | `visibilitytimeout` を付けて送信し、遅延実行させる | - |
| 順序 | 順序保証なし、FIFO が崩れるケース | - |

### 性能・制限

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| メッセージサイズ | 64 KB 上限、Base64 エンコードによる目減り、Claim Check パターン | - |
| スループット | キューあたり 2,000 msg/秒、アカウントあたり 20,000 msg/秒、キューの分割 | - |
| バッチ取得 | 最大 32 件、可視性タイムアウトとの関係 | - |
| ポーリング | ノンブロッキング受信、空ポーリングのトランザクションコスト、バックオフ | - |
| スロットリング | 503 / 500 と指数バックオフ | - |
| 課金 | 容量 + トランザクション、固定の時間課金なし | - |

### 運用・セキュリティ・DR

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| 認証・認可 | アカウントキー、SAS(保存されたアクセスポリシー)、Entra ID RBAC、マネージド ID | - |
| ネットワーク | ストレージファイアウォール、Private Endpoint | [azure-storage/01](../azure-storage/scenarios/01-private-endpoint-lockdown.md)(アカウント共通の話として) |
| 冗長性 | LRS / ZRS / GRS / GZRS、フェイルオーバー時のキューの扱い | - |
| 監視 | キューの長さ(概算)、最古メッセージの滞留時間、Storage のメトリクス・診断ログ | - |
| 暗号化 | Microsoft 管理キー / CMK | - |
| Azure Functions との連携 | キュートリガーの再試行(5 回)、`-poison` キュー、クラッシュ時の 10 分、`batchSize` | - |
| Event Grid 等からの出力先 | 他サービスのイベントの受け皿としての Storage Queue | - |

## 似たサービス・競合サービス

| サービス | 一言でいうと | 比較シナリオ |
| --- | --- | --- |
| [Azure Service Bus](../azure-service-bus/README.md) | 順序保証、DLQ、重複検出、トランザクション、トピックを持つエンタープライズ向けブローカー。キューは最大 80 GB | - |
| Azure Event Grid | イベント通知を push 型で配信する | - |
| Azure Event Hubs | 大量のイベントストリームを取り込む。ログ型で、読み直しができる | - |
| Amazon SQS | AWS のキュー。可視性タイムアウトの考え方が近い | - |

## 調査結果(resource)

- [概要と制限値](resource/overview-and-limits.md)

## 関連

- [services/azure-service-bus/scenarios/01](../azure-service-bus/scenarios/01-order-queue-basics.md)(Peek-Lock / DLQ との対比)
- [quiz/system/queue-notification-problem/resource](../../quiz/system/queue-notification-problem/resource/README.md)
