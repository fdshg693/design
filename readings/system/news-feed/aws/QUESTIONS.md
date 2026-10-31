# 質問集

質問が浮かばないときはここから選ぶ。「Q03 教えて」のように ID で聞けばよい。回答は [QA.md](QA.md) に記録される。

base の質問(`base Q01` など)は [../base/QUESTIONS.md](../base/QUESTIONS.md)。ここでは AWS 固有の話に絞る。

## 理解確認

- [ ] Q01: 投稿 1 件が、DynamoDB・Streams・Lambda・Valkey をどの順に通る?どこまでが同期で、フォロワーへの反映は最大何秒かかる?
- [ ] Q02: イベントフィルタで何を落としている?フィルタで落ちたレコードに Lambda の料金はかかる?
- [ ] Q03: クラスタモードの Valkey で、本文 30 件の `MGET` はどう分割されて送られる?

## なぜ

- [ ] Q04: base のキューを SQS にせず、DynamoDB Streams にしたのはなぜ?API から SQS に送ると何が困る?
- [ ] Q05: ElastiCache を Serverless ではなくノードベースにしたのはなぜ?Serverless のほうが良いのはどんなとき?
- [ ] Q06: プロフィール用の GSI を KEYS_ONLY にしたのはなぜ?ALL にすると何が増える?
- [ ] Q07: フォローを TransactWriteItems で書くのはなぜ?Put と UpdateItem に分けると何が起きる?

## エッジケース

- [ ] Q08: 投稿直後に自分のプロフィールを開くと、GSI の遅れで投稿が見えないことはある?防ぐなら?
- [ ] Q09: Lambda のリトライや二分割で、同じレコードが 2 回処理されたらどうなる?
- [ ] Q10: しばらくホームを開いていない人のタイムラインには書かないとすると、その人が戻ってきたとき何が起きる?

## 障害

- [ ] Q11: fan-out Lambda がエラーを出し続けたら、レコードはいつまで残る?SQS に退避した後はどう流し直す?
- [ ] Q12: Valkey のプライマリが 1 台落ちたら、ホームと fan-out はどうなる?フェイルオーバー中に書いた ZADD は失われる?
- [ ] Q13: 1 つの AZ が丸ごと落ちたら、Fargate・Lambda・Valkey・DynamoDB はそれぞれどう振る舞う?

## スケール

- [ ] Q14: 投稿が 1,000 件/秒に増えたら、Streams のシャード数と Lambda の並列数はどう追従する?どこで遅れが出る?
- [ ] Q15: Valkey とのクロス AZ 転送が月 $500 を超えるのはなぜ?同じ AZ のレプリカから読めば減らせる?
- [ ] Q16: 5 年後 3TB の `posts` は、Standard-IA テーブルクラスや TTL + S3 への退避にすべき?

## 別の設計

- [ ] Q17: タイムラインを Valkey ではなく DynamoDB の受信箱テーブルに置いたら、費用と読みの速さはどうなる?

## 発展

- [ ] Q18: マルチリージョンにするなら、DynamoDB Global Tables と Valkey(Global Datastore)をどう組み合わせる?fan-out はどのリージョンで走らせる?
