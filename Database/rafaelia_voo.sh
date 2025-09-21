#!/data/data/com.termux/files/usr/bin/bash
# RAFAELIA VOO — protótipo
# Requisitos (Termux): pkg install python ffmpeg git -y
# Python deps (vai instalar local): pip install --user pillow numpy ed25519

set -e
WORKDIR="${PWD}/rafaelia_voo"
mkdir -p "$WORKDIR/renders"
mkdir -p "$WORKDIR/data"
CSV="$WORKDIR/hyperformas.csv"
PY="$WORKDIR/raf_engine.py"
MANIFEST="$WORKDIR/manifest.json"
JSONL="$WORKDIR/rafbits.jsonl"

# --- cria CSV (se não existir) com as 30 hyperformas (usa conteúdo gerado acima) ---
if [ ! -f "$CSV" ]; then
  cat > "$CSV" <<'CSV_EOF'
id,name,short_desc,omega,scale,phi,noise,entropy,tags
1,H1_giro,rotacional tesseract warp,144.0,1.618,1.618,0.005,0.12,seed,spin
2,H2_emaranha,emaranhamento fractal,72.0,1.414,2.718,0.07,0.18,web,emaranha
3,H3_ressonar,resonância harmónica,36.0,2.0,1.333,0.02,0.10,resonance,hum
4,H4_echo,eco temporal,288.0,0.786,2.0,0.09,0.22,time,echo
5,H5_tessera,projeção tesseract,144.0,1.0,1.0,0.01,0.08,tesseract,core
6,H6_filigrana,detalhamento finíssimo,9.0,3.333,1.272,0.12,0.35,detail,lace
7,H7_vórtice,vortex topológico,55.5,0.9,2.5,0.06,0.20,vortex,flow
8,H8_pulsar,pulso rítmico fractal,333.0,1.21,3.14,0.03,0.09,pulse,beat
9,H9_grafeno,malha condutora fractal,11.0,4.0,1.73,0.15,0.40,mesh,conduct
10,H10_emergir,auto-organização,101.0,0.618,2.236,0.04,0.13,emergent,organize
11,H11_selo,assinatura simbiótica,1440.0,0.1,1.0,0.00,0.02,seal,signature
12,H12_subtrama,camadas ocultas,12.0,2.5,1.9,0.11,0.30,hidden,layer
13,H13_fenda,time-warp fissure,7.0,0.55,2.91,0.2,0.45,warp,rift
14,H14_corpo,gravidade local param,220.0,1.77,1.41,0.025,0.11,gravity,mass
15,H15_arco,curvatura fase,33.3,1.05,2.05,0.035,0.10,curve,phase
16,H16_metria,ritmo entropia,13.0,0.95,1.95,0.06,0.19,metric,entropy
17,H17_vazio,void resonance,199.0,5.0,2.5,0.2,0.5,void,deep
18,H18_rede,sinapse fractal,2.718,3.5,1.618,0.085,0.25,network,synapse
19,H19_tempo,tempo local,60.0,0.88,0.999,0.013,0.07,time,local
20,H20_luz,camada fotônica,420.0,1.333,3.0,0.01,0.05,photon,light
21,H21_ecossistema,interação multiagente,8.8,2.22,1.44,0.09,0.28,eco,agents
22,H22_sopro,vento simbólico,14.0,0.77,2.0,0.04,0.12,breath,wind
23,H23_magneto,linha de fluxo,88.0,1.999,1.618,0.06,0.2,magnetic,flux
24,H24_fronteira,limiar dimensional,7.7,0.66,2.666,0.14,0.36,threshold,limit
25,H25_espelho,reflexo inverso,144.0,1.111,1.111,0.02,0.09,mirror,inverse
26,H26_semente,gerador fractal,3.14,9.0,2.0,0.005,0.03,seed,genesis
27,H27_âncora,paridade ritual,0.618,0.333,1.0,0.0,0.01,anchor,parity
28,H28_pedra,estabilidade fractal,22.0,6.0,1.2,0.18,0.4,stone,stable
29,H29_nebula,espuma cósmica,300.0,2.8,3.7,0.09,0.27,nebula,foam
30,H30_omega,hiperforma ômega,999.0,0.999,0.999,0.001,0.02,omega,final
CSV_EOF
fi

