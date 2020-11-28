FROM python:3.8-alpine

RUN apk --no-cache add linux-headers musl-dev gcc py3-numpy

ENV PYTHONPATH /usr/lib/python3.8/site-packages

COPY ./build/ /app/

WORKDIR /app

RUN pip install -r requirements.txt

RUN apk --no-cache del linux-headers musl-dev gcc

ENTRYPOINT ["python", "respeaker_leds_hermes.py"]
