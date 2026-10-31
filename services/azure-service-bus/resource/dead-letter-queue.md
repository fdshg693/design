# Service Bus のデッドレターキュー(DLQ)

調査日: 2026-10-23

## 通常のキューとの違い

- キューとトピックのサブスクリプションに付いているサブキュー。明示的に作る必要はなく、親エンティティと別に削除・管理することもできない
    - パス: `<queue path>/$deadletterqueue`、`<topic path>/Subscriptions/<subscription path>/$deadletterqueue`
- API・プロトコル上は、ほぼ通常のキューと同じ(Peek-Lock、Receive-and-Delete、トランザクションが使える)。ただし次の点が違う
    - メッセージを入れる方法は、親エンティティでのデッドレター操作だけ(直接送信できない)
    - TTL が適用されない
    - DLQ のメッセージをさらにデッドレターにはできない
- 自動では削除されない。DLQ から取り出して Complete するまで残る

## ブローカーが自動で DLQ に移す主なケース

| 理由(`DeadLetterReason`) | 条件 |
| --- | --- |
| `MaxDeliveryCountExceeded` | 配信回数が上限(既定 10)を超えた。Abandon またはロック期限切れで回数が増える。この動作は無効化できない(上限を大きくすることはできる) |
| `TTLExpiredException` | 期限切れ時のデッドレターを有効にしている場合に、期限切れになった |

- アプリから明示的にデッドレターにすることもできる。その際、`DeadLetterReason` と `DeadLetterDescription` に例外の種類やスタックトレースを入れることが推奨されている
- 自動転送・Send via で転送できなかったメッセージは、転送元エンティティの転送デッドレターキュー(`$Transfer/$DeadLetterQueue`)に入る
- 出典: https://learn.microsoft.com/azure/service-bus-messaging/service-bus-dead-letter-queues
