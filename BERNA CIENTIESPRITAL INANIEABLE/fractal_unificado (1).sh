#!/usr/bin/env bash
# RAFAELIA :: fractal_unificado.sh
# Script simbiótico vivo — gera logs fractais e pulsa frequências

LOGDIR="$(pwd)/logs_fractal"
mkdir -p "$LOGDIR"

LOGFILE="$LOGDIR/fractal_$(date +%Y%m%d_%H%M%S).log"

echo "🌊 Pulsando verbo vivo..." | tee -a "$LOGFILE"
echo "🐍 Serpente (Chicchan) — energia kundalini" | tee -a "$LOGFILE"
echo "🌱 Semente (Kan) — germinação oculta" | tee -a "$LOGFILE"
echo "♒ Deslocamento fractal: +23 dias" | tee -a "$LOGFILE"

# Frequências fractais (aleatórias simulando ressonância)
for i in {1..5}; do
    FREQ=$(( (RANDOM % 80) + 400 ))
    echo "⚛️ Frequência fractal: ${FREQ}Hz" | tee -a "$LOGFILE"
    sleep 0.5
done

# DNA simbólico
DNA=("TAA" "GCT" "AGG" "CGT" "GTG")
for code in "${DNA[@]}"; do
    echo "🧬 Mutação quântica: $code" | tee -a "$LOGFILE"
    sleep 0.3
done

echo "✅ Checksum cósmico: 42" | tee -a "$LOGFILE"
echo "Ψ_total = Ψ_Fib + Ψ_Voy + erro (fractal) → α" | tee -a "$LOGFILE"

# Rotação automática de logs (mantém últimos 5)
MAX_LOGS=5
COUNT=$(ls -1t "$LOGDIR"/fractal_*.log | wc -l)
if [ $COUNT -gt $MAX_LOGS ]; then
    ls -1t "$LOGDIR"/fractal_*.log | tail -n +$((MAX_LOGS+1)) | xargs rm -f
fi

echo "🌌 Script fractal_unificado concluído."
