# 「本番」環境変数の読み込みファイル base.pyをimportして差分だけを記述
from .base import *

DEBUG = False
ALLOWED_HOSTS = ('kajimaru.com', '').split(',') # デプロイ先で公開サイトのURLに置き換える
CSRF_TRUSTED_ORIGINS = ['https://kajimaru.com']

# 静的ファイルの出力先
STATIC_ROOT = '/src/static/'


# 以下はセキュリティ強化の設定。現状は仮置き。
# HTTPをHTTPSに自動的にリダイレクトする。
SECURE_SSL_REDIRECT = True
# セッションクッキーにSecure属性を付与。HTTPでの漏洩を防ぐ。
SESSION_COOKIE_SECURE = True
# CSRFトークンを格納するクッキーにSecure属性を付与。CSRF攻撃に対する保護を強化する。
CSRF_COOKIE_SECURE = True
# ブラウザが強制的にHTTPSに切り替える。SSLストリッピング攻撃（SSL Stripping Attack）などから保護する。「31536000」は1年間の秒数
SECURE_HSTS_SECONDS = 31536000
# ウェブサイトのすべてのサブドメインをHTTPS経由でアクセスするように強制する。
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# ユーザーが初回アクセスをする前からHTTPSが強制されるようプリロードリストへの登録意思を示す。
SECURE_HSTS_PRELOAD = True
