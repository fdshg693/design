# ネットワークセキュリティ(ファイアウォール・Private Endpoint)

調査日: 2026-10-23

## ストレージファイアウォール(ネットワーク規則)

- ファイアウォール規則は **パブリックエンドポイント** へのアクセスを制御する。既定ではすべてのネットワークからの接続を許可する
- 規則は4種類。規則を設定すると、明示的に許可した送信元だけがパブリックエンドポイント経由でアクセスでき、それ以外は拒否される
    - **仮想ネットワーク規則**: 特定サブネットからの通信を許可。最大 400 個/アカウント。サブネット側でサービスエンドポイントを有効にする必要がある
        - `Microsoft.Storage`: VNet と **同じリージョン** のアカウントに接続
        - `Microsoft.Storage.Global`: 任意のリージョンのアカウントに接続
        - 1サブネットに付けられるのはどちらか一方だけ
    - **IP 規則**: パブリック IP の範囲を許可。最大 400 個/アカウント
    - **リソースインスタンス規則**: VNet や IP で分離できない Azure リソースのインスタンスを許可。ストレージアカウントと同じテナントのリソースに限る。何ができるかはそのインスタンスのロール割り当てで決まる
    - **信頼されたサービスの例外**: ネットワーク境界の外で動く特定の Azure サービスを許可する
- 許可された送信元からの要求も、別途認可(後述の RBAC / SAS / キー)の要件を満たす必要がある
- サービスエンドポイントを有効にしたサブネットからの通信は、送信元がプライベート IP になる。そのため、そのサブネットを IP 規則で許可しても効果はない
- SAS に IP 制限を付けても、ネットワーク規則を超えたアクセスを与えるわけではない
- オンプレからは IP 規則で許可する。ExpressRoute(Microsoft ピアリング)の場合は NAT 後のパブリック IP を許可する
- 出典: https://learn.microsoft.com/azure/storage/common/storage-network-security

### 制限・注意点

- ファイアウォール規則は **データプレーン** の操作にだけ適用される。コントロールプレーンの操作は対象外
    - コンテナー一覧などはコントロールプレーン経由でも実行できるので、ポータルでは成功することがある。Storage Explorer などから BLOB データにアクセスする操作はファイアウォールの制御を受ける
- REST・SMB を含むすべてのプロトコルに適用される。VM ディスクのトラフィックには影響しない
- 規則に含まれるサブネットを削除すると規則からも消える。同名のサブネットを作り直しても自動では許可されない
- 信頼されたサービスからのアクセスは、他のネットワーク制限より **優先** される。「選択したネットワーク」から「無効」に切り替えても、設定済みのリソースインスタンス規則や例外(信頼されたサービスの許可を含む)は有効なまま残る
- テンプレートで `publicNetworkAccess` を `Disabled` にしても `defaultAction` が `Allow` のまま残ることがある(`publicNetworkAccess` が優先されるが、Defender 等は `defaultAction` を見て警告する)
- IP 規則の制限
    - パブリック IP のみ。RFC 1918 のプライベート範囲(10.x、172.16〜31.x、192.168.x)は指定できない
    - `/31`・`/32` の範囲指定は不可(個別 IP として指定する)。IPv4 のみ
    - **ストレージアカウントと同じリージョンから来る要求には効かない**(同一リージョンの Azure サービスはプライベートな Azure IP で通信するため)。同一リージョンは仮想ネットワーク規則で許可する
    - サービスエンドポイントを有効にしたペアリージョンの VNet のクライアントも、IP 規則では制御できない
- 出典: https://learn.microsoft.com/azure/storage/common/storage-network-security-limitations

### 信頼されたサービス

- 同じテナントに登録されたリソースとして許可されるもの(例): Azure Backup、Event Grid(BLOB イベント発行、Storage Queue への配信)、Event Hubs Capture、Azure Monitor(リソースログ等の書き込み)、Network Watcher(フローログ)、Site Recovery など
- マネージド ID ベースで許可されるもの(例): API Management、AI Search、Foundry Tools など。インスタンスに適切な権限が必要
- 出典: https://learn.microsoft.com/azure/storage/common/storage-network-security-trusted-azure-services

## Private Endpoint

- VNet 内に、ストレージのサービスごとに別のプライベート IP を持つネットワークインターフェイスを作る。通信は VNet と Microsoft バックボーン上の Private Link を通る
- GPv1 アカウントでは使えない
- Private Endpoint を作っても、パブリックエンドポイントは **自動では閉じない**。閉じるにはファイアウォールを別途設定する
- ストレージファイアウォールはパブリックエンドポイントだけを制御するので、Private Endpoint のある VNet からの通信に許可規則は不要。代わりに **承認(consent)フロー** で接続を許可する(作成者がアカウントの所有者なら自動承認)
- Private Endpoint が構成されていれば、パブリックネットワークアクセスが無効でも、関連する VNet からの通信は許可される
- **サブリソースごとに** 別の Private Endpoint が必要: `blob` / `dfs` / `file` / `queue` / `table` / `web`
    - Data Lake(`dfs`)を作るなら `blob` も作る(dfs 向けの操作が blob にリダイレクトされることがある)。逆に blob だけだと ACL 管理・ディレクトリ作成などが失敗する
    - RA-GRS でセカンダリを読むには、セカンダリ用の Private Endpoint も別に作る(フェイルオーバー用には不要)
- 接続文字列は **パブリックと同じもの** を使う。`privatelink` サブドメインの URL で接続しない
- サービスエンドポイントを使うサブネットにも Private Endpoint を作れる
- アカウント間で BLOB をコピーするときは、クライアントが両方のアカウントにネットワーク的に到達できる必要がある
- 出典: https://learn.microsoft.com/azure/storage/common/storage-private-endpoints

### DNS

- Private Endpoint を作ると、`<account>.blob.core.windows.net` の CNAME が `<account>.privatelink.blob.core.windows.net` を向くようになる
- VNet の外から引くと、`privatelink` 名がさらにパブリックエンドポイントへ CNAME され、パブリック IP が返る
- Private DNS ゾーン(`privatelink.blob.core.windows.net` 等)がリンクされた VNet から引くと、`privatelink` 名の A レコードでプライベート IP が返る
- カスタム DNS / オンプレ DNS を使う場合、`privatelink` サブドメインを Private DNS ゾーンへ委任(転送)するか、自前の DNS に A レコードを登録する

| サービス | サブリソース | ゾーン名 |
| --- | --- | --- |
| Blob | `blob` | `privatelink.blob.core.windows.net` |
| Data Lake | `dfs` | `privatelink.dfs.core.windows.net` |
| File | `file` | `privatelink.file.core.windows.net` |
| Queue | `queue` | `privatelink.queue.core.windows.net` |
| Table | `table` | `privatelink.table.core.windows.net` |
| 静的 Web サイト | `web` | `privatelink.web.core.windows.net` |

- 既知の制約: VNet N1 に A1 の blob 用 Private Endpoint があり、別アカウント A2 も(別 VNet で)blob 用 Private Endpoint を持つ場合、N1 のクライアントは A2 にも Private Endpoint 経由でアクセスする必要がある(DNS の変更による)
- 出典: https://learn.microsoft.com/azure/storage/common/storage-private-endpoints#dns-changes-for-private-endpoints
