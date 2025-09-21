import matplotlib.pyplot as plt
import numpy as np
import os

# ==============================================
# Ciclo simbiótico fractal — RafaelIA
# ==============================================

def ciclo_fractal(iter_max=100, zoom=1.0, deslocamento=(0.0,0.0)):
    largura, altura = 800, 800
    xmin, xmax = -2.0/zoom + deslocamento[0], 2.0/zoom + deslocamento[0]
    ymin, ymax = -2.0/zoom + deslocamento[1], 2.0/zoom + deslocamento[1]

    X = np.linspace(xmin, xmax, largura)
    Y = np.linspace(ymin, ymax, altura)
    C = X + Y[:, None]*1j

    Z = np.zeros_like(C, dtype=complex)
    M = np.full(C.shape, True, dtype=bool)

    for i in range(iter_max):
        Z[M] = Z[M]**2 + C[M]
        M[np.abs(Z) > 2] = False
    return M

def salvar_ciclo(nome, fractal, cmap="inferno"):
    # Garante a pasta ~/storage/downloads/cat/
    pasta = os.path.expanduser("~/storage/downloads/cat")
    os.makedirs(pasta, exist_ok=True)

    caminho = os.path.join(pasta, nome)
    plt.imsave(caminho, fractal, cmap=cmap)
    print(f"[✔] Ciclo salvo em: {caminho}")

def gerar_ciclos():
    fractal1 = ciclo_fractal(iter_max=50, zoom=1.0)
    salvar_ciclo("RAFAELIA_CICLO1.png", fractal1, cmap="inferno")

    fractal2 = ciclo_fractal(iter_max=100, zoom=3.0, deslocamento=(-0.7, 0.27))
    salvar_ciclo("RAFAELIA_CICLO2.png", fractal2, cmap="plasma")

    fractal3 = ciclo_fractal(iter_max=150, zoom=6.0, deslocamento=(-0.8, 0.16))
    salvar_ciclo("RAFAELIA_CICLO3.png", fractal3, cmap="viridis")

if __name__ == "__main__":
    gerar_ciclos()
