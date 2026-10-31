# AWS: at-least-once をサポートするサービス

## 1. Amazon SQS(Simple Queue Service)

フルマネージドのメッセージキュー。キューは2種類。

### SQS Standard

- スループット: ほぼ無制限
- 配信: **at-least-once**(まれに重複する)
- 順序: **ベストエフォート**(順序は保証されない)
- 用途: 順序不要・大量・スケール優先

### SQS FIFO

- 順序: **メッセージグループ(`MessageGroupId`)内でFIFO**。異なるグループは並列処理される(ユーザー単位の順序保証なら `MessageGroupId = userId`)
- 重複排除: `MessageDeduplicationId`(またはコンテンツベース)で**5分間**の重複送信を排除 → 送信側の重複を防ぐ
- スループット: 既定でAPIアクションあたり300メッセージ/秒(バッチで3,000/秒)。**高スループットモード**で大幅に拡張可能(リージョンにより上限が異なる)
- 注意: 「exactly-once processing」と説明されるが、**可視性タイムアウト超過などで再配信されうる**ため、コンシューマ側の冪等性は引き続き必要
- 同一グループでメッセージが失敗し続けると、そのグループ内の後続が止まる(グループ単位のHead-of-line blocking)

### at-least-once の仕組み

- `ReceiveMessage` で取得 → **可視性タイムアウト**(既定30秒、最大12時間)の間、他コンシューマから見えなくなる
- 処理後に `DeleteMessage`。削除されなければタイムアウト後に再び見える → **at-least-once**
- ロングポーリング(`WaitTimeSeconds` 最大20秒)でコスト・空ポーリング削減
- 処理が長い場合は `ChangeMessageVisibility` で延長

### 重要機能

| 機能 | 内容 |
|---|---|
| **DLQ** | 別のSQSキューをDLQとして指定。`maxReceiveCount` 超過で移動。標準キューのDLQは標準、FIFOのDLQはFIFOにする |
| **DLQ Redrive** | DLQからソースキューへコンソール/APIで再投入 |
| 遅延キュー / メッセージタイマー | 最大15分の配信遅延(リトライの待機に利用) |
| 保持期間 | 既定4日(1分〜14日) |
| メッセージサイズ | 最大256KB(拡張クライアントでS3利用可。近年さらに拡大されているため要確認) |
| 暗号化 | SSE-SQS / SSE-KMS |
| バッチ | 送信・受信・削除は最大10件/リクエスト |

### 設計上の注意

- **優先度機能なし** → urgent / bulk のキューを分ける
- 遅延リトライは可視性タイムアウト延長や遅延キューで実装(指数バックオフはコンシューマが `ChangeMessageVisibility` で制御)
- Lambdaイベントソースマッピングと組み合わせる場合、バッチ内の部分失敗は `ReportBatchItemFailures` で個別に返す(全バッチ再処理を避ける)

---

## 2. Amazon SNS(Simple Notification Service)

Pub/Sub型のファンアウトサービス。

- **標準トピック**: at-least-once 配信、順序保証なし
- **FIFOトピック**: メッセージグループ内の順序保証+重複排除。サブスクライバは主にSQS FIFO(近年SQS標準も可)
- サブスクライバ: SQS / Lambda / HTTP(S) / Email / SMS / モバイルプッシュ(APNs, FCM)など
- **サブスクリプションごとの配信リトライポリシー**と**DLQ**(SQS)を設定可能
- フィルタポリシー(メッセージ属性・本文)で宛先を絞れる
- 定番パターン: **SNS → 複数のSQS(ファンアウト)**。チャネルごとにキューを分離でき、遅いチャネルが他へ影響しない
- 注意: SNS自体は個別の遅延リトライ制御が限定的。バッファとして**SQSを間に挟む**のが一般的

---

## 3. Amazon Kinesis Data Streams

**ストリーム型**(ログ)サービス。

### 基本

