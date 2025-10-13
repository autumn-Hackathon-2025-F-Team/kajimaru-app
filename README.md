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
本アプリのディレクトリ・ファイル構成を以下のとおり示す。

.
└── アプリ名
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

## 開発環境の起動から終了までの手順
### 1) 環境変数ファイル.envの作成
.env.exampleをコピーして、.envファイルをプロジェクトルートディレクトリ直下に保存する。  
注）.envファイルは必ず、.env.exampleファイルと同じ階層に保存すること。（Docker、Djangoの設定ファイルで環境変数.envのファイルパスを指定しているため。）  
`cp .env.example .env`

以下が.env.exampleの中身であり、「各自で変更する設定」を各自で変更する。  
「DJANGO_SECRET_KEY」の設定は、以下のとおりである。  
`python -c "import secrets; print(secrets.token_urlsafe(50))"`

```
======= ✅ チームで共通にする設定 =======
MYSQL_DATABASE=django_db                    # 開発環境で使うデータベース名（チームで共通・固定）
MYSQL_USER=dev_user                         # 開発用のデータベースユーザ名（チーム共通）
MYSQL_HOST=db                               # Django(web)コンテナが接続するDBコンテナ名(db)（チーム共通）
MYSQL_PORT=3306                             # MySQLのポート番号（チーム共通）
DJANGO_PORT=8000                            # Djangoのポート番号（チーム共通）
DJANGO_LANGUAGE_CODE=ja                     # 言語コード設定(チーム共通)
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1    # アプリにアクセスできるホスト・ドメイン名（チーム共通）
DJANGO_SETTINGS_MODULE=config.settings.dev  # 開発環境ファイルの参照（チーム共通）
TZ=Asia/Tokyo                               # タイムゾーン設定（チーム共通）
USERNAME=appuser                            # コンテナ内のユーザーネーム（チーム共通）
GROUPNAME=appgroup                          # コンテナ内のグループネーム（チーム共通）

======= 🔧 各自で変更する設定 =======
MYSQL_PASSWORD=your_own_password            # 各自がローカル環境で設定するDBユーザーパスワード(環境開発で各自設定、非公開)
MYSQL_ROOT_PASSWORD=your_root_pw            # MYSQLのrootパスワード(開発環境で各自設定、非公開)
DJANGO_SECRET_KEY=your_secret_key           # Djangoのセキュリティキー(必ず各自で生成すること)
DJANGO_DEBUG=True                           # デバッグモード設定。開発中はTrue、本番や検証環境はFalse推奨
UID=your_uid                                # 各自のuidを指定（id -uコマンドで確認）
GID=your_gid                                # 各自のgidを指定（id -gコマンドで確認）
```

### 2) 起動時のdockerコマンド
初回起動ではイメージをビルドする必要があるため、以下のコマンドで起動させる。  
`docker compose up --build`  
もしくは  
`make build`

2回目以降は既にイメージがビルドされているため、以下のコマンドで起動してもよい。  
必要に応じて、 **-d** をupの後に付けて、バックグラウンドで起動してもよい。  
`docker compose up -d`  
もしくは  
`make up`

### 3) 終了時のdockerコマンド
終了時は以下のコマンドで終了する。  
必要に応じて、ボリューム（db_data）を削除する場合は、 **-v** をdownのあとに付ける。  
`docker compose down`  
もしくは  
`make down`

## アクセス先
ブラウザで以下のアドレスを入力して、Djangoの初期画面が開いていることを確認する。  
`http://localhost:8000/`  
もしくは  
`http://127.0.0.1:8000/`  

ドキュメントが **「日本語」** 、DEBUGが **「True」** になっていることを確認する。  
成功すると以下の画面が表示される。  
<img width="auto" height="auto" alt="Image" src="https://github.com/user-attachments/assets/15fc92ec-35fb-4c9e-9c9a-3439b8e3fd29" />

## 各コンテナへのアクセス手順
### 1)MySQL(db)
MySQLコンテナへのアクセスは、以下のコマンドを入力する。  
`docker compose exec -it db mysql -u dev_user -p`  
もしくは  
`make db`  
コマンド入力後にパスワードを聞かれるため、.envの「MYSQL_PASSWORD」で設定したパスワードを各自入力する。  

### 2)Django(web)
Djangコンテナへのアクセスは、以下のコマンドを入力する。  
`docker compose exec -it web /bin/bash`  
もしくは  
`make sh`  

また、docker compose up -dで起動した後に、Djangoのlogsを確認したい場合は、以下のコマンドを入力する。  
`docker compose logs -f web`  
もしくは  
`make logs`  

## Django 新規アプリ作成手順
### 1) 新規アプリの作成
以下のコマンドで新規アプリを作成する。  
通常のコマンドでは、長くなるため、以下のmakeコマンドを推奨する。  
<アプリ名>に作成したいアプリを入力する。  
`make app name=<アプリ名>`  
もしくは  
`docker compose exec web mkdir -p apps/<アプリ名>`  
`docker compose exec web python manage.py startapp <アプリ名> apps/<アプリ名>`  

コマンド入力後に、/src/appsの直下に指定したアプリが作成されていることを確認する。  

### 2) INSTALLED_APPSへの新規アプリ追加
以下のファイル（base.py）のINSTALLED_APPS変数へ新規アプリを追加する。  
`/src/config/settings/base.py`  
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    '（ここにアプリを追加する。以下はアプリ名「test」の一例）',
    'apps.test.apps.TestConfig'
]
```

### 3) apps.pyへのname追加
新規作成したアプリディレクトリ内のapps.pyへnameを追加する。  
以下はアプリ名「test」とした場合の一例である。  
appsディレクトリ下にあるため、name=apps.<アプリ名>とする。  
```
class TestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.test'
```

## Django マイグレーションファイル作成、マイグレーションの手順
### 1) models.pyへのテーブル定義
該当アプリディレクトリのmodels.pyにテーブルを定義する。  

### 2) マイグレーションファイルの作成
models.pyのテーブル定義後、マイグレーションファイルを作成するために以下のコマンドを入力する。  
`docker compose exec web python manage.py makemigrations`  
もしくは  
`make mm`  
マイグレーションファイルが作成されると、該当ディレクトリの「migrations」にマイグレーションファイルが作成される。（例：0001_initial.py）  

### 3) マイグレーション（データベースへの反映）
マイグレーションファイルが作成された後に、以下のコマンドを入力して、データベースへ反映させる。  
`docker compose exec web python manage.py migrate`  
もしくは  
`make migrate`  

コマンド入力後に、MySQLコンテナへ入り、テーブルが作成されていれば、マイグレーション完了である。  

## Django 管理者作成手順
Djangoでの管理者作成は、以下のコマンドで行う。  
`docker compose exec web python manage.py createsuperuser`  
もしくは  
`make csu`  
コマンド入力後に、ユーザー名、メールアドレス（省略可）、パスワードが聞かれるため、各自で設定する。  
ブラウザに以下のアドレスを入力し、設定したユーザー名とパスワードを入力し、ログインできるか確認する。  
`http://localhost:8000/ or http://127.0.0.1:8000/`  
成功すると以下の画面が表示される。  
<img width="auto" height="auto" alt="Image" src="https://github.com/user-attachments/assets/db0ab465-c744-4f87-8bbd-0e018c0beaa2" />


