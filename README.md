# プロジェクト名
かじまる

## 概要
プロジェクト名の由来は、「家事 ＋ まるっと」であり、日々の家事を全部回す・まるく収めることをねらいとする。

## 開発環境
- Python 3.13       # 最新のLTSバージョン
- Django 5.2.7      # 最新のLTSバージョン
- MySQL 8.4         # AWS RDS MySQLのLTS(8.4)と整合
- Bootstrap5 25.2   # Djangoと互換性のある最新版

## ディレクトリ・ファイル構成
本プロジェクトのディレクトリ・ファイル構成を以下のとおり示す。

<pre>
.
└── プロジェクト名
    ├── src                                   # ソースディレクトリ
    │   ├── apps                              # バックエンドディレクトリ
    │   │   ├── (core)                        # 任意(共通動作ディレクトリ)
    │   │   └── (your_app)                    # 任意
    │   ├── templates                         # テンプレートディレクトリ
    │   │   └── (your_html)                   # 任意
    │   ├── static                            # 静的ファイルディレクトリ
    │   │   ├── img                           # 画像ディレクトリ
    │   │   │   └── (your_img)                # 任意
    │   │   ├── css                           # CSSディレクトリ
    │   │   │   └── (your_css)                # 任意
    │   │   └── js                            # JavaScriptディレクトリ
    │   │       └── (your_js)                 # 任意
    │   ├── config                            # プロジェクト設定ディレクトリ
    │   │   ├── __init__.py                   # パッケージ化のための空ファイル
    │   │   ├── urls.py                       # プロジェクト全体のURL設定
    │   │   ├── asgi.py                       # 非同期通信のための設定ファイル
    │   │   ├── wsgi.py                       # 同期通信のための設定ファイル
    │   │   └── settings                      # 環境設定ディレクトリ
    │   │       ├── __init__.py               # パッケージ化のための空ファイル
    │   │       ├── base.py                   # 全環境共通の設定
    │   │       ├── dev.py                    # 開発環境専用の設定（例: DEBUG=True）
    │   │       └── prod.py                   # 本番環境専用の設定（例: DEBUG=False, セキュリティ強化）
    │   └── manage.py                         # Django管理ファイル
    ├── docker                                # Dockerディレクトリ
    │   ├── Dockerfile                        # Python(Django)のDockerイメージ
    │   └── wait-for-it.sh                    # DB起動後にDjangoを開始するためのシェルスクリプト
    ├── .dockerignore                         # Dockerビルド時の無視ファイルの設定
    ├── .gitignore                            # GitHubにpushしないファイルの設定
    ├── docker-compose.yml                    # Python(django)とDBの構成ファイル
    ├── Makeflie                              # コマンド省略のための設定ファイル
    ├── .env                                  # 開発用環境設定ファイル（Gitに含めない）
    ├── .env.exapmle                          # 環境変数のテンプレート（ダミー値で共有）
    ├── README.md                             # プロジェクトの説明ファイル
    └── requirements.txt                      # 依存関係ファイル
</pre>

## 開発環境の起動から終了までの手順
### 1) 環境変数ファイル.envの作成
.env.exampleをコピーして、.envファイルをプロジェクトルートディレクトリ直下に保存する。  
注）.envファイルは必ず、.env.exampleファイルと同じ階層に保存すること。（Docker、Djangoの設定ファイルで環境変数.envのファイルパスを指定しているため。）  
`cp .env.example .env`

以下が.env.exampleの中身であり、「各自で変更する設定」を各自で変更する。  
「DJANGO_SECRET_KEY」の設定は、以下のとおりである。  
`python -c "import secrets; print(secrets.token_urlsafe(50))"`

```
