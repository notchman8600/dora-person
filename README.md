**for main server (stg&prod)**

```shell
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## 困ったときはとりあえずこれを実行

```shell
docker compose down --rmi all --volumes --remove-orphans
```