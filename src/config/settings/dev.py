# 「開発」環境変数の読み込みファイル base.pyをimportして差分だけを記述
from .base import *

DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

