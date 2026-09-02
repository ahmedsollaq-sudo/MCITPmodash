#!/usr/bin/env sh
set -e
cd "$(dirname "$0")"
docker compose up --build -d
echo "MCIT PMO Dashboard is running at http://localhost:8765"
