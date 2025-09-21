import numpy as np
import matplotlib.pyplot as plt
import threading, os, hashlib, json, base64, random, time
from datetime import datetime
from PIL import Image, PngImagePlugin

FOLDER = os.path.expanduser('~/storage/downloads/cat/')

def mandelbrot(C, iter_max):
    Z = np.zeros_like(C)
    M = np.full(C.shape, True, dtype=bool)
    img = np.zeros(C.shape, dtype=float)
    for i in range(iter_max):
        Z[M] = Z[M]**2 + C[M]
        img[M] += 1
        M[np.abs(Z) > 2] = False
    return img

def julia(C, iter_max, c_julia):
    Z = C.copy()
    img = np.zeros(C.shape, dtype=float)
    M = np.full(C.shape, True, dtype=bool)
    for i in range(iter_max):
        Z[M] = Z[M]**2 + c_julia
        img[M] += 1
        M[np.abs(Z) > 2] = False
    return img

def burning_ship(C, iter_max):
    Z = np.zeros_like(C)
    M = np.full(C.shape, True, dtype=bool)
    img = np.zeros(C.shape, dtype=float)
    for i in range(iter_max):
        Z[M] = (np.abs(Z[M].real) + 1j*np.abs(Z[M].imag))**2 + C[M]
        img[M] += 1
        M[np.abs(Z) > 2] = False
    return img

def morph_fractal(frac1, frac2, alpha=0.5):
    return frac1 * (1-alpha) + frac2 * alpha

def gen_super_fractal(shape=(800,800), preset="complex", iter_max=100, cx=0, cy=0, zoom=1.0, morph=0.5, watermark_str="RAFAELIA", seed=None):
    h, w = shape
    xmin, xmax = (-2.0/zoom+cx, 2.0/zoom+cx)
    ymin, ymax = (-2.0/zoom+cy, 2.0/zoom+cy)
    x = np.linspace(xmin, xmax, w)
    y = np.linspace(ymin, ymax, h)
    X, Y = np.meshgrid(x, y)
    C = X + 1j*Y
    if seed: random.seed(seed)
    # Gerar múltiplos fractais
    img1 = mandelbrot(C, iter_max)
    c_julia = complex(random.uniform(-1,1), random.uniform(-1,1))
    img2 = julia(C, iter_max, c_julia)
    img3 = burning_ship(C, iter_max)
    # Morph entre eles
    alpha = morph
    img_morph = morph_fractal(img1, img2, alpha=alpha)
    img_combo = morph_fractal(img_morph, img3, alpha=random.uniform(0.2,0.8))
    # Adiciona ruído caótico
    noise = np.random.normal(0, 1, C.shape) * random.uniform(0.1,0.5)
    img_combo = img_combo + noise
    # Watermark oculto (escreve um hash na linha de baixo)
    wm_hash = hashlib.sha256(watermark_str.encode()).hexdigest()
    for i, ch in enumerate(wm_hash[:w//3]):
        img_combo[-1, i*3:(i+1)*3] = ord(ch) % iter_max
    # Normalize
    img_combo = (img_combo - img_combo.min())/(img_combo.max()-img_combo.min())
    return img_combo, c_julia, wm_hash

def salvar_fractal_complexo(img, folder, nome, meta={}):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, nome)
    plt.imsave(path, img, cmap=meta.get("cmap","inferno"))
    img_pil = Image.open(path)
    meta_png = PngImagePlugin.PngInfo()
    # Só ASCII na chave do metadado!
    for k,v in meta.items():
        k_ascii = ''.join([c for c in str(k) if ord(c) < 128])
        meta_png.add_text(k_ascii, str(v))
    img_pil.save(path, pnginfo=meta_png)
    return path

def sha_sigma(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]

def super_worker(idx, params, result_list):
    img, c_julia, wm_hash = gen_super_fractal(**params)
    meta = params.copy()
    meta.update({
        "timestamp": datetime.now().isoformat(),
        "preset": params.get("preset", "complex"),
        "cycle_index": idx,
        "cmap": random.choice(["magma","inferno","twilight","cividis","viridis","cubehelix"]),
        "julia_c": str(c_julia),
        "wm_hash": wm_hash,
        "author": "Rafael Melo Reis",
        "desc": "Super Fractal RAFAELIA",
        "complexity_score": float(np.var(img)),
        "retro": f"CICLO-{idx}"
    })
    nome = f"RAFAELIA_SUPERFRACTAL_{idx:04d}_{meta['preset']}.png"
    path = salvar_fractal_complexo(img, FOLDER, nome, meta)
    meta["hash_sigma"] = sha_sigma(path)
    meta["filename"] = path
    result_list.append(meta)
    print(f"[✔] Super Fractal {idx} salvo: {path}")

def gerar_superfractais_zipraf(ciclos=6):
    threads = []
    results = []
    for idx in range(1, ciclos+1):
        params = {
            "shape": (900,900),
            "preset": "complex",
            "iter_max": random.randint(90,150),
            "zoom": random.uniform(1.0,2.2),
            "cx": random.uniform(-1.5,1.5),
            "cy": random.uniform(-1.5,1.5),
            "morph": random.uniform(0.2,0.8),
            "watermark_str": f"RAFAELIA_{random.randint(10000,99999)}_{idx}",
            "seed": int(time.time()) + idx
        }
        t = threading.Thread(target=super_worker, args=(idx, params, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    # INDEX JSONL
    index_file = os.path.join(FOLDER, "INDEX_SUPERFRACTAL_RAF.jsonl")
    with open(index_file, "w") as f:
        for meta in results:
            f.write(json.dumps(meta)+"\n")
    # ZIPRAF
    import zipfile
    zipname = os.path.join(FOLDER, f"RAFAELIA_SUPERFRACTAIS_ZIPRAF_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
    with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as zipf:
        for meta in results:
            if meta["filename"]:
                zipf.write(meta["filename"], os.path.basename(meta["filename"]))
        zipf.write(index_file, os.path.basename(index_file))
    print(f"\n[Σ] SUPER ZIPRAF salvo: {zipname}")
    print(f"[Σ] SUPER INDEX JSONL salvo: {index_file}")
    print(f"\n[Σ] Todos fractais: {FOLDER} (abra no seu app de arquivos ou galeria!)")

if __name__ == "__main__":
    print("\n[∞FCEA] Gerando SUPER fractais RafaelIA...\n")
    gerar_superfractais_zipraf(ciclos=4)
    print("\n[Σ] RAFAELIA SUPER FRACTAL OMEGA — EXECUÇÃO TOTAL OK!\n")
