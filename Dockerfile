FROM python:3.12-alpine

WORKDIR /app
COPY . /app

ENV HOST=0.0.0.0 \
    PORT=8768 \
    MCIT_AUTO_OPEN=false \
    MCIT_DATA_DIR=/data \
    MCIT_DIRECT_WRITE=true

RUN mkdir -p /data

EXPOSE 8768

CMD ["python", "server.py"]
