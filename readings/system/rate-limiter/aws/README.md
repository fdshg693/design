---
summary: base のレート制限を AWS(ALB + WAF / ECS Fargate / ElastiCache Serverless for Valkey / DynamoDB)で具体化する
topic: system
variant: aws
level: 中級
status: 未読
---

# API レート制限: AWS

[base](../base/README.md) の設計を AWS のマネージドサービスで具体化したもの。

## base との違い

- 追加・変更した要件
    - 前段に IP 単位の粗い制限を足す(API キーを持たない大量通信で、Redis まで負荷を届かせないため。base Q15 の改善案の一部)
- 具体化した対象
    - ロードバランサ → ALB(+ AWS WAF のレートベースルール)
    - API サーバ → ECS on Fargate(複数 AZ)
    - Redis → ElastiCache Serverless for Valkey
    - ルール DB(RDB) → DynamoDB(オンデマンド)
- base の前提(要件・規模・スコープ外)は、ここに書いたもの以外そのまま引き継ぐ
    - 想定リージョンは東京(ap-northeast-1)。料金は公式ページの us-east-1 の例を目安として使う

## スコープ外

- API キーの発行・保存の仕組み: base と同じくスコープ外
- IaC(CDK / Terraform)の全文: 構成の理解が主題のため、設定値だけを表で示す
- マルチリージョン: base と同じ(→ Q13)

## 読み方

1. [base の DESIGN.md](../base/DESIGN.md) を読んでいる前提
2. [DESIGN.md](DESIGN.md) を読む
3. 分からないことをそのまま質問する(浮かばなければ [QUESTIONS.md](QUESTIONS.md) から選ぶ)
4. 回答は [QA.md](QA.md) に溜まっていく

## 進捗

- 質問集: 0 / 13 問
- 自由質問: 0 件

## 関連

- 外部プロバイダ側のレート制限を含む通知配信(クイズ): [queue-notification-problem](../../../../quiz/system/queue-notification-problem/QUESTION.md)
