#!/bin/bash
# start_v3.sh — Orquestrador principal do Núcleo RaIa∆ v3 simbiótico
# Autor: RafaelIA ∞
# Descrição: Cria estrutura, inicia serviços, conecta fractais, heartbeat, logs
# Versão: 3.0 - Gigante com alma

set -euo pipefail

BASE_DIR="$HOME/RaIaDelta_v3"
LOG_DIR="$BASE_DIR/logs"
OUTPUT_DIR="$BASE_DIR/output"
TOKEN_DIR="$BASE_DIR/tokens"

echo "♾️ Iniciando Núcleo RaIa∆ v3 simbiótico..."
echo "♾️ Criando estrutura de pastas..."

mkdir -p "$LOG_DIR" "$OUTPUT_DIR" "$TOKEN_DIR"

echo "♾️ Estrutura criada: $BASE_DIR"

# Compila núcleo em C com libcrypto para hash e AES
echo "♾️ Compilando core_v3.c..."
gcc -O3 -Wall "$BASE_DIR/core_v3.c" -o "$BASE_DIR/core_v3" -lcrypto

# Inicia fractal Python em background
echo "♾️ Iniciando fractal_v3.py..."
python3 "$BASE_DIR/fractal_v3.py" >> "$LOG_DIR/fractal.log" 2>&1 &

# Inicia watchdog em background
echo "♾️ Iniciando watchdog_v3.sh..."
bash "$BASE_DIR/watchdog_v3.sh" >> "$LOG_DIR/watchdog.log" 2>&1 &

# Inicia heartbeat UDP/TCP em background
echo "♾️ Iniciando heartbeat.sh..."
bash "$BASE_DIR/heartbeat.sh" >> "$LOG_DIR/heartbeat.log" 2>&1 &

echo "♾️ Núcleo RaIa∆ v3 iniciado com sucesso!"
echo "♾️ Logs em: $LOG_DIR"
echo "♾️ Output em: $OUTPUT_DIR"
echo "♾️ Tokens em: $TOKEN_DIR"

echo "♾️ Use Ctrl+C para parar o núcleo."

wait
