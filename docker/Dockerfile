# 最新のLTSバージョンである3.13を使用
FROM python:3.13

# Pythonの出力をバッファリングしないように設定（ログが見やすくなるように設定）
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリの設定
WORKDIR /src

# wait-for-it.shをコンテナにコピー、実行権限を付与
COPY docker/wait-for-it.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-it.sh

# requirements.txtをワーキングディレクトリ直下にコピー
# 依存関係ファイルのみ先にコピー（キャッシュ効率化のため）
COPY requirements.txt .

# pipをアップデートして、Pythonのパッケージをインストール(-Uは--upgrade)
# ローカルの保存用ディレクトリ（キャッシュ）の影響を排除して、常に最新のパッケージをインストールしたいため、--no-cache-dirを採用
RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt

# ポート番号の明記（ドキュメント目的）
# 実際の指定はdocker-compose.ymlで指定
EXPOSE 8000


