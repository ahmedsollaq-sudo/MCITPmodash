FROM python:3.12-alpine

WORKDIR /app
COPY . /app

ENV MCIT_HOST=0.0.0.0 \
    MCIT_PORT=8768 \
    MCIT_AUTO_OPEN=false \
    MCIT_DATA_DIR=/data \
    MCIT_DIRECT_WRITE=true

RUN mkdir -p /data

EXPOSE 8765

CMD ["python", "server.py"]
