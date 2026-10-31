---
summary: 複数チームが共有するAKSクラスタについて、ネットワーク・ID・スケーリング・アップグレード・マルチテナント分離を設計する
topic: infra
level: 中級
---

# 問題:共有AKSプラットフォームの設計(AKS中級)

- 回答: `answer\infra\aks-multi-tenant-platform-problem.md`

## 背景

ある企業で、5つのプロダクトチームが利用する社内向けコンテナ基盤を Azure Kubernetes Service (AKS) 上に構築する。
現在は各チームが個別にVMで運用しており、コスト・運用負荷・セキュリティの統制が課題になっている。

## 要件

- 対象は Web API(同期処理)と、夜間バッチ(CPU/メモリを大量消費)の2種類のワークロード
- Web API は昼間にトラフィックが 5 倍程度変動し、急なスパイクもある
- 各チームは**自分の名前空間のみ**を操作でき、他チームのリソースやSecretを参照できないこと
- アプリは Azure SQL / Key Vault / Storage に接続する。**接続文字列やクライアントシークレットをマニフェストやイメージに含めない**こと
- 外部公開するAPIは WAF 経由とし、クラスタ内のPodから社内ネットワーク(オンプレ)へは Private な経路でのみ通信する
- Kubernetes のマイナーバージョンアップを、**サービス停止なし**で四半期ごとに実施したい
- 1チームの暴走(リソース過剰消費、無限スケール)が他チームに影響しないこと
- コストは極力抑えたい(夜間バッチ用の計算資源を常時確保したくない)

## 設問

1. クラスタ構成を示せ(クラスタ数、System/User ノードプールの分け方、可用性ゾーン、ノードプールをワークロード別に分ける場合の基準)
2. ネットワーク設計を述べよ(Azure CNI / kubenet / CNI Overlay の選定理由、Ingress と WAF の構成、Private クラスタにするか、NetworkPolicy の使いどころ)
3. 各チームの分離とアクセス制御をどう実現するか(Microsoft Entra ID 連携、Kubernetes RBAC、Namespace、ResourceQuota / LimitRange)
4. Pod から Azure SQL / Key Vault へシークレットレスに接続する方法を述べよ(Workload Identity を用いた場合の認証の流れを含む)
5. スケーリング戦略を述べよ(HPA / KEDA / Cluster Autoscaler の役割分担、夜間バッチ用ノードのコスト最適化、スパイク時にPodが Pending になるのを避ける工夫)
6. 無停止でのバージョンアップ手順と、そのために必要なアプリ側・クラスタ側の設定を述べよ(surge、PodDisruptionBudget、readiness probe など)
7. 運用面の観点として、監視・ログ・イメージの取得元(ACR)・ポリシー統制(Azure Policy / Gatekeeper)をどう組み込むか

## ヒント

- 「クラスタを分ける」か「名前空間で分ける」かは、分離の強さと運用コストのトレードオフ
- System ノードプールと User ノードプールを分ける理由は何か
- Pod IP の枯渇は、CNI の選択でどう変わるか
- Workload Identity では、Kubernetes の ServiceAccount と Entra ID のどこが結びつくのか
- HPA は Pod 数を、Cluster Autoscaler は何を増減させるのか。両者はどの順で動くか
- アップグレード時にノードが drain される際、Pod はどう扱われるべきか
