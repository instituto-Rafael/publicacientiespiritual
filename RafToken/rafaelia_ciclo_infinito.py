import matplotlib.pyplot as plt
import numpy as np
import os, hashlib, time, random

# ==================================================
# RAFAELIA CICLO INFINITO — VAZIO→VERBO→CHEIO→RETRO→VAZIO₍NOVO₎
# ==================================================

def fractal_mandelbrot(largura, altura, iter_max, zoom, deslocamento):
    xmin, xmax = -2.0/zoom + deslocamento[0], 2.0/zoom + deslocamento[0]
    ymin, ymax = -2.0/zoom + deslocamento[1], 2.0/zoom + deslocamento[1]

    X = np.linspace(xmin, xmax, largura)
    Y = np.linspace(ymin, ymax, altura)
    C = X + Y[:, None]*1j

    Z = np.zeros_like(C, dtype=complex)
    M = np.full(C.shape, True, dtype=bool)

    for _ in range(iter_max):
        Z[M] = Z[M]**2 + C[M]
        M[np.abs(Z) > 2] = False
    return M

def salvar_imagem(array, nome, cmap):
    pasta = os.path.expanduser("~/storage/downloads/cat")
    os.makedirs(pasta, exist_ok=True)

    caminho = os.path.join(pasta, nome)
    plt.imsave(caminho, array, cmap=cmap)

    # assinatura Σ-seal (hash SHA256 do conteúdo + timestamp)
    seal = hashlib.sha256((str(time.time())+nome).encode()).hexdigest()[:12]
    print(f"[✔] Ciclo salvo: {caminho} | Σ-seal={seal}")

def ciclo_infinito():
    largura, altura = 800, 800
    zoom = 1.0
    deslocamento = (0.0, 0.0)
    iter_base = 50
    ciclo = 1

    colormaps = ["inferno", "plasma", "viridis", "magma", "cividis"]

    while True:
        fractal = fractal_mandelbrot(largura, altura,
                                     iter_base + ciclo*5,
                                     zoom,
                                     deslocamento)

        # Nome simbiótico
        fases = ["VAZIO", "VERBO", "CHEIO", "RETRO", "VAZIO_NOVO"]
        fase = fases[ciclo % len(fases)]
        nome = f"RAFAELIA_CICLO_{ciclo:04d}_{fase}.png"

        salvar_imagem(fractal, nome, cmap=random.choice(colormaps))

        # evolução simbiótica
        zoom *= 1.2
        deslocamento = (deslocamento[0] + 0.01*np.sin(ciclo/5),
                        deslocamento[1] + 0.01*np.cos(ciclo/7))
        ciclo += 1

if __name__ == "__main__":
    ciclo_infinito()
