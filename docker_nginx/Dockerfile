# 使用するイメージを設定
FROM nginx
USER root

ENV DOCKER_DIR="./docker_nginx"

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

# default.confファイル削除
RUN rm /etc/nginx/conf.d/default.conf
RUN touch /etc/nginx/conf.d/default.conf

# ローカルの default.conf をコンテナ内の /etc/nginx/conf.d/ にコピーする
COPY $DOCKER_DIR/app_nginx.conf /etc/nginx/conf.d/app_nginx.conf
# ローカルの uwsgi_params をコンテナ内の /etc/nginx/conf.d/ にコピーする
COPY $DOCKER_DIR/uwsgi_params /etc/nginx/.

# ローカルのhtmlファイル をコンテナ内の /var/www/html/ にコピーする
#COPY ./*.html /var/www/html/
# ローカルのStaticをコピー
COPY ./workspace/django_sql/static /static


RUN apt-get install -y vim less

# PORT開放
EXPOSE 8001

