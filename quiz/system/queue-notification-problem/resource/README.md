# at-least-once をサポートするAzure・AWSのメッセージングサービス

問題: [QUESTION.md](../QUESTION.md)

- [azure.md](azure.md) … Azureのサービス詳細
- [aws.md](aws.md) … AWSのサービス詳細

## at-least-once とは

- メッセージは**最低1回**は配信される。失敗やタイムアウト時は再配信されるので、**重複して届く可能性がある**
- 仕組みは共通: 「受信 → 処理 → **ACK(削除/チェックポイント)**」。ACKが届く前にコンシューマが落ちたり、可視性タイムアウト/ロックが切れると再配信される
- したがって**コンシューマ側は冪等に作る**のが前提(exactly-onceの代替は「at-least-once + 冪等性」)
- 対比: at-most-once(ACK先行で、失敗時は消失)、exactly-once(ブローカー内のみ成立するなど条件付き)

## 全体比較

| 分類 | Azure | AWS | 特徴 |
|---|---|---|---|
| キュー(メッセージブローカー) | Service Bus Queue | SQS Standard / FIFO | 1メッセージ=1コンシューマ、個別ACK、DLQ、リトライ |
| Pub/Sub(ファンアウト) | Service Bus Topic | SNS(+SQS) | 1メッセージを複数サブスクライバに配信 |
| シンプルなキュー | Storage Queue | SQS Standard | 安価・大容量、機能は少なめ |
| ストリーム(ログ型) | Event Hubs | Kinesis Data Streams / MSK | パーティション順序、オフセット管理、リプレイ可能 |
| イベントルーティング | Event Grid | EventBridge | イベント通知、リトライ+DLQ |
| 互換ブローカー | (Service Bus: AMQP) | Amazon MQ | ActiveMQ/RabbitMQ互換 |

## 機能比較(キュー系・ストリーム系の主要サービス)

| 項目 | Service Bus | Storage Queue | Event Hubs | SQS Standard | SQS FIFO | Kinesis |
|---|---|---|---|---|---|---|
| 配信保証 | at-least-once(PeekLock) | at-least-once | at-least-once | at-least-once | FIFOで重複排除(処理は実質at-least-once) | at-least-once |
| 順序 | セッションでFIFO | 保証なし(おおむねFIFO) | パーティション内 | ベストエフォート | メッセージグループ内 | シャード内 |
| 個別ACK | あり | あり(削除) | なし(チェックポイント) | あり(削除) | あり(削除) | なし(チェックポイント) |
| DLQ | 標準装備 | なし(ポイズンキューを自作) | なし | あり(設定) | あり(設定) | なし(自作) |
| 重複排除 | あり(MessageId) | なし | なし | なし | あり(5分) | なし |
| リプレイ | 不可 | 不可 | 可(保持期間内) | 不可 | 不可 | 可(保持期間内) |

## 通知配信問題との対応(目安)

| 要件 | 使えそうな機能 |
|---|---|
| 同一ユーザー内の順序 | Service Bus セッション(SessionId=userId)、SQS FIFO(MessageGroupId=userId)、Event Hubs/Kinesis(パーティションキー=userId) |
| 失敗し続けるメッセージの隔離 | Service Bus DLQ(MaxDeliveryCount)、SQS DLQ(maxReceiveCount) |
| 重複抑制 | Service Bus 重複検出、SQS FIFO 重複排除、いずれもコンシューマ側冪等性が別途必要 |
| チャネル別の分離(HoL回避) | チャネルごとにキュー/サブスクリプションを分ける(Topic+フィルタ、SNS+SQS) |
| 緊急通知の優先 | 優先度キューは未サポートが基本。**キューを分ける**(urgent / bulk)のが定石 |

> 注: クォータや上限値はリージョン・SKU・時期で変わる。設計時は必ず公式ドキュメントで確認すること。
