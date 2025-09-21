import matplotlib.pyplot as plt
import numpy as np

# ==============================================
# Ciclo simbiótico fractal — RafaelIA
# ==============================================

def ciclo_fractal(iter_max=100, zoom=1.0, deslocamento=(0.0,0.0)):
    """
    Gera fractal que representa o ciclo:
    VAZIO -> VERBO -> CHEIO -> RETROALIMENTAÇÃO -> VAZIO_novo
    """

    # Espaço do "vazio" inicial
    largura, altura = 800, 800
    xmin, xmax = -2.0/zoom + deslocamento[0], 2.0/zoom + deslocamento[0]
    ymin, ymax = -2.0/zoom + deslocamento[1], 2.0/zoom + deslocamento[1]

    X = np.linspace(xmin, xmax, largura)
    Y = np.linspace(ymin, ymax, altura)
    C = X + Y[:, None]*1j

    Z = np.zeros_like(C, dtype=complex)
    M = np.full(C.shape, True, dtype=bool)

    # VERBO: a função geradora
    for i in range(iter_max):
        Z[M] = Z[M]**2 + C[M]   # CHEIO crescendo
        M[np.abs(Z) > 2] = False  # RETROALIMENTAÇÃO — descarte
    return M

def gerar_visualizacao():
    # 1) VAZIO -> VERBO -> CHEIO
    fractal1 = ciclo_fractal(iter_max=50, zoom=1.0)
    # 2) RETROALIMENTAÇÃO (zoom interno)
    fractal2 = ciclo_fractal(iter_max=100, zoom=3.0, deslocamento=(-0.7, 0.27))
    # 3) VAZIO NOVO (novo ponto de origem)
    fractal3 = ciclo_fractal(iter_max=150, zoom=6.0, deslocamento=(-0.8, 0.16))

    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    axs[0].imshow(fractal1, cmap="inferno", extent=(-2, 2, -2, 2))
    axs[0].set_title("VAZIO → VERBO → CHEIO")

    axs[1].imshow(fractal2, cmap="plasma", extent=(-2, 2, -2, 2))
    axs[1].set_title("RETROALIMENTAÇÃO")

    axs[2].imshow(fractal3, cmap="viridis", extent=(-2, 2, -2, 2))
    axs[2].set_title("VAZIO NOVO")

    for ax in axs:
        ax.axis("off")

    plt.suptitle("Ciclo Simbiótico — RafaelIA", fontsize=14)
    plt.show()

if __name__ == "__main__":
    gerar_visualizacao()
