---
summary: 社内ドキュメントを根拠に回答する生成 AI チャット(RAG)を Azure 上に設計する
topic: [system, db, api, infra, security]
status: 要件定義
---

# 社内ドキュメント RAG チャット

社員が自然言語で質問すると、社内ドキュメント(規程・手順書・設計書など)を検索し、根拠付きで回答するチャットサービス。

## 主な学習テーマ

- RAG パイプライン(取り込み → チャンク分割 → 埋め込み → 検索 → 生成)
- ハイブリッド検索(ベクトル + キーワード)とリランキング
- ドキュメント単位のアクセス制御(権限トリミング)
- LLM のコスト・レイテンシ・レート制限(TPM)を踏まえた設計
- 閉域ネットワーク(Private Endpoint)での構成

## 想定 Azure サービス(候補)

Azure OpenAI / AI Foundry, Azure AI Search, Blob Storage, Functions, Container Apps, Cosmos DB, Entra ID, API Management

## 進捗

- [x] 要件定義(ドラフト) → [design/01-requirements.md](design/01-requirements.md)
- [ ] 規模見積もり
- [ ] 全体構成
- [ ] API / データモデル
- [ ] 深掘り

## スコープ外

- モデルのファインチューニング・独自モデル学習(RAG の設計に集中するため)
- 画像・動画など非テキストの理解(テキスト抽出可能な文書に限定して簡略化)
- フロントエンド UI の詳細設計
