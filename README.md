# 令和に蘇りし銅鑼パーソン決定戦

その昔のYAPCで使われた銅鑼パーソン総選挙のサイトをリスペクト(?)した銅鑼叩きの投票サイト。
enPiT2023のLT会の投票とnotch_man君のLTネタのために作りました。
当時の物とは全く別物だと思います。

※このアプリでは特に音は鳴りません（仮）

## how to use

.env.exampleを参考に必要な物は自分で集めてください。GitHub APIのクライアントIDとシークレット以外に変な物は無いと思います。

```shell
docker compose build
docker compose up -d
```

## パッケージを更新したらこれを叩け

```shell
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## 困ったときはとりあえずこれを実行

```shell
docker compose down --rmi all --volumes --remove-orphans
```
