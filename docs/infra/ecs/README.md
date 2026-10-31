---
summary: AWS のコンテナオーケストレーションサービス。コンテナを「タスク」単位で起動・維持・スケールさせる
category: infra
level: 初級〜中級(Docker コンテナの基本は理解済み)
status: 未読
---

# Amazon ECS(Elastic Container Service)

## 一言でいうと

**「コンテナを、決めた数だけ、AWS 上で動かし続けてくれるサービス」**。Kubernetes の AWS 純正・シンプル版と考えるとよい。

## 構成(サブトピック)

| フォルダ | 内容 |
| --- | --- |
| [task/](task/README.md) | ECS タスク: ECS で動く「実行の単位」。タスク定義・ライフサイクル・ネットワーク・IAM ロール |

- 今後、サービス(`service/`)、起動タイプ・Fargate(`fargate/`)などを必要に応じて追加する

## 関連

- [../../../readings/system/url-shortener/aws/DESIGN.md](../../../readings/system/url-shortener/aws/DESIGN.md): API サーバを ECS on Fargate で動かす設計
- [../../../readings/system/rate-limiter/aws/DESIGN.md](../../../readings/system/rate-limiter/aws/DESIGN.md): 同上(ステートレスな API タスクを 3 AZ に分散)
