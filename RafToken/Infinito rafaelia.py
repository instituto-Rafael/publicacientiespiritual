import matplotlib.pyplot as plt
import numpy as np
import os
import hashlib
from datetime import datetime

# ==============================================
# Ciclo simbiótico fractal — RafaelIA ∞
# ==============================================

def ciclo_fractal(iter_max=100, zoom=1.0, deslocamento=(0.0,0.0), preset="base"):
    largura, altura = 800, 800
    xmin, xmax = -2.0/zoom + deslocamento[0], 2.0/zoom + deslocamento[0]
    ymin, ymax = -2.0/zoom + deslocamento[1], 2.0/zoom + deslocamento[1]

    X = np.linspace(xmin, xmax, largura)
    Y = np.linspace(ymin, ymax, altura)
    C = X + Y[:, None]*1j

    Z = np.zeros_like(C, dtype=complex)
    M = np.full(C.shape, True, dtype=bool)
    # Coloração simbiótica
    img = np.zeros(C.shape)

    for i in range(iter_max):
        Z[M] = Z[M]**2 + C[M]
        img[np.abs(Z) < 2] += 1   # Cada ponto "cheio" soma valor
        M[np.abs(Z) > 2] = False

    # Presets de cor/camadas (blindagem simbiótica)
    if preset == "base_hole":
        cmap = "twilight_shifted"
    elif preset == "base_delta0":
        cmap = "plasma"
    elif preset == "deltaS":
        cmap = "viridis"
    elif preset == "voynich":
        cmap = "cubehelix"
    elif preset == "rafael_fibonacci":
        cmap = "cividis"
    else:
        cmap = "inferno"
    return img, cmap

def assinar_arquivo(path):
    """Assina arquivo com SHA256 e marca Σ-RAFAELIA no nome"""
    with open(path, "rb") as f:
        hash = hashlib.sha256(f.read()).hexdigest()[:12]
    base, ext = os.path.splitext(path)
    novo = f"{base}_Σ_{hash}{ext}"
    os.rename(path, novo)
    return novo

def gerar_ciclos_infinito(pasta="~/storage/downloads/cat/", presets=None):
    pasta = os.path.expanduser(pasta)
    os.makedirs(pasta, exist_ok=True)
    if presets is None:
        presets = ["base", "base_hole", "base_delta0", "deltaS", "voynich", "rafael_fibonacci"]
    deslocamentos = [
        (0.0,0.0),
        (-0.7,0.27),
        (-0.8,0.16),
        (-1.3,0.05),
        (0.3,-0.7),
        (-1.4, 0.0)
    ]
    zoom_ini = 1.0
    iter_ini = 50
    ciclo = 1
    while True:
        for preset, desloc in zip(presets, deslocamentos):
            iter_max = iter_ini + ciclo * 15
            zoom = zoom_ini * (1.4 + ciclo*0.1)
            fractal, cmap = ciclo_fractal(iter_max=iter_max, zoom=zoom, deslocamento=desloc, preset=preset)
            agora = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome = f"RAFAELIA_CICLO_{ciclo:04d}_{preset}_{agora}.png"
            caminho = os.path.join(pasta, nome)
            plt.imsave(caminho, fractal, cmap=cmap)
            final = assinar_arquivo(caminho)
            print(f"[Σ] Salvo e assinado: {final}")
            ciclo += 1

if __name__ == "__main__":
    try:
        gerar_ciclos_infinito()
    except KeyboardInterrupt:
        print("\n[∞] Atlas fractal simbiótico interrompido por Rafael!")
