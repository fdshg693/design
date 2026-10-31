# 図解:注文イベント配信を Kafka で組む

[ANSWER.md](ANSWER.md) の内容を、図を中心にまとめ直したもの。細かい理由づけは ANSWER.md を参照。

## 全体像(決めたこと一覧)

| 設問 | 決定 | 一言でいうと |
|---|---|---|
| 1. キー | `order_id` | 順序を守りたい最小の単位 |
| 2. パーティション数 | 40(最低 30) | 600 イベント/秒 ÷ 20 件/秒 = 30、そこに約1.3倍の余裕 |
| 3. コンシューマグループ | サービスごとに3グループ | 全サービスが全件を受け取るため |
| 4. コミット | 処理の後に手動コミット | 取りこぼしより重複のほうがまし |
| 5. 失敗し続けるイベント | リトライ上限 → DLQ | パーティション全体を止めないため |

完成形の構成は次のとおり。

```mermaid
flowchart LR
    P[注文サービス] -->|"key = order_id"| T

    subgraph T["topic: order-events(40 パーティション)"]
        direction TB
        P0[P0]
        P1[P1]
        Pdots[...]
        P39[P39]
    end

    T --> G1
    T --> G2
    T --> G3

    subgraph G1["group: notification-service"]
        N["40 インスタンス"]
    end
    subgraph G2["group: delivery-assignment-service"]
        D["3 インスタンス"]
    end
    subgraph G3["group: sales-aggregation-service"]
        S["2〜3 インスタンス"]
    end

    N -->|プッシュ通知| EXT["外部API(APNs / FCM)"]
    N -.->|送信済み event_id| R[(Redis)]
    N -.->|上限超えの失敗| DLQ["order-events.notification.dlq"]
```

---

## 1. メッセージキー:`order_id`

Kafka が順序を保証するのは **同じパーティションの中だけ**。パーティションは `hash(key) % パーティション数` で決まるので、キーが同じなら必ず同じパーティションに入る。

```mermaid
flowchart LR
    subgraph 注文A
        A1[CREATED] --> A2[ACCEPTED] --> A3[CANCELLED]
    end
    subgraph 注文B
        B1[CREATED] --> B2[ACCEPTED]
    end

    注文A -->|"hash(order_A) % 40"| PX["P7:A1 → A2 → A3 の順で並ぶ"]
    注文B -->|"hash(order_B) % 40"| PY["P23:B1 → B2 の順で並ぶ"]
```

同じ注文のイベントは1つのパーティションに発生順で並ぶ。違う注文は別々のパーティションに散らばるので、負荷も分散する。

### キーなしだと順序が壊れる

キーなしだと、同じ注文のイベントが別々のパーティションに入る。パーティションごとに処理の進み具合が違うので、後に発生したイベントが先に処理されうる。

```mermaid
sequenceDiagram
    participant Prod as 注文サービス
    participant P3 as P3(混んでいる)
    participant P9 as P9(空いている)
    participant C as 配達割当サービス

    Prod->>P3: ACCEPTED
    Prod->>P9: CANCELLED
    P9->>C: CANCELLED を先に処理
    P3->>C: ACCEPTED を後から処理
    Note over C: キャンセル済みの注文に<br/>配達員を割り当ててしまう
```

### `user_id` / `store_id` だと偏る

順序は守られるが、まとめる単位が大きすぎる。注文の多いユーザーや人気店のイベントが1つのパーティションに集中する(ホットパーティション)。

```mermaid
flowchart LR
    S1["人気チェーン店<br/>(ランチ時に大量)"] -->|"key = store_id"| HOT["P5:詰まる"]
    S2[小さな店] -->|"key = store_id"| P12["P12:ほぼ空"]
    S3[小さな店] -->|"key = store_id"| P30["P30:ほぼ空"]

    style HOT fill:#f99,stroke:#c00
```

| キー | 同じ注文の順序 | 問題 |
|---|---|---|
| `order_id` | 守られる | なし(採用) |
| `user_id` | 守られる | ヘビーユーザー・法人アカウントの分が偏る |
| `store_id` | 守られる | 人気店でホットパーティションになる |
| キーなし | **壊れる** | `CANCELLED` が `ACCEPTED` より先に処理される |

---

## 2. パーティション数:40(最低 30)

### 計算

```mermaid
flowchart TD
    A["ピーク注文数<br/>120 件/秒"] --> C["イベント流量<br/>120 × 5 = 600 イベント/秒"]
    B["1注文あたり<br/>5 イベント"] --> C
    D["通知の処理時間<br/>50ms/件"] --> E["1インスタンスの処理能力<br/>1 ÷ 0.05 = 20 件/秒"]
    C --> F["必要な並列数<br/>600 ÷ 20 = 30"]
    E --> F
    F --> G["並列数の上限 = パーティション数<br/>→ 最低 30 パーティション"]
    G --> H["約1.3倍の余裕<br/>→ 40 パーティション"]
```

