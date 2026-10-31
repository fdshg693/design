---
summary: ホームタイムラインの base 設計を AWS(DynamoDB + Streams / Lambda / ElastiCache for Valkey / ECS)で具体化し、二重書き込みの回避・クラスタモードの制約・メモリと転送料の見積もりを学ぶ
topic: system
variant: aws
level: 中級
status: 未読
---

# ホームタイムライン: AWS 版

[base](../base/README.md) の設計を AWS のマネージドサービスで具体化したもの。

## base との違い

- 追加・変更した要件: なし
- 具体化した対象
    - ロードバランサ → ALB
    - API サーバ → ECS on Fargate(3 AZ)
    - 投稿ストア → DynamoDB `posts`(+ プロフィール用 GSI)
    - フォロー関係 → DynamoDB `follows`(+ フォロワー用 GSI)と `users`
    - Redis → ElastiCache for Valkey(ノードベース、クラスタモード有効)
    - キュー + fan-out ワーカー → **DynamoDB Streams + Lambda**(キューを置かない)
- base の前提(要件・規模・スコープ外)は、ここに書いたもの以外そのまま引き継ぐ
- リージョンは単一(料金の試算は us-east-1 の単価)

## スコープ外

- IaC(CDK / Terraform)のコード: 構成と設定値の理解が主題のため
- 認証(Cognito など)・WAF: 別トピックとして扱う
- 監視(CloudWatch のアラーム設計): 必要なら質問で扱う

## 読み方

1. [base の DESIGN.md](../base/DESIGN.md) を読んでいる前提
2. [DESIGN.md](DESIGN.md) を読む
3. 分からないことをそのまま質問する(浮かばなければ [QUESTIONS.md](QUESTIONS.md) から選ぶ)
4. 回答は [QA.md](QA.md) に溜まっていく

## 進捗

- 質問集: 0 / 18 問
- 自由質問: 0 件

## 関連

- [base](../base/README.md)
- [url-shortener の AWS 版](../../url-shortener/aws/README.md): DynamoDB・ElastiCache・SQS + Lambda の基本と AZ 配置はこちらで扱った
