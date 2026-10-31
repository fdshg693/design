---
summary: URL 短縮サービスの base 設計を AWS(DynamoDB / ElastiCache / SQS / Lambda / ECS)で具体化し、サービス固有の制約・上限・料金を学ぶ
topic: system
variant: aws
level: 中級
status: 読解中
---

# URL 短縮サービス: AWS 版

[base](../base/README.md) の設計を AWS のマネージドサービスで具体化したもの。

## base との違い

- 追加・変更した要件: なし
- 具体化した対象
    - ロードバランサ → ALB(Application Load Balancer)
    - API サーバ → ECS on Fargate(3 AZ に分散)
    - 採番 DB(RDB のシーケンス) → **DynamoDB のアトミックカウンタ**(RDB をやめた)
    - URL ストア(KV DB) → DynamoDB(オンデマンド、TTL 有効)
    - Redis → ElastiCache Serverless for Valkey
    - キュー + 集計ワーカー → SQS 標準キュー + Lambda
    - 集計 DB → DynamoDB(別テーブル)
- base の前提(要件・規模・スコープ外)は、ここに書いたもの以外そのまま引き継ぐ
- リージョンは単一(料金の試算は us-east-1 の単価。東京リージョンはやや高い)

## スコープ外

- IaC(CDK / Terraform)のコード: 構成と設定値の理解が主題のため
- WAF・Shield などのセキュリティ製品: 別トピックとして扱う
- 監視(CloudWatch のダッシュボード・アラーム設計): 必要なら質問で扱う

## 読み方

1. [base の DESIGN.md](../base/DESIGN.md) を読んでいる前提
2. [DESIGN.md](DESIGN.md) を読む
3. 分からないことをそのまま質問する(浮かばなければ [QUESTIONS.md](QUESTIONS.md) から選ぶ)
4. 回答は [QA.md](QA.md) に溜まっていく

## 進捗

- 質問集: 0 / 20 問
- 自由質問: 1 件

## 関連

- [base](../base/README.md)
