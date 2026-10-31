# Data Lake のアクセス制御(RBAC と ACL)

調査日: 2026-10-23

前提: 階層型名前空間(HNS)が有効なストレージアカウント。HNS が無効なら ACL はなく、RBAC のルールだけが適用される。

## 認可の種類と ACL が効く範囲

- Data Lake は Azure RBAC、ABAC(ロール割り当て条件)、POSIX ライクな ACL、Shared Key、SAS をサポートする
- **Shared Key・アカウント SAS・サービス SAS** は Entra ID の ID を持たないので、RBAC・ABAC・ACL は **効かない**
    - Shared Key の呼び出し元は実質スーパーユーザー。所有者の変更や ACL の変更を含む全操作ができる
    - **ユーザー委任 SAS** は Entra 資格情報で保護されているので ACL を適用できる(省略可能なパラメーター `suoid` を使うと、そのオブジェクト ID で POSIX ACL チェックを行う)
- 出典: https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-access-control-model

## RBAC と ACL の評価順

1. 主体にロール割り当てがあるか → あれば条件(ABAC)を評価、なければ ACL を評価
2. 条件がなければアクセス許可。条件があり、すべて一致すれば許可、一致しなければ ACL を評価
3. ACL が要求されたアクセスを許可すれば許可、そうでなければ拒否

- RBAC が先に評価され、十分な権限があれば ACL は無視される。そのため **ACL で RBAC の付与を制限(拒否)することはできない**
- RBAC は粗い粒度(アカウント・コンテナー)、ACL は細かい粒度(ディレクトリ・ファイル)を想定
- ロール割り当てはサブスクリプション → リソースグループ → アカウント → コンテナーへ継承される
- 出典: https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-access-control-model#how-permissions-are-evaluated

## ACL の仕組み

- 各ファイル・ディレクトリが ACL を持つ。エントリーの主体はユーザー、グループ、サービスプリンシパル、マネージド ID
- **アクセス ACL**: そのオブジェクトへのアクセスを制御する(ファイル・ディレクトリ両方)
- **既定 ACL**: ディレクトリに付けるテンプレート。その下に **新しく作られる** 子の ACL を決める。ファイルには既定 ACL はない
- 親の既定 ACL を変えても、**既存の子** のアクセス ACL・既定 ACL は変わらない。既存の子を変えるには ACL を再帰的に追加・更新・削除する
- 権限の意味

| 権限 | ファイル | ディレクトリ |
| --- | --- | --- |
| Read (R) | ファイルの内容を読む | 一覧するには Read + Execute が必要 |
| Write (W) | 書き込み・追記 | 子を作るには Write + Execute が必要 |
| Execute (X) | Data Lake では意味なし | 子をたどる(traverse)のに必要 |

- ACL だけで(RBAC なしで)ファイルの読み書きを許可するには、コンテナーのルートからそのファイルまでの **各ディレクトリに Execute** が必要
- 例(`/Oregon/Portland/Data.txt`、ACL のみの場合)

| 操作 | `/` | `Oregon/` | `Portland/` | `Data.txt` |
| --- | --- | --- | --- | --- |
| Data.txt を読む | `--X` | `--X` | `--X` | `R--` |
| Data.txt に追記 | `--X` | `--X` | `--X` | `RW-` |
| Data.txt を削除 | `--X` | `--X` | `-WX` | `---` |
| Data.txt を作成・更新 | `--X` | `--X` | `-WX` | `---` |
| `/Oregon/` を一覧 | `--X` | `R-X` | `---` | `---` |

- ディレクトリとその中身を削除するには、親に Write + Execute、削除するディレクトリとその中の各ディレクトリに Read + Write + Execute が必要
- 出典: https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-access-control

## 所有者・評価順・マスク

- ID の評価順: スーパーユーザー → 所有ユーザー → 名前付きユーザー → 所有グループ・名前付きグループ → その他。最初に当てはまった ID の権限が使われる
- 名前付きグループはまとめて評価し、どれかが要求権限を満たせば許可
- マスクは名前付きユーザー・名前付きグループ・所有グループのエントリーの上限を決める
- 作成者が所有ユーザーになる。Shared Key / アカウント SAS / サービス SAS で作成した場合、所有者と所有グループは `$superuser`
- 新しい項目の所有グループは親ディレクトリからコピーされる
- umask は 007 固定(既定 ACL がない親の下で作るとき、other の権限はすべて外れる)
- 出典: https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-access-control

## 推奨・制限

- ACL のエントリーには **Entra のセキュリティグループ** を使う(個人やサービスプリンシパルを直接入れない)。メンバーの増減だけで済み、ACL をツリー全体に再適用しなくてよい
- 1主体のグループ所属は 200 未満を推奨(JWT の制限)
- 制限

| 仕組み | 範囲 | 上限 |
| --- | --- | --- |
| Azure RBAC | アカウント、コンテナー、サブスクリプション / リソースグループ | サブスクリプションあたり 4,000 ロール割り当て |
| ACL | ディレクトリ、ファイル | 1ファイル・1ディレクトリあたり 32 エントリー(実質 28)。アクセス ACL と既定 ACL はそれぞれ 32 |

- 削除されたユーザーの ACL エントリーは GUID で表示される。手動で消す
- 出典: https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-access-control
