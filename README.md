# RareTECH 2026ハッカソン春の陣 Bチーム 「METIS」

## プロジェクト概要
### 概要
ハッカソン2026春の陣 Bチームの成果物になります。 <br>
「METIS」は資格学習ロードマップ自動生成アプリです。 <br>
受験資格、受験日、勉強時間を入力するとAIが自動で学習のロードマップを生成してくれます。 <br>
主な機能はロードマップ生成機能、学習管理機能、学習進捗可視化機能です。

### アプリ概要資料
[ハッカソン発表資料](/README_Materials/RareTECHハッカソン最終発表資料.pdf)

## 使用技術
| カテゴリ       | 使用技術 | バージョン |
| -------------- | ------- | ------- |
| フロントエンド | HTML <br> CSS <br> JavaScript <br> tailwindcss |
| バックエンド | django <br> gunicorn | 5.0 <br> 25.3.0 |
| データベース | MySQL(AWS RDS) | 8.4.8 |
| インフラ | AWS <br> docker <br> NGINX |
| デザイン | figma <br> Sparkle Design |

## デプロイ環境構築
インフラのデプロイ環境は、下記[インフラ構成](#インフラ構成)の環境を前提に説明。

### アプリ起動
1. 本アプリではOpenAIのAPIを使用します。事前にAPIキー取得を行なってください。
2. EC2インスタンス内に、Docker、Gitをインストール
3. 本リポジトリをクローン
4. .envを作成し以下を記述  

| 変数名       | 役割 | 入力値 |
| ----------- | ---- | ----- |
| DB_NAME | MySQLのデータベース名 |  |
| DB_USER | MySQLのユーザー名 |  |
| DB_PASSWORD | MySQLのパスワード |  |
| DB_HOST | MySQLのホスト名 |  |
| DB_PORT | MySQLのポート番号 |  |
| DJANGO_SECRET_KEY | Djangoのシークレットキー | 他者に推測されない <br> ランダムな値にすること。 |
| ALLOWED_HOSTS | Djangoで待ち受けるURL | デフォルト値:`localhost` <br> AWS ALBならALBのDNS名を <br> ドメインを取得するならドメイン名。 |
| AI_API_KEY | OpenAIのAPIキー | OpenAIのAPI取得をお願いします。 |

5. Nginxの設定ファイル ./dockerfiles/nginx/[default.conf](/dockerfiles/nginx/default.conf)の29行目 server_nameに.env内の`ALLOWED_HOSTS`と同じ値を入力(デフォルト値として`localhost`を記述してあります。)
6. `docker compose build`を実行
7. `docker compose up -d`を実行
8. `docker compose exec web python manage.py migrate`を実行

#### アプリ停止
##### DB情報保持
1. `docker compose down`を実行

##### DB情報(dockerボリューム)削除
1. `docker compose down -v`を実行 <br> 再起動時は再度マイグレーションを実行してください。

## 開発環境構築(ローカル環境にて起動)
1. 本リポジトリをクローン
2. .envを作成し以下を記述

`DB_NAME='django-db'DB_USER='django'` <br>
`DB_PASSWORD='django'` <br>
`DB_HOST='db'` <br>
`DB_PORT='3306'` <br>
`DJANGO_SECRET_KEY='(他者に推測されないランダムな値)'` <br>
`ALLOWED_HOSTS='localhost'` <br>
`AI_API_KEY='(APIキーを取得していないのであれば適当な値で良い)'` <br> 
※OpenAIのAPIキーが無くてもアクセスできますが一部機能が使用できずエラーになる恐れがあります。

3. Nginxの設定ファイル ./dockerfiles/nginx/[default.conf](/dockerfiles/nginx/default.conf)の29行目 server_nameに.env内の`ALLOWED_HOSTS`と同じ値を入力(デフォルト値として`localhost`を記述してあります。)
4. Djangoの[settings.py](/djangopj/settings.py)の43行目、`DEBUG = False`を`DEBUG = True`にし、デバッグモードへ変更
5. `docker-compose -f docker-compose-develop.yml build`を実 <br> 
docker-compose-develop.ymlがアプリをローカル環境で起動させるファイルになる為、ファイルを直接指定しています。
6. `docker-compose -f docker-compose-develop.yml up -d`を実行
7. `docker compose exec web python manage.py migrate`を実行
8. ブラウザにて http://localhost へアクセスすれば開発環境にてアプリ操作を行えます。

#### アプリ停止
##### DB情報保持
1. `docker compose -f docker-compose-develop.yml down`を実行 <br> 
※通常の`docker compose down`を実行してしまうと、DBコンテナが停止しません。

##### DB情報(dockerボリューム)削除
1. `docker compose -f docker-compose-develop.yml down -v`を実行

## インフラ構成
### 構成図
最終発表時のインフラ構成図
![インフラ構成図](/README_Materials/インフラ構成図ハッカソン春2026.png)
### インフラ構成概要
#### VPC
VPCはマルチAZ構成を基本としています。EC2、RDSをプライベートサブネットにおくことで、インターネット上からEC2、RDSへ直接アクセスできないようにしています。
#### EC2
EC2二つのマルチAZ構成を採用。EC2内でDockerを起動しアプリ運用を行います。
#### RDS
RDSはMySQLを使用しています。コストの関係上シングルAZ構成にしています。  
（RDSはインスタンスにもよるがシングル構成で約7,000円。マルチ構成だとその倍以上。）
#### ALB
EC2がプライベートサブネットにある為、ALBを使用することでHTTP通信のみに制限しアクセスすることができます。また、自動で負荷分散も可能にし、サーバーのヘルスチェックも担当します。ヘルスチェックは数10秒に一回HTTP通信をサーバーへ送り200が帰ってきたらサーバーは起動しているものとしています。
#### NATgateway
EC2からインターネットアクセスの為に設置。
#### SSM
セッションマネージャーを利用し、SSHを使用せずにEC2へアクセスすることによって、EC2のSSHポートを閉じることができセキュリティ向上に繋がります。
#### CloudWatch
EC2内のdockerログの取得とCPU使用率、メモリ使用率、ネットワークin/out、  
生きているサーバー数（ALBヘルスチェックのレスポンス200で判断）の監視に使用しました。  
また、アラームを設定しアラームが出たら行うアクションを選択でき今回はSNSでのメール送信を行いました。
（LambdaやEC2なども選ぶことができます。具体的に何ができるかはわかりませんが...）
メモリ使用率に閾値を超えたらアラームを出すように設定しました。
#### SNS
CloudWatchアラームが出たら、SNSにて事前に設定したメールアドレスへメールを送ることができます。