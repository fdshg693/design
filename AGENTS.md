# システムデザインの勉強

## フォルダ構成

- `projects/`: 実際のサービスを題材に、対話形式でシステム設計を行う(サービスごとにサブフォルダ)。詳細は `projects/AGENTS.md`
- `quiz/`: トピック別のシステムデザインのクイズ(問題・回答・調査結果)。詳細は `quiz/AGENTS.md`
- `services/`: 特定のサービス(例: Azure Service Bus)を主役に、そのサービスが活きる状況ごとに問題・設計を行う。他サービスは抽象的に扱う。詳細は `services/AGENTS.md`
- `readings/`: AI が完成済みの設計(Mermaid + 説明)を用意し、ユーザーが読んで質問しながら学ぶ。質問集付き。詳細は `readings/AGENTS.md`
- `docs/`: 特定の題材に紐づかない技術・概念そのものの解説(例: Redis の概要)。ユーザーが読んで質問しながら学ぶ。詳細は `docs/AGENTS.md`

- 各題材の配下に `deliverables/` がある場合は、ユーザーの依頼で作った発表資料(構成案と Marp / pptx)。作成は依頼があったときだけ `marp-deck` スキルで行う

- WEB 検索には `web-lookup` スキルがおすすめ
