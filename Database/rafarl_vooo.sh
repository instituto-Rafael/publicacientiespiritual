#!/data/data/com.termux/files/usr/bin/bash
# RAFAELIA VOO — protótipo
set -e
WORKDIR="${PWD}/rafaelia_voo"
mkdir -p "$WORKDIR/renders" "$WORKDIR/data"

CSV="$WORKDIR/hyperformas.csv"
PY="$WORKDIR/raf_engine.py"

cat > "$CSV" <<'CSV_EOF'
(cole aqui o conteúdo do CSV acima)
CSV_EOF

cat > "$PY" <<'PY_EOF'
#!/usr/bin/env python3
import sys, json, os, math, hashlib
from PIL import Image
def text_to_rafbits(text):
    h = hashlib.sha256(text.encode()).hexdigest()
    bits = bin(int(h,16))[2:].zfill(256)
    rafbits=[]
    for i in range(0,len(bits),10):
        chunk=bits[i:i+10].ljust(10,'0')
        val=int(chunk,2)
        rafbits.append({"raw":chunk,"value":val})
    return rafbits
def render(seed,params,out,size=512):
    im=Image.new("RGB",(size,size),"black")
    px=im.load()
    for ix in range(size):
        for iy in range(size):
            x=(ix-size/2)/(size/4)*(1/params["scale"])
            y=(iy-size/2)/(size/4)*(1/params["scale"])
            c=complex(x,y)
            z=0
            it=0
            while abs(z)<4 and it<80:
                z=z*z+c
                it+=1
            px[ix,iy]=(int(255*it/80),int(255*((it*params["phi"])%1)),int(255*((it*params["scale"])%1)))
    im.save(out)
if __name__=="__main__":
    seed=sys.argv[1]
    out=sys.argv[2]
    params={"scale":1.618,"phi":1.618}
    render(seed,params,out)
PY_EOF

chmod +x "$PY"
echo "Execute: python3 $PY RAFCODE-𝚽-Δ144 $WORKDIR/renders/test.png"
