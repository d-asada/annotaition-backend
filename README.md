# README

##  API_KEYの設定

.chalice/config.jsonの
```
"OPENAI_API_KEY": "YOUR_API_KEY"
```
のYOUR_API_KEYを自身のAPIキーに変更。

## ローカル実行時
```
pip install -r requirements.txt
chalice local
```
上記のコマンドでローカルホストに8000番ポートで起動。

## AWS環境にデプロイ

### 前提

AWSのIAMユーザキーが設定済みであること

### デプロイ

```
pip install --target vendor/  -r requirements.txt
chalice package .chalice/deployments/
chalice deploy
```

で、API Gateway, Lambdaなどがデプロイされる。