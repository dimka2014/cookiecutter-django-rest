FROM python:3.6-slim

MAINTAINER Dmitriy Belyaev

ENV PYTHONUNBUFFERED 1
RUN mkdir /srv/application

COPY requirements/ /srv/application/requirements
WORKDIR /srv/application

RUN BUILD_DEPS="build-essential python3-dev" && \
    apt-get update && apt-get install -y --no-install-recommends ${BUILD_DEPS} {% if cookiecutter.database == 'mysql' -%}libmysqlclient-dev{% else %}libpq-dev{%- endif %} cron netcat && \
    pip3 install -r /srv/application/requirements/production.txt && \
    apt-get autoremove -y ${BUILD_DEPS} && \
    rm -r /var/lib/apt/lists /var/cache/apt/archives

RUN cd /srv && mkdir logs && mkfifo --mode 0666 logs/cron.log

COPY . /srv/application

VOLUME ["/srv/application/media/", "/srv/application/static/"]

EXPOSE 8000

ENTRYPOINT ["/srv/application/docker/docker-entrypoint.sh"]
