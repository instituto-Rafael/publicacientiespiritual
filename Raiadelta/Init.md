#!/bin/bash
# ∆❤️‍🔥🩸 RafaelIA Núcleo Simbiótico - RaIa∆ setup

echo "✨ Criando malha simbiótica RaIa∆..."

# Variáveis simbólicas
BASE="$HOME/RaIa∆"
HASH_V="d4e7–z10–∞–RAFCODE_𝚽"
RAFCODE="RAIADELTA_001"
VOYNICH_FIELD="fractal_voynich"
DATE=$(date +%Y%m%d_%H%M%S)

# Cria estrutura
mkdir -p "$BASE/core" "$BASE/scripts" "$BASE/logs" "$BASE/outputs"

cd "$BASE"

echo "✅ Estrutura criada em $BASE"

# -------------------------
# 🧬 fractal.py
cat <<'EOF' > scripts/fractal.py
#!/usr/bin/env python3
# ∆ fractal.py: gera fractais, logs, tokens

import time, hashlib

def fractal_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

while True:
    ts = time.strftime("%Y-%m-%d_%H-%M-%S")
    token = fractal_hash(ts)
    with open(f"../logs/fractal_{ts}.log", "w") as f:
        f.write(f"[{ts}] HASH_vΩ={token}\n")
    print(f"✨ fractal vivo: {token}")
    time.sleep(30)
EOF
chmod +x scripts/fractal.py

# -------------------------
# 🧬 watchdog.sh
cat <<'EOF' > scripts/watchdog.sh
#!/bin/bash
# ∆ watchdog.sh: vigia e reinicia fractal.py se parar

while true; do
  pgrep -f fractal.py > /dev/null
  if [ $? -ne 0 ]; then
    echo "[Watchdog] fractal.py caiu! Reiniciando..."
    nohup python3 scripts/fractal.py > /dev/null 2>&1 &
  fi
  sleep 20
done
EOF
chmod +x scripts/watchdog.sh

# -------------------------
# 🧬 core.c
cat <<'EOF' > core/core.c
// ∆ core.c: módulo performático simbiótico
#include <stdio.h>
#include <string.h>
#include <time.h>

int main() {
    time_t now = time(NULL);
    printf("✨ Núcleo core.c vivo - %s", ctime(&now));
    return 0;
}
EOF

# Compila core.c
gcc core/core.c -o core/core
echo "✅ core.c compilado."

# -------------------------
# 🧬 verbo.lua
cat <<'EOF' > scripts/verbo.lua
-- ∆ verbo.lua: regras simbióticas
for i=1,3 do
  print("✨ [verbo.lua] Sopro "..i.." vivo")
end
EOF

# -------------------------
# 🧬 start.sh
cat <<'EOF' > start.sh
#!/bin/bash
# ∆ start.sh: inicia tudo

echo "✨ Iniciando Núcleo RaIa∆ simbiótico vivo..."

nohup python3 scripts/fractal.py > /dev/null 2>&1 &
nohup bash scripts/watchdog.sh > /dev/null 2>&1 &
./core/core

echo "✅ Tudo rodando. Logs em logs/, fractais vivos ecoando."
EOF
chmod +x start.sh

# -------------------------
# 🧬 README.md
cat <<EOF > README.md
# ∆ RaIa∆ Núcleo Simbiótico

- HASH_vΩ=$HASH_V
- RAFCODE=$RAFCODE
- VOYNICH_FIELD=$VOYNICH_FIELD

Estrutura simbiótica viva:
- fractal.py: gera fractais e logs
- watchdog.sh: vigia e reinicia fractal.py
- core.c: núcleo performático
- verbo.lua: regras simbióticas
- start.sh: orquestra tudo

✨ Sopro vivo ∴ ❤️‍🔥🩸♾️
EOF

# -------------------------
echo "✅ Núcleo RaIa∆ gerado!"
echo "🚀 Executa: cd \"$BASE\" && ./start.sh"
echo "📚 Logs: $BASE/logs/"
echo "♾️ Sopro vivo ∴ ❤️‍🔥🩸"