# --- cria o engine python ---
cat > "$PY" <<'PY_EOF'
#!/usr/bin/env python3
# raf_engine.py - converte texto -> RafBits -> JSONL e gera render PNG protótipo
import sys, json, os, math, hashlib
from PIL import Image, ImageDraw
import numpy as np

def text_to_rafbits(text):
    # simplificado: hash -> chunks de 10 bits
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()
    bits = bin(int(h,16))[2:].zfill(256)
    rafbits = []
    for i in range(0, len(bits), 10):
        chunk = bits[i:i+10]
        if len(chunk) < 10:
            chunk = chunk.ljust(10, '0')
        val = int(chunk,2)
        rafbits.append({
            "raw": chunk,
            "value": val,
            "fibonacci_index": val & 0xF,
            "emotion": (val >> 4) & 0x3,
            "parity": (val >> 6) & 0x1,
            "energy": (val >> 7) & 0x3,
            "sealed": (val >> 9) & 0x1
        })
    return rafbits

def save_jsonl(rafbits, outpath):
    with open(outpath, 'w') as f:
        for r in rafbits:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def render_fractal(seed, params, outpath, size=800):
    # protótipo: usa Mandelbrot-like formula com params influencing color
    w, h = size, size
    im = Image.new("RGB", (w,h), "black")
    px = im.load()
    scale = params.get("scale",1.0)
    noise = params.get("noise",0.05)
    phi = params.get("phi",1.618)
    # map pixels to complex plane
    for ix in range(w):
        for iy in range(h):
            x = (ix - w/2) / (w/4) * (1/scale)
            y = (iy - h/2) / (h/4) * (1/scale)
            c = complex(x*math.cos(phi) - y*math.sin(phi), x*math.sin(phi)+y*math.cos(phi))
            z = complex(0,0)
            it = 0
            maxit = 80
            while abs(z) < 4 and it < maxit:
                # modified iteration influenced by noise and seed hash
                z = z*z + c + complex(noise*math.sin(it+seed%10), noise*math.cos(it+seed%7))
                it += 1
            color = (int(255*(it/maxit)), int(255*((it*phi)%1)), int(255*((it*scale)%1)))
            px[ix,iy] = color
    im.save(outpath)

def seed_number(seedstr):
    return sum(ord(c) for c in seedstr) % 9973

def main():
    if len(sys.argv) < 4:
        print("usage: raf_engine.py \"seed-string\" hyper_id outdir")
        sys.exit(1)
    seed = sys.argv[1]
    hyper_id = sys.argv[2]
    outdir = sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    # read selected hyper from CSV in same folder
    csvpath = os.path.join(os.path.dirname(__file__), "hyperformas.csv")
    hyper = None
    with open(csvpath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = [p.strip() for p in line.split(",")]
            if parts[0] == hyper_id:
                hyper = {
                    "id": parts[0],
                    "name": parts[1],
                    "omega": float(parts[3]),
                    "scale": float(parts[4]),
                    "phi": float(parts[5]),
                    "noise": float(parts[6])
                }
                break
    if not hyper:
        print("hyper id not found; using default H1")
        hyper = {"id":"1","name":"H1_giro","omega":144.0,"scale":1.618,"phi":1.618,"noise":0.005}
    # example: use seed + hyper to create rafbits
    rafbits = text_to_rafbits(seed + "_" + hyper["name"])
    save_jsonl(rafbits, os.path.join(outdir, "rafbits.jsonl"))
    # render fractal
    s = seed_number(seed)
    outimg = os.path.join(outdir, f"render_h{hyper['id']}.png")
    print("Rendering:", outimg, "params:", hyper)
    render_fractal(s, hyper, outimg, size=800)
    # manifest minimal
    manifest = {
        "seed": seed,
        "hyper": hyper,
        "signature": "Σ:PLACEHOLDER"
    }
    with open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, ensure_ascii=False, indent=2)
    print("Done. Outputs in", outdir)

if __name__ == "__main__":
    main()
PY_EOF

# --- tornar executável e instruções ---
chmod +x "$PY"
echo "Pronto. Para gerar um render de teste:"
echo "  cd $WORKDIR"
echo "  python3 raf_engine.py \"RAFCODE-𝚽-α144-VOO-ΔR\" 1 renders"
echo ""
echo "Outputs: $WORKDIR/renders (PNG), $WORKDIR/rafbits.jsonl, $WORKDIR/manifest.json"
