FROM python:3.6-alpine

RUN mkdir -p /usr/src/wabot

WORKDIR /usr/src/wabot
COPY requirements.txt /usr/src/wabot/requirements.txt

RUN apk add gcc \
            libressl-dev \
            musl-dev \
            libffi-dev \
            py-dateutil \
            py3-setuptools \
            python3-dev \
            libevent-dev \
            libxml2 \
            libxslt-dev \
            ncurses-dev \
			openssl-dev \
            tzdata \
            && ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
            && echo Europe/Moscow > /etc/timezone 

RUN	pip3 install -r requirements.txt 

COPY . /usr/src/wabot/
RUN chmod +x ./install.sh 
RUN sh ./install.sh -i

