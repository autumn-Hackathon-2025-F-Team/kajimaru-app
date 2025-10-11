# housework-management

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
    │   │   ├── __init__.py
    │   │   ├── urls.py                       # プロジェクト全体のURL設定
    │   │   ├── asgi.py
    │   │   ├── wsgi.py
    │   │   └── settings  /
    │   │       ├── __init__.py
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