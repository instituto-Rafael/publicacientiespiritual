import numpy as np
import matplotlib.pyplot as plt
import threading, os, hashlib, json, base64, random, time
from datetime import datetime
from PIL import Image, PngImagePlugin

# Caminho universal e seguro para Android+Termux
FOLDER = os.path.expanduser('~/storage/downloads/cat/')

def fractal_omega(shape=(800,800), preset="hybrid", iter_max=120, cx=0, cy=0, zoom=1.1, seed=None):
    h, w = shape
    xmin, xmax = (-2.0/zoom+cx, 2.0/zoom+cx)
    ymin, ymax = (-2.0/zoom+cy, 2.0/zoom+cy)
    x = np.linspace(xmin, xmax, w)
    y = np.linspace(ymin, ymax, h)
    X, Y = np.meshgrid(x, y)
    C = X + 1j*Y

    if seed: random.seed(seed)
    cj = (random.uniform(-1, 1), random.uniform(-1, 1))
    J = np.full(C.shape, complex(cj[0], cj[1]))
    Z = np.zeros(C.shape, dtype=complex)
    M = np.full(C.shape, True, dtype=bool)
    F = np.zeros(C.shape, dtype=float)
    for i in range(iter_max):
        Z[M] = Z[M]**2 + C[M] + 0.35*J[M] + (np.sin(i*Z[M].imag + cj[0]))*0.01
        F[M] += 1 + np.sin(i+cj[1])*0.5
        M[np.abs(Z) > 2] = False
    noise = np.random.normal(0, 1, C.shape)*0.15
    F = F + noise
    watermark = base64.b64encode(f"{cj[0]:.5f}{cj[1]:.5f}".encode()).decode()
    for i, ch in enumerate(watermark):
        F[-1, i*3:(i+1)*3] = ord(ch) % iter_max
    return F

def salvar_fractal(img, folder, nome, meta={}):
    try:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, nome)
        plt.imsave(path, img, cmap=meta.get("cmap","magma"))
        img_pil = Image.open(path)
        meta_png = PngImagePlugin.PngInfo()
        # Só ASCII nas chaves do meta!
        for k,v in meta.items():
            k_ascii = ''.join([c for c in str(k) if ord(c) < 128])
            meta_png.add_text(k_ascii, str(v))
        img_pil.save(path, pnginfo=meta_png)
        return path
    except Exception as e:
        print(f"[!] Erro ao salvar fractal: {e}")
        return None

def sha_sigma(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except Exception as e:
        return f"error:{e}"

def fractal_worker(idx, params, result_list):
    try:
        fractal_params = {k: v for k, v in params.items() if k in
            ["shape", "preset", "iter_max", "cx", "cy", "zoom", "seed"]}
        folder = params.get("folder", FOLDER)
        img = fractal_omega(**fractal_params)
        meta = fractal_params.copy()
        meta.update({
            "timestamp": datetime.now().isoformat(),
            "preset": params["preset"],
            "cycle_index": idx,
            "cmap": random.choice(["magma","inferno","twilight","cividis","viridis","cubehelix"]),
            "voynich_code": base64.b64encode(os.urandom(9)).decode(),
            "tag14": random.getrandbits(32),
            "author": "Rafael Melo Reis",
            "desc": "Fractal Omega Sigma",  # Aqui só valor, pode Sigma etc.
            "retro": f"CICLO-{idx}"
        })
        nome = f"RAFAELIA_FRACTAL_OMEGA_{idx:04d}_{meta['preset']}.png"
        path = salvar_fractal(img, folder, nome, meta)
        meta["hash_sigma"] = sha_sigma(path)
        meta["filename"] = path
        result_list.append(meta)
        print(f"[✔] Fractal {idx} salvo: {path}")
    except Exception as e:
        print(f"[!] Erro no worker {idx}: {e}")

def gerar_fractais_zipraf(ciclos=4, folder=FOLDER):
    os.makedirs(folder, exist_ok=True)
    threads = []
    results = []
    params_base = [
        {"shape": (800,800), "preset":"hybrid", "iter_max":100, "zoom":1.1, "cx":-0.8, "cy":0.0, "seed":int(time.time())+1, "folder":folder},
        {"shape": (850,850), "preset":"voynich", "iter_max":105, "zoom":1.3, "cx":-0.7, "cy":0.25, "seed":int(time.time())+2, "folder":folder},
        {"shape": (900,900), "preset":"fibonacci", "iter_max":115, "zoom":1.45, "cx":0.1, "cy":-0.7, "seed":int(time.time())+3, "folder":folder},
        {"shape": (950,950), "preset":"tag14", "iter_max":125, "zoom":1.2, "cx":0.35, "cy":-1.0, "seed":int(time.time())+4, "folder":folder},
    ]
    for idx, params in enumerate(params_base[:ciclos]):
        t = threading.Thread(target=fractal_worker, args=(idx+1, params, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    # INDEX JSONL
    index_file = os.path.join(folder, "INDEX_FRACTAL_RAF.jsonl")
    try:
        with open(index_file, "w") as f:
            for meta in results:
                f.write(json.dumps(meta)+"\n")
        # ZIPRAF
        import zipfile
        zipname = os.path.join(folder, f"RAFAELIA_FRACTAIS_ZIPRAF_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as zipf:
            for meta in results:
                if meta["filename"]:
                    zipf.write(meta["filename"], os.path.basename(meta["filename"]))
            zipf.write(index_file, os.path.basename(index_file))
        print(f"\n[Σ] ZIPRAF fractal salvo: {zipname}")
        print(f"[Σ] INDEX JSONL salvo: {index_file}")
        print(f"\n[Σ] Todos fractais: {folder} (abra no seu app de arquivos ou galeria!)")
    except Exception as e:
        print(f"[!] Erro ao salvar zip/index: {e}")

if __name__ == "__main__":
    print("\n[∞FCEA] Gerando fractais RafaelIA...\n")
    gerar_fractais_zipraf(ciclos=4, folder=FOLDER)
    print("\n[Σ] RAFAELIA FRACTAL OMEGA — EXECUÇÃO TOTAL OK!\n")
