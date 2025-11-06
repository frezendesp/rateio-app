#!/usr/bin/env bash
set -euo pipefail

SERVICE_FILE_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)/systemd/rateio.service"
SERVICE_FILE_TARGET="/etc/systemd/system/rateio.service"

if [[ $EUID -ne 0 ]]; then
  echo "Este script precisa ser executado como root." >&2
  exit 1
fi

echo "Instalando serviço systemd em ${SERVICE_FILE_TARGET}"
cp "$SERVICE_FILE_SOURCE" "$SERVICE_FILE_TARGET"
systemctl daemon-reload
systemctl enable rateio.service
systemctl restart rateio.service

echo "Serviço rateio.service instalado e iniciado."
