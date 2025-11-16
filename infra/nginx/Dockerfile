# nginxのDockerfile
# curlコマンドインストールのため、Dockerfileを作成（docker-composeのcommandではCMDが上書きされてしまうため）
FROM nginx:1.28

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*