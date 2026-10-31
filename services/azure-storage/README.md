---
summary: Blob / Files / Queue / Table / Data Lake をまとめて提供するストレージアカウント。ネットワーク制御と認可の層が多い
category: ストレージ
status: 着手
---

# Azure Storage(ストレージアカウント)

## 学習の進め方

1. `scenarios/` のシナリオを順番に解く(`回答` 欄に書く)
2. AI が `レビュー` を書き、学んだことを `ポイント` にまとめる
3. 機能マップの未着手の機能や、出てきた疑問から次のシナリオを作る

## 最初に押さえる: 「ACL」は2種類ある

Azure Storage で「ACL」と言うと、まったく別の2つを指すことがある。混ざると理解が崩れるので、シナリオも分けている。

| 呼び方 | 正体 | 何を制御するか | シナリオ |
| --- | --- | --- | --- |
| ネットワーク ACL(`networkAcls`、ストレージファイアウォール) | ARM のプロパティ名が `networkAcls`。仮想ネットワーク規則 / IP 規則 / リソースインスタンス規則 / 信頼されたサービスの例外 | **どこから来た通信を** パブリックエンドポイントで受け付けるか | [01](scenarios/01-private-endpoint-lockdown.md) |
| Data Lake の ACL(POSIX ライク ACL) | 階層型名前空間(HNS)を有効にしたアカウントで、ディレクトリ・ファイルごとに付ける `rwx` | **誰が** どのディレクトリ・ファイルに何をできるか | [02](scenarios/02-data-lake-acl.md) |

さらにその上下に、Private Endpoint(経路)・DNS(名前解決)・RBAC / SAS / アカウントキー(認可)が重なる。通信は「名前解決 → 経路 → ネットワーク規則 → 認証・認可」の順に関門を通る、と考えると切り分けやすい。

## シナリオ一覧

| # | シナリオ | 機能 | 種類 | レベル | 状態 |
| --- | --- | --- | --- | --- | --- |
| 01 | [閉域化したら一部だけつながらない](scenarios/01-private-endpoint-lockdown.md) | private-endpoint, storage-firewall, private-dns | troubleshoot | 中級 | 出題済 |
| 02 | [分析基盤のフォルダ単位アクセス制御](scenarios/02-data-lake-acl.md) | data-lake-acl, rbac, shared-key | design | 中級 | 出題済 |

## 機能マップ

### ネットワーク

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| パブリックネットワークアクセス | `Enabled` / 選択したネットワークのみ / `Disabled`、`defaultAction` との関係 | [01](scenarios/01-private-endpoint-lockdown.md) |
| 仮想ネットワーク規則 + サービスエンドポイント | サブネット単位の許可、宛先はパブリック IP のまま、同一リージョン / `Storage.Global` | [01](scenarios/01-private-endpoint-lockdown.md) |
| IP 規則 | パブリック IP のみ、同一リージョンからの通信には効かない | [01](scenarios/01-private-endpoint-lockdown.md) |
| リソースインスタンス規則 / 信頼されたサービスの例外 | VNet に入れられない Azure サービスをどう通すか | [01](scenarios/01-private-endpoint-lockdown.md) |
| Private Endpoint | サブリソース(blob / dfs / file / queue / table / web)ごとに必要、承認フロー、ファイアウォールの対象外 | [01](scenarios/01-private-endpoint-lockdown.md) |
| Private DNS ゾーン / カスタム DNS | `privatelink.*` の CNAME、VNet リンク、オンプレ・ピアリング先からの名前解決 | [01](scenarios/01-private-endpoint-lockdown.md) |
| コントロールプレーンとデータプレーン | ファイアウォールはデータプレーンだけ。ポータルで「見えるのに開けない」 | [01](scenarios/01-private-endpoint-lockdown.md) |
| ネットワークセキュリティ境界(NSP) | `SecuredByPerimeter`、PaaS 同士の境界 | - |

### 認証・認可

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| アカウントキー(Shared Key) | 全権限、ACL・RBAC が効かない、`allowSharedKeyAccess` で無効化 | [02](scenarios/02-data-lake-acl.md) |
| SAS(アカウント / サービス / ユーザー委任) | 有効期限、保存されたアクセスポリシーでの失効、ユーザー委任 SAS と ACL | [02](scenarios/02-data-lake-acl.md)(一部) |
| Entra ID + RBAC | データアクション(`Storage Blob Data *`)と管理アクションの違い、スコープ(アカウント / コンテナー) | [02](scenarios/02-data-lake-acl.md) |
| ABAC(ロール割り当て条件) | パスやタグで RBAC を絞る | - |
| Data Lake の ACL | アクセス ACL / 既定 ACL、Execute の意味、既存の子に反映されない、評価順(RBAC が先) | [02](scenarios/02-data-lake-acl.md) |
| 匿名アクセス(パブリック BLOB) | `allowBlobPublicAccess`、コンテナーのアクセスレベル | - |

### データ管理・運用

| 機能 | 論点 | シナリオ |
| --- | --- | --- |
| アカウントの種類 / パフォーマンス | Standard GPv2 / Premium(BlockBlob, FileStorage) | - |
| アクセス層 | Hot / Cool / Cold / Archive、リハイドレート、早期削除 | - |
| ライフサイクル管理 | 層の自動移動・削除 | - |
| データ保護 | 論理削除、バージョン管理、ポイントインタイムリストア、不変ストレージ(WORM) | - |
| 冗長性 | LRS / ZRS / GRS / GZRS / RA-*、フェイルオーバー | - |
| 暗号化 | Microsoft 管理キー / CMK、インフラ暗号化 | - |
| 監視 | 診断ログ、メトリクス、Defender for Storage | - |
| 性能・制限 | アカウント / BLOB ごとのスケール目標、パーティション、503 | - |

## 似たサービス・競合サービス

| サービス | 一言でいうと | 比較シナリオ |
| --- | --- | --- |
| [Azure Storage Queue](../azure-storage-queue/README.md) | このストレージアカウントの Queue サービス。ネットワーク・認可の仕組みは共通 | - |
| Azure NetApp Files | 高性能な NFS / SMB ファイル共有 | - |
| Amazon S3 | AWS のオブジェクトストレージ。バケットポリシー、VPC エンドポイント(Gateway / Interface) | - |
| Google Cloud Storage | GCP のオブジェクトストレージ。IAM、VPC Service Controls | - |

## 調査結果(resource)

- [ネットワークセキュリティ(ファイアウォール・Private Endpoint)](resource/network-security.md)
- [Data Lake のアクセス制御(RBAC と ACL)](resource/data-lake-access-control.md)

## 関連

- [quiz/infra/azure-vnet-private-network-problem](../../quiz/infra/azure-vnet-private-network-problem/QUESTION.md)(VNet 設計の中で Private Endpoint を扱う。こちらは Storage 側の挙動に絞る)
- [projects/internal-rag-chat](../../projects/internal-rag-chat/README.md)
