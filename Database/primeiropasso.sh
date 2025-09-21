#!/data/data/com.termux/files/usr/bin/bash

WORKDIR="/storage/downloads/doit"
cd "$WORKDIR"

# 1. Extrair APK/XAPK para pasta temp/
for f in *.apk *.xapk; do
  [ -f "$f" ] || continue
  mkdir -p temp && cd temp
  if [[ $f == *.xapk ]]; then
    unzip "../$f"
  else
    unzip "../$f"
  fi
  cd ..
done

# 2. Limpando lixo (libs, trackers, redundâncias)
find temp/ -name "*.so" -delete
find temp/ -name "*.dex" -delete
find temp/ -name "lib*" -exec rm -rf {} +
find temp/ -name "*firebase*" -exec rm -rf {} +

# 3. Recria Manifesto e Identidade
python3 <<EOF
import os, hashlib
manifest = f"RAFAELIA_MOD_{hashlib.sha256(b'RAFAELIA').hexdigest()[:8]}.txt"
with open(manifest, 'w') as f:
    f.write("Manifesto Vivo - RAFAELIA MOD\nAssinatura: BITRAF-Ω\n")
EOF

# 4. Reconstrói APK/XAPK limpo
cd temp && zip -r ../RAFAELIA_MOD_FINAL.zip . && cd ..
