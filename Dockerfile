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
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/', timeout=3)" || exit 1

CMD ["python", "server.py"]
