# Azure: at-least-once をサポートするサービス

## 1. Azure Service Bus

エンタープライズ向けのフルマネージドメッセージブローカー。通知基盤のキューとして第一候補。

### 基本

- エンティティ: **Queue**(1対1)、**Topic + Subscription**(1対多、サブスクリプションごとにフィルタ可能)
- プロトコル: AMQP 1.0 / HTTPS
- SKU: Standard(従量、メッセージ最大256KB)/ Premium(専有リソース、最大100MB、VNet・Private Link、安定したレイテンシ)

### at-least-once の仕組み

- 受信モードは2種類
  - **PeekLock(既定)**: 受信するとメッセージがロックされ、`Complete` で削除。ロック期間内に完了しなければ再配信 → **at-least-once**
  - ReceiveAndDelete: 受信時点で削除 → at-most-once(失敗時は消失)
- 主なAPI: `Complete`(削除)/ `Abandon`(即再配信)/ `DeadLetter`(DLQへ)/ `Defer`(後で取り出す)
- ロック期間(LockDuration): 既定1分、最大5分。処理が長いと重複配信の原因になるので、ロック更新(自動更新)を使う

### 重要機能

| 機能 | 内容 |
|---|---|
| **DLQ** | エンティティごとに組み込み(`/$deadletterqueue`)。MaxDeliveryCount(既定10)超過、TTL期限切れ、アプリからの明示送信で移動 |
| **セッション** | `SessionId` が同じメッセージは**FIFO**で、同時に1コンシューマのみが処理。ユーザー単位の順序保証に使える |
| **重複検出** | `MessageId` で一定期間(既定10分〜最大7日)内の重複送信を排除。送信側リトライによる重複を防ぐ |
| スケジュール送信 | 指定時刻に配信(遅延リトライ、予約通知) |
| TTL | メッセージ有効期限。期限切れはDLQへ移動可能 |
| トランザクション | 複数操作(受信完了+送信)をアトミックに |
| 自動転送(Auto-forward) | キュー/サブスクリプション間の連結 |

### 設計上の注意

- 順序が必要な場合、セッション単位で並列化する(セッション数 ≒ 並列度の上限)
- 組み込みの**優先度機能はない**。緊急/通常はキューを分ける
- リトライ待機(バックオフ)は自前実装が基本。スケジュール送信で再投入するか、Abandon後に再取得
- 「重複検出」は送信側の重複を防ぐだけ。受信側の再配信による重複は**冪等処理**が必要

---

## 2. Azure Storage Queue

Azure Storage アカウント内のシンプルで安価なキュー。

### 基本

- メッセージ最大**64KB**、キューあたりの容量はストレージアカウント上限まで(実質大容量)
- REST API(HTTP/HTTPS)。AMQPなどのプロトコルは使わない
- TTL: 既定7日(無期限も指定可)

### at-least-once の仕組み

- `Get Messages` で取得すると**可視性タイムアウト**(既定30秒、最大7日)の間、他のコンシューマから見えなくなる
- 処理後に `Delete Message` しないとタイムアウト後に再表示 → **at-least-once**
- `DequeueCount` が取得でき、リトライ回数を判断できる

### 制約

- **順序保証なし**(おおむねFIFOだが保証されない)
- **DLQなし**: DequeueCountを見て自前で別キュー(poison queue)へ移動する。Azure Functionsのキュートリガーは `<name>-poison` に自動で移す
- 重複検出、セッション、トピックなし
- 通知基盤では、順序要件がない大量バルク通知やジョブキューに向く

---

## 3. Azure Event Hubs

大量イベントを取り込む**ストリーム型**のサービス(Kafka互換エンドポイントあり)。

### 基本

- **パーティション**に分かれたログに追記。メッセージは削除されず、**保持期間**(Standard: 最大7日 / Premium・Dedicated: 最大90日)内なら再読み込み可能
- **コンシューマグループ**ごとに独立してオフセットを持つ
- 順序: **同一パーティション内**のみ保証。パーティションキー(例: userId)で同一パーティションに寄せる

### at-least-once の仕組み

- コンシューマは**チェックポイント**(オフセット)を保存(通常はBlob Storage)
- 処理済み〜チェックポイント保存前にクラッシュすると、その区間が再読み込みされる → **at-least-once**
- 公式SDKのEventProcessorがパーティション割り当て(負荷分散)とチェックポイントを担当

### 制約

- **個別メッセージのACK・DLQ・遅延リトライはない**。失敗メッセージのスキップや退避、リトライは自前実装(別Hub/キューへの再送など)
- 1件の失敗でそのパーティションが止まる(Head-of-line blocking)ため、設計上の工夫が必要
- 並列度の上限 = パーティション数
- 通知基盤では、取り込み口(イベント集約)や、後段のキューへ振り分けるルーターとして使うのが現実的

---

## 4. Azure Event Grid

イベント駆動のルーティングサービス(Pub/Sub)。

- 配信保証: **at-least-once**
- 失敗時はエクスポネンシャルバックオフでリトライ(最大24時間 / 最大試行回数を設定可)
- 配信できなかったイベントは**Blob Storageにデッドレター**として保存可能
- サブスクライバ側は**Webhook / Functions / Service Bus / Event Hubs / Storage Queue** など
- 用途: Azureリソースイベント(Blob作成など)の通知、サービス間疎結合。高スループットな通知配信のキューには不向き(個別の取得制御・順序保証がない)
- Event Grid Namespace(新しいモデル)では、**pull配信(キューのような取得・ACK・リリース・Reject)**やMQTTブローカーもサポートされる

---

## 使い分け早見表

| 用途 | 推奨 |
|---|---|
| ユーザー単位の順序保証+DLQ+リトライ | Service Bus(セッション) |
| 順序不要・安価・大量のジョブ | Storage Queue |
| 超高スループットの取り込み・再処理 | Event Hubs |
| Azureイベントの通知・疎結合 | Event Grid |

## 参考

- Service Bus: https://learn.microsoft.com/azure/service-bus-messaging/
- Storage Queue: https://learn.microsoft.com/azure/storage/queues/
- Event Hubs: https://learn.microsoft.com/azure/event-hubs/
- Event Grid: https://learn.microsoft.com/azure/event-grid/
