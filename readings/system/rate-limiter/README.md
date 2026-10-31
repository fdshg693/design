---
summary: API キーごとにリクエスト数を制限し、超過分は 429 で返すサービス
topic: system
---

# API レート制限

API キーごとに「一定時間あたり何回まで」を判定し、超えたリクエストは通さない。

## バリアント

まず `base/` を読み、その後に興味のあるバリアントへ進む。

| フォルダ | 内容 | level | status |
| --- | --- | --- | --- |
| [base](base/README.md) | 基礎となる構成(特定クラウドに依存しない) | 初級〜中級 | 未読 |
| [aws](aws/README.md) | ALB + WAF / ECS Fargate / ElastiCache Serverless for Valkey / DynamoDB で具体化 | 中級 | 未読 |
