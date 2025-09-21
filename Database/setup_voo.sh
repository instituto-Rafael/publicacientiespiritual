#!/usr/bin/env bash
set -e
echo "=== RAFAELIA: Setup rápido para Obra-APK (Termux-friendly) ==="

echo "[1/6] Atualizando e instalando pacotes mínimos (pode demorar)..."
pkg update -y
pkg upgrade -y
pkg install -y openjdk-17 python git zip unzip wget curl nano
python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
python3 -m pip install pynacl >/dev/null 2>&1 || true

echo "[2/6] Criando manifest.json ..."
cat > manifest.json <<'JSON'
{
  "name": "ARKRE-VERBOΩ - Obra-APK",
  "author": "Rafael Melo Reis / ∆RafaelVerboΩ",
  "nucleo": "FCEA / VERBO VIVO / CVV188 / 999",
  "hash_simbólico": "3f9c...z0∞ΣΦΩΔARKRE",
  "timestamp": "2025-09-18T00:00:00Z",
  "tags": ["ARKRE","VERBOΩ","RAFCODE-𝚽","ZIPRAF","ZRF"],
  "instructions": "Obra-APK viva e absoluta — entregue com RAFCODE embutido. Autorização: D'Ele.",
  "signature_type": "RAFCODE-Ed25519-embedded"
}
JSON

echo "[3/6] Criando raf_sign.py ..."
cat > raf_sign.py <<'PY'
#!/usr/bin/env python3
from nacl import signing, encoding
import sys, os
def gen_keys(private_out="raf_priv.pem", pub_out="raf_pub.pem"):
    sk = signing.SigningKey.generate()
    pk = sk.verify_key
    open(private_out,"wb").write(sk.encode())
    open(pub_out,"wb").write(pk.encode())
    print(f"Generated keys: {private_out}, {pub_out}")
    return sk, pk
def sign_file(sk, target_path, sig_out="rafcode.sig"):
    with open(target_path,"rb") as f:
        data = f.read()
    sig = sk.sign(data).signature
    open(sig_out,"wb").write(sig)
    print(f"Signed {target_path} -> {sig_out}")
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 raf_sign.py <file-to-sign> [privkey]")
        sys.exit(1)
    target = sys.argv[1]
    if len(sys.argv) >= 3:
        privfile = sys.argv[2]
        sk = signing.SigningKey(open(privfile,"rb").read())
        pk = sk.verify_key
    else:
        sk, pk = gen_keys()
    sign_file(sk, target)
    print("Public key (hex):", pk.encode(encoder=encoding.HexEncoder).decode())
PY
chmod +x raf_sign.py

echo "[4/6] Criando build_voo.sh (versão simplificada para telefone)..."
cat > build_voo.sh <<'SH2'
#!/usr/bin/env bash
set -e
PROJECT_DIR="${1:-./project}"
OUTDIR="${2:-./out}"
KEYSTORE="${3:-./release.keystore}"
KEYPASS="${4:-rafael_pass}"
ALIAS="${5:-rafkey}"

mkdir -p "$OUTDIR"
echo "Project dir: $PROJECT_DIR"
if [ ! -f "$PROJECT_DIR/unsigned.apk" ]; then
  echo "Erro: coloque um unsigned.apk em $PROJECT_DIR/unsigned.apk e rode novamente."
  exit 1
fi

UNSIGNED="$PROJECT_DIR/unsigned.apk"
cp "$UNSIGNED" "$OUTDIR/unsigned.apk"

if [ ! -f "$KEYSTORE" ]; then
  echo "Criando keystore (jarsigner / RSA 2048) em $KEYSTORE"
  keytool -genkeypair -v -keystore "$KEYSTORE" -alias "$ALIAS" \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass "$KEYPASS" -keypass "$KEYPASS" \
    -dname "CN=Rafael Melo Reis, OU=RAFAELIA, O=FCEA, L=Brasil, ST=SP, C=BR"
fi

SIGNED="$OUTDIR/signed.apk"
echo "Assinando com jarsigner (v1) - pode não atender v2/v3. Se APK falhar no Android moderno, será necessário apksigner do SDK."
jarsigner -keystore "$KEYSTORE" -storepass "$KEYPASS" -keypass "$KEYPASS" "$UNSIGNED" "$ALIAS"
cp "$UNSIGNED" "$SIGNED"

# criar assets e embutir manifest + raf signature
mkdir -p "$OUTDIR/assets"
cp ../manifest.json "$OUTDIR/assets/manifest.json" 2>/dev/null || cp manifest.json "$OUTDIR/assets/manifest.json"

# gerar assinatura RAFCODE sobre o APK final
python3 raf_sign.py "$SIGNED" || { echo "erro gerando raf signature"; exit 1; }
mv rafcode.sig "$OUTDIR/assets/rafcode.sig" || cp rafcode.sig "$OUTDIR/assets/rafcode.sig" 2>/dev/null || true
[ -f raf_pub.pem ] && cp raf_pub.pem "$OUTDIR/assets/raf_pub.pem" 2>/dev/null || true

# embutir assets no APK (zip)
TMPAPK="$OUTDIR/temp_injected.apk"
cp "$SIGNED" "$TMPAPK"
( cd "$OUTDIR/assets" && zip -ur "../temp_injected.apk" . ) >/dev/null 2>&1 || true
mv "$TMPAPK" "$OUTDIR/raf_signed_with_rafcode.apk"
echo "Final APK: $OUTDIR/raf_signed_with_rafcode.apk"
SH2
chmod +x build_voo.sh

echo "[5/6] Pequeno README com o fluxo (imediato):"
cat > README_voo.txt <<'TXT'
1) Crie a pasta do projeto e coloque seu unsigned.apk dentro:
   mkdir -p project
   cp /sdcard/Download/meu_unsigned.apk project/unsigned.apk

2) Rode o build (exemplo):
   ./build_voo.sh ./project ./out ./release.keystore "senha_keystore" rafkey

3) Resultado:
   ./out/raf_signed_with_rafcode.apk

OBS: jarsigner faz assinatura v1 (legacy). Para assinatura v2/v3 em Android moderno, é preciso usar apksigner do Android SDK; se precisar, eu explico como instalar/usar apksigner (mais pesado no celular).
TXT

echo "[6/6] Pronto. Arquivos criados: manifest.json, raf_sign.py, build_voo.sh, README_voo.txt"
echo "Tenta agora:"
echo "1) cria a pasta do projeto -> mkdir -p project"
echo "2) move teu unsigned.apk para project/unsigned.apk (use o gerenciador de arquivos do Android ou mv)"
echo "3) ./build_voo.sh ./project ./out ./release.keystore 'sua_senha' rafkey"
echo "Se quiser que eu gere um APK dummy de exemplo para testar o fluxo, eu explico o próximo comando."
