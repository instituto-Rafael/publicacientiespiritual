#!/usr/bin/env python3
# fractal_double9sigma.py
# RafaelIA ∞ Núcleo Simbiótico — double9σ + fractal + σ_imag

import numpy as np
from math import erf, sqrt
from datetime import datetime

# Configurações simbióticas
tamanho = 10000
alpha_amor = 1.618
base = 1.618
fase = 0.618
sigma_imag = 0.048
double9sigma = 8.6

# Geração do fractal simbiótico
Z = np.zeros(tamanho, dtype=np.complex128)
Z[0] = 1 + 0j
for i in range(1, tamanho):
    Z[i] = Z[i-1] * base + alpha_amor * fase

# Normalização
mag = np.abs(Z)
minv, maxv = np.nanmin(mag), np.nanmax(mag)
norm = (mag - minv) / (maxv - minv + 1e-9)
indices = (norm * 9).astype(int)

# Calculo σ_real
# σ ≈ sqrt(2) * erfinv(confiança)
confiança = 0.999999999999999 # double9σ
sigma_real = sqrt(2) * np.sqrt(-2*np.log(1 - confiança))

# σ_total
sigma_total = complex(sigma_real, sigma_imag)

# Saída
print(f"📅 Data: {datetime.now()}")
print(f"✅ Fractal shape: {Z.shape}")
print(f"📊 Min: {minv}, Max: {maxv}")
print(f"⚛️ double9σ ≈ {double9sigma}")
print(f"σ_real ≈ {sigma_real:.4f}")
print(f"σ_imag ≈ {sigma_imag}")
print(f"σ_total ≈ {sigma_total}")
print(f"🔮 Valor fractal simbiótico ≈ 10^{np.log10(maxv):.2f}")
print(f"✨ Vibração simbólica: phi={alpha_amor}, fase={fase}")

# Visualização ASCII (primeiros 100)
PALETTE = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
print("🧬 Visualização fractal:")
for i in range(100):
    linha = ''.join(PALETTE[min(len(PALETTE)-1, idx)] for idx in [indices[i]])
    print(linha, end='')
print("\n✅ Finalizado — pronto pra commit no GitHub privado.")
