# Azure Queue Storage の概要と制限値

調査日: 2026-10-23

## 概要

- 大量のメッセージを保存するためのサービス。HTTP/HTTPS の認証付き呼び出し(REST)でアクセスする
- ストレージアカウントの中に作る。URL は `https://<storage account>.queue.core.windows.net/<queue>`
- キュー名はすべて小文字
- メッセージは任意の形式で最大 64 KB
- TTL(有効期限)の既定は 7 日。バージョン 2017-07-29 以降は任意の正の値、または `-1`(期限なし)を指定できる
- 用途の例: 非同期に処理する作業のバックログ([Web-Queue-Worker](https://learn.microsoft.com/azure/architecture/guide/architecture-styles/web-queue-worker))
- 出典: https://learn.microsoft.com/azure/storage/queues/storage-queues-introduction

## スケーラビリティの目標値

| 項目 | 目標値 |
| --- | --- |
| 1キューの最大サイズ | 500 TiB |
| 1メッセージの最大サイズ | 64 KiB |
| キューあたりの保存されたアクセスポリシー数 | 5 |
| ストレージアカウントあたりの最大リクエスト率 | 20,000 メッセージ/秒(1 KiB のメッセージを前提) |
| 1キューのスループット目標(1 KiB のメッセージ) | 最大 2,000 メッセージ/秒 |

- パーティションの限界に達すると 503 (Server Busy) または 500 (Operation Timeout) が返る。503 には指数バックオフでのリトライを検討する
- 出典: https://learn.microsoft.com/azure/storage/queues/scalability-targets

## メッセージの取得(Get Messages)

- `numofmessages`: 1回で取得する件数。既定 1、最大 32
- `visibilitytimeout`: 取得後、他のクライアントから見えなくする時間(秒)。既定 30 秒、1 秒以上 7 日以下
- 取得してもメッセージは自動では削除されない。応答に含まれる `PopReceipt` を使って `Delete Message` で削除する
- `TimeNextVisible` までに削除しないと、メッセージは再び他のクライアントから見えるようになる
- `PopReceipt` は取得のたびに変わる。削除・更新が 404 になったら、別のクライアントがすでに取得している
- クロックスキューにより、可視性タイムアウトより前に再出現することがある(予約は保証されない)
- `DequeueCount` は初回取得で 1、削除されずに再取得されるたびに増える
- 出典: https://learn.microsoft.com/rest/api/storageservices/get-messages

## Service Bus キューとの主な違い

| 項目 | Storage Queue | Service Bus キュー |
| --- | --- | --- |
| 順序保証 | なし(通常は FIFO だが、可視性タイムアウト切れなどで順序が入れ替わる) | あり(セッション使用時) |
| 配信保証 | At-Least-Once | At-Least-Once(Peek-Lock)/ At-Most-Once(Receive-and-Delete) |
| 受信の挙動 | ノンブロッキング(メッセージがなければすぐ返る) | ブロッキング(ロングポーリング) |
| 受信モード | Peek & Lease | Peek & Lock / Receive & Delete |
| リース/ロック期間 | 既定 30 秒、最大 7 日。`UpdateMessage` で延長・解放できる | 既定 30 秒(※)。手動更新または自動ロック更新 |
| リース/ロックの粒度 | メッセージ単位(メッセージごとに異なるタイムアウトを設定・更新できる) | キュー単位 |
| バッチ受信 | あり(最大 32 件) | あり(プリフェッチ、トランザクション) |
| バッチ送信 | なし | あり |
| キューの最大サイズ | 500 TiB | 80 GB |
| 重複検出・トランザクション・DLQ・トピック | なし | あり |

- ※ 比較ページの記載のまま。Service Bus 側のロック期間の既定値は Service Bus のドキュメントも確認すること
- 出典: https://learn.microsoft.com/azure/service-bus-messaging/service-bus-azure-and-storage-queues-compared-contrasted

## Azure Functions のキュートリガー

- 失敗時、同じメッセージに対して最初の試行を含め最大 5 回実行する。5 回とも失敗すると `<元のキュー名>-poison` キューに移す
- 実行失敗時は `host.json` の `visibilityTimeout` に従って再表示する(既定 0 = すぐ再表示)
- ホストがクラッシュした場合は `visibilityTimeout` が適用できず、ストレージ側の既定 10 分後に再表示される(変更不可)
- アイドル時はランダム指数バックオフでポーリングし、トランザクションコストを抑える。最大間隔は `maxPollingInterval`
- 出典: https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-queue-trigger
