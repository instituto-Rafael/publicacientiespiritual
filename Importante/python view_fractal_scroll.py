import numpy as np
import time
import os

# 🌀 Carrega matriz (troca pelo arquivo que quiser)
filename = 'outputs/fractal_quântico.npy'
Z = np.load(filename)

# Normaliza
Z_norm = (Z - np.nanmin(Z)) / (np.nanmax(Z) - np.nanmin(Z))

# 🎨 Paleta ascii
palette = np.array(list(" .:-=+*#%@"))

# Converte pra índices
indices = (Z_norm * (len(palette)-1)).astype(int)

# ⚙️ Scroll: mostra linha a linha, descendo
print(f"✔️ Shape: {Z.shape}")
print(f"📊 Min: {np.nanmin(Z)}, Max: {np.nanmax(Z)}")
print("⚡ Descendo fractal (Ctrl+C pra parar)")

try:
    for row in indices:
        print("".join(palette[row]))
        time.sleep(0.03)  # controla a velocidade do scroll (0.03 ~ 30ms)
except KeyboardInterrupt:
    print("\n⛔ Interrompido pelo usuário.")