グループ内では1パーティションを1インスタンスしか担当できないので、**並列数の上限 = パーティション数**。だから必要な並列数がそのまま最低パーティション数になる。

### なぜ 30 ちょうどではダメか

| パーティション数 | 1パーティションあたり | 稼働率 | 状態 |
|---|---|---|---|
| 30 | 20 件/秒 | 100% | 少しでも遅れるとラグが増え続ける |
| 40 | 15 件/秒 | 75% | 25% の余力で一時的なラグを解消できる |

余裕が必要な理由は3つ。

- 50ms は平均値で、外部APIが遅くなることがある
- `hash(order_id) % N` は完全には均等にならない
- パーティション数を後から増やすと `order_id` の割り当て先が変わり、切り替え前後で順序が崩れうる。だから最初に多めに取る

---

## 3. コンシューマグループ:サービスごとに分ける

### ルール

- **同じグループ** の中では、1件のイベントはどれか1インスタンスにしか届かない(分担)
- **違うグループ** は、それぞれ独立したオフセットでトピックを全部読む(全員が全件受け取る)

### 1グループにまとめた場合(NG)

```mermaid
flowchart LR
    subgraph T[order-events]
        P0[P0]
        P1[P1]
        P2[P2]
    end
    subgraph G["1つのグループに3サービス"]
        N[通知]
        D[配達割当]
        S[売上集計]
    end
    P0 --> N
    P1 --> D
    P2 --> S
```

P0 のイベントは通知サービスにしか届かず、配達割当・売上集計は受け取れない。「それぞれが全イベントを受け取る」という要件を満たせない。

### サービスごとに分けた場合(採用)

```mermaid
flowchart LR
    subgraph T[order-events]
        P0[P0]
        P1[P1]
        P2[P2]
    end
    subgraph G1[notification-service]
        N0[通知 #0]
        N1[通知 #1]
        N2[通知 #2]
    end
    subgraph G2[delivery-assignment-service]
        D0[配達割当 #0]
    end
    P0 --> N0
    P1 --> N1
    P2 --> N2
    P0 --> D0
    P1 --> D0
    P2 --> D0
```

(売上集計グループも同様。図では省略)

各グループが独立したオフセットを持つので、通知サービスが外部APIの遅れでラグをためても、他のサービスには影響しない。スケールやデプロイもサービスごとにできる。

| グループ | インスタンス数 | 理由 |
|---|---|---|
| `notification-service` | 40 | パーティション数と同じ。最低でも 30 台必要 |
| `delivery-assignment-service` | 3 程度 | 処理が速いので、可用性のために複数あれば十分 |
| `sales-aggregation-service` | 2〜3 | 同上 |

### インスタンスをパーティション数より多くすると

```mermaid
flowchart LR
    subgraph T["order-events(40 パーティション)"]
        P0[P0]
        Pd[...]
        P39[P39]
    end
    subgraph G["notification-service(50 インスタンス)"]
        I0["#0"]
        Id[...]
        I39["#39"]
        I40["#40〜#49<br/>割り当てなし"]
    end
    P0 --> I0
    Pd --> Id
    P39 --> I39

    style I40 fill:#ddd,stroke:#999,stroke-dasharray: 5 5
```

1パーティションを同時に担当できるのは1インスタンスだけなので、余った 10 台は何もしない。処理能力は 40 台のときと変わらない。並列度をもっと上げたいなら、パーティションを増やす必要がある。

---

## 4. オフセットコミット:処理の後に手動コミット

### 処理の前にコミット → 取りこぼし(at-most-once)

```mermaid
sequenceDiagram
    participant K as Kafka
    participant C1 as 通知 #1
    participant C2 as 通知 #2(引き継ぎ)
    participant API as 外部API

    K->>C1: offset 100 を受信
    C1->>K: offset 100 をコミット
    Note over C1: ここで落ちる
    K->>C2: offset 101 から再開
    Note over API: offset 100 の通知は<br/>一度も送られない
```

### 処理の後にコミット → 重複(at-least-once)

```mermaid
sequenceDiagram
    participant K as Kafka
    participant C1 as 通知 #1
    participant C2 as 通知 #2(引き継ぎ)
    participant API as 外部API

    K->>C1: offset 100 を受信
    C1->>API: 通知を送信
    Note over C1: コミット前に落ちる
    K->>C2: offset 100 から再開
    C2->>API: 同じ通知をもう一度送信
    C2->>K: offset 100 をコミット
    Note over API: 通知が2回届く
```

要件は「取りこぼし厳禁」「重複はなるべく避けたい」。取りこぼしは後から取り戻せないので、**処理の後にコミット**を選ぶ。自動コミット(`enable.auto.commit=true`)は処理の完了を待たずにコミットするので切る。

### 重複をゼロにできない理由

