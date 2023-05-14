FROM python:3.8
USER root

ENV DOCKER_DIR="./docker_srv"
ENV SOURCE_DIR="./workspace"
ENV WORK_DIR="/workspace"
ENV SSH=./docker_srv/.ssh

RUN apt-get update && \
    apt-get -y install locales && \
    apt-get install -y vim less && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
#RUN apt-get install -y vim less

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm


# コンテナ側へコピー
COPY $DOCKER_DIR/requirements.txt requirements.txt
# python ライブラリインストール
RUN pip install -r ./requirements.txt

COPY $SSH /root/.ssh
RUN chmod 0600 /root/.ssh/*

WORKDIR $WORK_DIR
EXPOSE 8000

# Django起動
#CMD ["python", "/workspace/django_sql/manage.py", "runserver", "0.0.0.0:8000"]

#CMD ["uwsgi", "--socket", ":8000", "--chdir", "/workspace/deposit_srv", "--wsgi-file", "deposit_srv/wsgi.py"]
#CMD ["uwsgi", "--socket", ":8000", "--chdir", "/workspace/deposit_srv", "--wsgi-file", "env/wsgi.py"]

