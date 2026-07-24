# 令和に蘇りし銅鑼パーソン決定戦

その昔のYAPCで使われた銅鑼パーソン総選挙のサイトをリスペクト(?)した銅鑼叩きの投票サイト。
enPiT2023のLT会の投票とnotch_man君のLTネタのために作りました。
当時の物とは全く別物だと思います。

※このアプリでは特に音は鳴りません（仮）

## アーキテクチャ

GitHub OAuth でログインし、銅鑼パーソン候補への投票数を集計する FastAPI アプリ。
レイヤごとに責務を分割している。

```
dora_person/
├── main.py            # create_app(): アプリ生成・例外ハンドラ・ルーター登録
├── config.py          # Settings (pydantic-settings) に環境変数を集約
├── dependencies.py    # FastAPI の依存性注入（認証・サービス供給）
├── security.py        # セッションJWTの発行・検証
├── templating.py      # Jinja2 テンプレート環境
├── schemas.py         # DTO（GitHubProfile / SubmitRequest / Candidate）
├── errors.py          # ドメインエラー型
├── routers/           # ルーティング層
│   ├── pages.py       # トップ・ログイン・OAuthコールバック・投票ページ
│   └── votes.py       # 投票・立候補・リセット
├── services/          # ビジネスロジック層
│   ├── github.py      # GitHub OAuth / REST 連携ゲートウェイ
│   └── votes.py       # 投票ドメインロジック
├── repositories/      # 永続化層
│   ├── redis_votes.py     # 投票カウント（Redis）
│   └── mysql_candidates.py# 候補者（MySQL）
├── db/                # DBドライバ境界
│   ├── interface.py   # DBInfraInterface（抽象）
│   ├── mysql.py       # MySqlDB（実装）
│   └── connector.py   # プーリングコネクタ
├── templates/  static/
```

リクエストは `routers → services → repositories → db` の一方向に流れ、
各層は下位層を抽象（インターフェース／依存性注入）越しに利用するためユニットテストが容易。

## セットアップ（ローカル）

依存管理は [uv](https://docs.astral.sh/uv/) を利用する。

```shell
uv sync              # 依存をインストール（uv.lock に固定）
cp .env.example .env # 必要な値を埋める（SECRET_KEY は必須）
uv run hypercorn dora_person.main:app --reload
```

## 開発

```shell
uv run ruff check .      # lint
uv run ruff format .     # format
uv run pytest            # テスト
```

依存を追加・更新したら `uv.lock` が自動更新される（`uv add <pkg>` / `uv lock --upgrade`）。
`requirements.txt` は廃止し、Docker ビルドも `uv sync` に一本化した。

## Docker

`.env.local` に環境変数を用意した上で:

```shell
make up           # 開発（compose.yml）
make up mode=prod # 本番（compose.yml + compose.prod.yml、New Relic 有効）
```

Dockerfile はマルチステージの単一ファイルに統合。開発／本番の違いは実行コマンドのみで、
本番は `compose.prod.yml` が `newrelic-admin run-program` でラップしワーカー数を増やす。

## 困ったときはとりあえずこれを実行

```shell
make reset  # コンテナ・イメージ・ボリュームを一括削除
```
