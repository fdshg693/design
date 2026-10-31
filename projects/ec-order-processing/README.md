---
summary: EC サイトの注文〜決済〜在庫引当〜出荷をイベント駆動のマイクロサービスとして Azure 上に設計する
topic: [system, db, api, infra]
status: 要件定義
---

# EC 注文処理(イベント駆動マイクロサービス)

EC サイトの注文確定から決済・在庫引当・出荷指示までを、サービス間のイベント連携で処理するバックエンド。

## 主な学習テーマ

- Saga パターン(オーケストレーション / コレオグラフィ)と補償トランザクション
- Transactional Outbox、冪等性、重複・順序の扱い
- 結果整合性と、ユーザーへの見せ方
- メッセージング基盤の使い分け(Service Bus / Event Grid / Event Hubs)
- セール時のスパイク対策(在庫の過剰販売防止)

## 想定 Azure サービス(候補)

Service Bus, Event Grid, Event Hubs, Container Apps(Dapr) / AKS, Azure SQL Database, Cosmos DB, Azure Cache for Redis, API Management, Durable Functions

## 進捗

- [x] 要件定義(ドラフト) → [design/01-requirements.md](design/01-requirements.md)
- [ ] 規模見積もり
- [ ] 全体構成
- [ ] API / データモデル
- [ ] 深掘り

## スコープ外

- 商品検索・レコメンド・カート(注文確定以降の処理に集中するため)
- 決済代行サービス内部の設計(外部 API として扱う)
- 倉庫管理システム(WMS)の内部(出荷指示を受け取る外部システムとして扱う)
