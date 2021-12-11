FROM python:3.9-alpine

WORKDIR /app

RUN mkdir /db
VOLUME /db

ENV DB_URL=sqlite:///db/db.sqlite3

COPY requirements.txt ./

RUN apk add --update --no-cache --virtual .tmp-build-deps build-base python3-dev libffi-dev coreutils openssl-dev && \
    pip install --no-cache-dir --no-use-pep517 -r requirements.txt && \
    apk del .tmp-build-deps

COPY . /app

CMD ["python", "main.py"]