- **シャード**単位でスケール(1シャードあたり書き込み 1MB/秒・1,000件/秒、読み取り 2MB/秒)。オンデマンドモード(自動スケール)/プロビジョンドモード
- 順序: **同一シャード内**のみ保証。パーティションキー(例: userId)のハッシュでシャードが決まる
- 保持期間: 既定24時間、最大365日。保持期間内はリプレイ可能
- 複数コンシューマ: 共有スループットまたは**拡張ファンアウト**(コンシューマごとに専用スループット)

### at-least-once の仕組み

- コンシューマ(KCL)が**チェックポイント**を保存(DynamoDBに保存)
- チェックポイント前にクラッシュすると再読み込み → **at-least-once**。プロデューサのリトライでも重複が発生しうる
- Lambda連携では、失敗時にバッチ全体が(期限まで)再試行され、そのシャードが詰まる。`BisectBatchOnFunctionError`、最大リトライ回数、失敗時の宛先(SQS/SNS)を設定して制御

### 制約

- 個別メッセージのACK・DLQ機能はなく、失敗時の退避は自前(またはLambdaのOn-failure destination)
- 並列度の上限 = シャード数(Lambdaは並列化係数で1シャードあたり最大10まで拡張可能だが、同一パーティションキーの順序は保たれる)

---

## 4. Amazon MSK(Managed Streaming for Apache Kafka)

マネージドKafka。Kafkaエコシステム(Connect, Streams等)を使いたい場合。

- 配信保証: コンシューマのオフセットコミット次第で **at-least-once**(処理後にコミット)
- 冪等プロデューサ+トランザクションで、Kafka内の処理についてはexactly-onceも可能(外部システムへの副作用は別途冪等性が必要)
- 順序: パーティション内。DLQはアプリ側でDLQトピックを作って実装
- MSK Serverless / Provisioned を選択可能

---

## 5. Amazon EventBridge

イベントバス型のサーバーレスルーティング。

- 配信: **at-least-once**
- ターゲットへの配信失敗時、**最大24時間・最大185回**(既定。調整可)までバックオフ付きでリトライ
- **DLQ(SQS)**をターゲットごとに設定可能
- イベントパターンによるルール・フィルタ、スケジュール、アーカイブ/リプレイ、API宛先、パイプ(Pipes)に対応
- 通知配信のキューというよりは、イベントのルーティング用。順序保証なし

---

## 6. Amazon MQ

ActiveMQ / RabbitMQ互換のマネージドブローカー。

- AMQP / MQTT / JMS / STOMPなど標準プロトコル対応(既存アプリの移行用途)
- 配信保証は**コンシューマACK方式で at-least-once**(未ACKは再配信)
- DLQ(ActiveMQのDLQ、RabbitMQのDead Letter Exchange)や優先度キュー(RabbitMQ/ActiveMQの優先度)も使える
- 新規設計ではSQS/SNSが優先され、Amazon MQは互換性重視のときに選ぶ

---

## 補足: Lambdaの非同期呼び出し

- Lambdaの非同期呼び出し(SNS/EventBridgeトリガーなど)は**at-least-once**。失敗時は既定で2回リトライ
- 失敗時の宛先(Destination)またはDLQ(SQS/SNS)を設定可能
- ハンドラは冪等に作ること

---

## 使い分け早見表

| 用途 | 推奨 |
|---|---|
| 大量・順序不要・シンプル | SQS Standard |
| ユーザー単位の順序保証+重複排除 | SQS FIFO(`MessageGroupId=userId`) |
| チャネル別のファンアウト | SNS → SQS(チャネルごとのキュー) |
| 超高スループット・リプレイ | Kinesis Data Streams / MSK |
| イベントのルーティング | EventBridge |
| 既存ActiveMQ/RabbitMQの移行 | Amazon MQ |

## 参考

- SQS: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/
- SNS: https://docs.aws.amazon.com/sns/
- Kinesis: https://docs.aws.amazon.com/streams/latest/dev/
- MSK: https://docs.aws.amazon.com/msk/
- EventBridge: https://docs.aws.amazon.com/eventbridge/
- Amazon MQ: https://docs.aws.amazon.com/amazon-mq/
