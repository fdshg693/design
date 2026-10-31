---
summary: Web クローラの base 設計を AWS(SQS FIFO / ElastiCache for Valkey の Bloom filter / S3 / ECS on Fargate / Lambda)で具体化し、FIFO のメッセージグループで礼儀を守る方法とその制約・料金を学ぶ
topic: system
variant: aws
level: 中級
status: 未読
---

# Web クローラ: AWS 版

[base](../base/README.md) の設計を AWS のマネージドサービスで具体化したもの。

## base との違い

- 追加・変更した要件: なし
- 具体化した対象
    - URL フロンティア(ドメインハッシュで 32 分割 × 高優先/低優先) → **SQS FIFO キュー 2 本**(`MessageGroupId` = ホスト)。パーティション分割とワーカーの専有をやめた
    - 礼儀の時計(ワーカーのメモリの `next_allowed_at`) → FIFO のグループ単位の受信制御 + Valkey の `SET NX PX 1000`
    - Bloom filter(共有のビット配列) → ElastiCache Serverless for Valkey 8.1 の Bloom filter(16 キーに分割)
    - オブジェクトストレージ → S3 Standard
    - 取得ワーカー → ECS on Fargate(2 AZ、パブリックサブネット)
    - 7 日バケット + 日次ジョブ → S3 の分単位ファイル + **5 分ごと**の Lambda(EventBridge Scheduler)
- 追加した仕組み: 1 ドメインあたりキューに置く URL を 500 件までにする上限。FIFO キューの制約に対応するため(→ Q09)
- base の前提(要件・規模・スコープ外)は、ここに書いたもの以外そのまま引き継ぐ
- リージョンは単一(料金の試算は us-east-1 の単価)

## スコープ外

- IaC(CDK / Terraform)のコード: 構成と設定値の理解が主題のため
- 監視(CloudWatch のダッシュボード・アラーム設計): 必要なら質問で扱う
- 送信元 IP の管理(固定 IP、IP レピュテーション): クロール先との関係の話で、AWS の構成とは別の話題のため

## 読み方

1. [base の DESIGN.md](../base/DESIGN.md) を読んでいる前提
2. [DESIGN.md](DESIGN.md) を読む
3. 分からないことをそのまま質問する(浮かばなければ [QUESTIONS.md](QUESTIONS.md) から選ぶ)
4. 回答は [QA.md](QA.md) に溜まっていく

## 進捗

- 質問集: 0 / 20 問
- 自由質問: 0 件

## 関連

- [base](../base/README.md)
- [URL 短縮サービス: AWS 版](../../url-shortener/aws/README.md): ElastiCache Serverless・SQS 標準キュー・Fargate の AZ 配置の説明がある
