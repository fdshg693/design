---
summary: Slack のようなチャンネル型リアルタイムチャットを Azure 上に設計する
topic: [system, db, api, infra]
status: 要件定義
---

# リアルタイムチャット(Slack ライク)

ワークスペース・チャンネル単位でメッセージをリアルタイムにやり取りするチャットサービス。

## 主な学習テーマ

- WebSocket 接続のスケールアウト(接続管理とファンアウト)
- メッセージの順序保証・重複排除・既読管理
- プレゼンス(オンライン状態)・入力中表示
- オフライン時の差分同期とプッシュ通知
- マルチリージョンでのデータ配置と整合性

## 想定 Azure サービス(候補)

Azure Web PubSub / SignalR Service, Cosmos DB(Change Feed), Azure Cache for Redis, Service Bus, Notification Hubs, Front Door, Container Apps

## 進捗

- [x] 要件定義(ドラフト) → [design/01-requirements.md](design/01-requirements.md)
- [ ] 規模見積もり
- [ ] 全体構成
- [ ] API / データモデル
- [ ] 深掘り

## スコープ外

- 音声・ビデオ通話(メディアサーバー設計は別領域のため)
- 共同編集(CRDT/OT)は深掘りの候補として保留し、初期スコープからは外す
- エンドツーエンド暗号化(鍵管理が主題になり、チャットの分散設計から外れるため)
