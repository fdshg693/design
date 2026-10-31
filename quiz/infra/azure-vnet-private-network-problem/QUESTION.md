---
summary: 社内業務Webアプリ(App Service + Azure SQL + Storage)を、VNet・Subnet設計とPrivate Endpointで閉域化する
topic: infra
level: 初級
---

# 問題:Azure VNet・Subnet設計と閉域化(初級)

- 回答: `answer\infra\azure-vnet-private-network-problem.md`

## 背景

ある企業の社内向け経費精算システムを Azure に構築する。
構成は次のとおりで、現状はすべてのPaaSがパブリックエンドポイントのまま公開されている。セキュリティ監査で「データ層がインターネットから到達可能な状態は不可」と指摘を受けた。

- Web アプリ: Azure App Service (Premium v3)
- データベース: Azure SQL Database
- 添付ファイル保管: Azure Storage (Blob)
- 利用者: 社内ユーザーのみ(オンプレ拠点から VPN 経由で接続。VPN は Azure の VPN Gateway で終端)
- 一部の運用担当者が、踏み台VM経由でDBを直接操作する

## 要件

- Azure SQL と Storage には**インターネットから到達できない**こと(パブリックネットワークアクセスを無効化する)
- App Service から Azure SQL / Storage へは、Azure 内の**プライベートIP経由**で通信すること
- オンプレ拠点の利用者は、VPN 経由で App Service にアクセスできること(App Service もインターネット公開しない)
- App Service からの外向き通信(アウトバウンド)も、VNet 経由で制御できること
- 環境は本番・開発の2つ。将来、他システムのVNetとも接続する可能性がある
- オンプレのネットワークは `10.0.0.0/8` のうち `10.0.0.0/16` を既に使用している

## 設問

1. VNet のアドレス空間と Subnet 分割を設計せよ(CIDR を具体的に示すこと。Subnet の用途ごとの分け方、予約アドレスやサイズの考慮点、オンプレ・他VNetとの重複を避ける理由を含む)
2. Subnet ごとに NSG を設定する場合、どのような基本ルールを入れるか(最低限、インバウンド/アウトバウンドの方針を表形式などで示せ)
3. Azure SQL / Storage を閉域化する方法を述べよ。**サービスエンドポイントと Private Endpoint の違い**を比較し、今回どちらを選ぶか理由とともに答えよ
4. Private Endpoint を使うとき、名前解決はどうなるか(Private DNS Zone の役割、`privatelink` 付きのゾーン名、VNet リンクが必要な理由)
5. App Service を VNet と接続する2つの方向(インバウンド/アウトバウンド)を整理せよ(VNet 統合と Private Endpoint の違い、それぞれ何のために使うか)
6. オンプレからのアクセス経路を説明せよ(VPN Gateway の置き場所となる Subnet、オンプレから Private Endpoint の名前を引くための DNS の考慮点)
7. 閉域化した後に起きがちなトラブルを2つ以上挙げ、原因の切り分け方を述べよ(例:接続できない、名前が解決されない)

## ヒント

- Subnet のサイズを決めるとき、Azure が各 Subnet で予約するアドレス数は何個か
- VPN Gateway を置く Subnet には、決まった名前がある
- VNet 統合用 Subnet は、他のリソースと共用してよいか
- サービスエンドポイントでは、アクセス先のIPアドレスはパブリックのままか、プライベートか
- Private Endpoint を作っただけでは、アプリの接続先ホスト名は自動でプライベートIPに向くか
- 「パブリックネットワークアクセスを無効化」しただけで、App Service からの通信はどうなるか
