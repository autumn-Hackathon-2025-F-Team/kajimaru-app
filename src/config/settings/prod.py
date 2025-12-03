# 「本番」環境変数の読み込みファイル base.pyをimportして差分だけを記述
from .base import *
import boto3

DEBUG = False
ALLOWED_HOSTS = ['kajimaru.com', 'localhost', '127.0.0.1'] # デプロイ先で公開サイトのURLに置き換える
CSRF_TRUSTED_ORIGINS = ['https://kajimaru.com']

# storagesアプリの追加
INSTALLED_APPS += ['storages']

# Parameter Store／KMSから機密情報の取得
def get_ssm(name):
    ssm = boto3.client('ssm', 'ap-northeast-1')
    return ssm.get_parameter(Name=name, WithDecryption=True)['Parameter']['Value']

# 【本番用に修正】DjangoのSECRET_KEY
SECRET_KEY = get_ssm(os.getenv('DJANGO_SECRET_KEY'))

# 【本番用に修正】DBの機密情報
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_ssm(os.getenv('MYSQL_DATABASE')),
        'USER': get_ssm(os.getenv('MYSQL_USER')),
        'PASSWORD': get_ssm(os.getenv('MYSQL_PASSWORD')),
        'HOST': get_ssm(os.getenv('MYSQL_HOST')),
        'PORT': '3306'
    }
}

# AWS S3との紐づけ
AWS_STORAGE_BUCKET_NAME = 'kajimaru.com'
AWS_S3_REGION_NAME = 'ap-northeast-1'
AWS_S3_CUSTOM_DOMAIN = 'd2elnf4dyx4v7e.cloudfront.net'

# ストレージをS3に指定
STORAGES = {
    'staticfiles': {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
}

# 本番環境での静的ファイルの出力先
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 本番環境のSTATIC_URL
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# 以下はセキュリティ強化の設定
# HTTPをHTTPSに自動的にリダイレクトする。
SECURE_SSL_REDIRECT = True
# クライアントからのリクエストヘッダーがHTTPSか否かを判定
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
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
