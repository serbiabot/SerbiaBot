FROM python:3.10.12

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /apart_bot

COPY ./requirements.txt ./


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt


COPY ./ ./

RUN chmod -R 777 ./