外部APIへの送信と、自社側の記録(コミットや Redis への書き込み)は1つのトランザクションにできない。そのため「送信した直後・記録する前」に落ちると、送ったという事実がどこにも残らない。外部APIは冪等キーに対応しておらず変更もできないので、この1件の重複は原理的に残る。

### 重複を減らす方法

```mermaid
flowchart TD
    A[イベント受信] --> B{"Redis に event_id がある?"}
    B -->|ある| SKIP[送らずにスキップ]
    B -->|ない| C[外部APIに送信]
    C --> D["Redis に event_id を記録<br/>(TTL 7日)"]
    D --> E[オフセットをコミット]
    SKIP --> E
```

| 方法 | 効く場面 |
|---|---|
| グレースフルシャットダウン | デプロイ時(本命)。処理中の1件を終わらせ、コミットしてから止まる |
| コミット間隔を短くする | 落ちたときに読み直す件数を減らす |
| `event_id` を Redis に記録 | コミットを数十件ごとにまとめる場合や、コミット失敗時の読み直し |
| `apns-collapse-id` / `collapse_key` | 補助。端末上で同じ通知を1件にまとめて見せる |

デプロイ時のグレースフルシャットダウンの流れは次のとおり。計画的な停止なら「送信後・コミット前」で落ちる状況そのものが起きない。

```mermaid
sequenceDiagram
    participant Deploy as デプロイ
    participant C as 通知インスタンス
    participant API as 外部API
    participant K as Kafka

    Deploy->>C: 停止シグナル
    C->>C: 新しいイベントの取得をやめる
    C->>API: 処理中のイベントを送り終える
    C->>K: オフセットをコミット
    C->>K: グループから抜ける
    Note over K: 別インスタンスへリバランス<br/>(続きから読むので重複なし)
```

---

## 5. 失敗し続けるイベント:リトライ上限 → DLQ

### 何が起きるか(head-of-line blocking)

```mermaid
flowchart LR
    subgraph P7[パーティション P7]
        direction LR
        E1["注文A: ACCEPTED<br/>✕ 失敗し続ける"] --- E2["注文A: PICKED_UP"] --- E3["注文X: CREATED"] --- E4["注文Y: ACCEPTED"] --- E5[...]
    end
    E1 -.->|ここで止まる| STOP["後続はすべて待ち<br/>7日後には保持期間切れで消える"]

    style E1 fill:#f99,stroke:#c00
    style STOP fill:#fdd,stroke:#c00
```

止まるのは同じ注文のイベントだけではなく、**同じパーティションに入っている他の注文のイベントもすべて**。放置すると保持期間切れで、設問4で避けたはずの取りこぼしになる。再起動しても同じイベントで失敗するだけなので解決しない。

### 対処の流れ

```mermaid
flowchart TD
    A[イベントを送信] --> B{成功?}
    B -->|成功| OK[コミットして次へ]
    B -->|失敗| C{"API 全体が落ちている?<br/>(どのイベントも 5xx・タイムアウト)"}
    C -->|はい| CB["サーキットブレーカーで一時停止<br/>コミットせずに待つ"]
    CB -->|API 復旧| A
    C -->|"いいえ(このイベントだけ)"| D{"リトライしても直らないエラー?<br/>(無効トークンなど 4xx)"}
    D -->|はい| DLQ
    D -->|いいえ| E{リトライ上限に達した?}
    E -->|まだ| W[待ち時間を伸ばして再試行] --> A
    E -->|達した| DLQ["DLQ トピックに書き込む<br/>(エラー内容つき)"]
    DLQ --> F[書き込み成功後にコミットして次へ]
    F --> M["DLQ を監視・アラート<br/>原因を直して再送 or 破棄"]
```

ポイントは2つ。

- **DLQ への書き込みが成功してからコミットする**。順番を逆にすると、DLQ に書く前に落ちたときにイベントが消える
- **DLQ が効くのはイベント固有の失敗だけ**。API 全体が落ちているときに全部 DLQ に流すと、DLQ が本流の代わりになるだけ。その場合はサーキットブレーカーで止めて待てば、Kafka に残っているイベントを復旧後に続きから処理できる

### (参考)順序を厳密に守りたい場合

B を DLQ に移すと、その注文の通知は `A → B → C` ではなく `A → C` になる。通知なら許容できるが、配達割当サービスのように状態を持つ処理では、B を飛ばして C を処理すると状態が壊れうる。その場合は失敗した `order_id` を保留として記録し、同じ `order_id` の後続イベントも DLQ(または保留用の場所)に回す。

```mermaid
flowchart LR
    B["注文A: B が失敗"] --> H["order_id = A を保留に登録"]
    C["注文A: C が到着"] --> Q{"order_id が保留中?"}
    Q -->|はい| DLQ[DLQ / 保留へ]
    Q -->|いいえ| PROC[通常どおり処理]
    X["注文X: 到着"] --> Q
```

こうすると、止まるのは注文A だけで、他の注文の処理は続けられ、注文A の中の順序も守られる。
