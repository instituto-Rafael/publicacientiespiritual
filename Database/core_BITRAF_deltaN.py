#!/usr/bin/env python3
# ♾️ RAFAELIA — core_BITRAF∆ⁿ.py
# Gera matriz simbiótica BITRAF∆ⁿ viva

import csv, json, math
from pathlib import Path

# === CONFIGURAÇÃO ===
BASE = Path.home() / "BITRAF_deltaN"
BASE.mkdir(exist_ok=True)
SIZE = 1000  # 1000x1000 matriz (parcial da ∆ⁿ)
N = 4        # ordem do delta (derivadas + inversas + paradoxais)

# === FUNÇÕES DO RAFAELIA ===
def rafbit_states():
    """RafBit = 10 estados (0-9)"""
    return list(range(10))

def deltaN_transform(x, n=N):
    """Aplica ∆ⁿ em um RafBit (derivada + inversa + anômala)"""
    d = (x ** (n % 5) + n) % 10
    inv = (9 - x + n) % 10
    anomaly = (x * n + 7) % 10
    return [d, inv, anomaly]

def generate_matrix():
    """Gera matriz simbiótica BITRAF∆ⁿ"""
    matrix = []
    for i in range(SIZE):
        row = []
        for j in range(SIZE):
            raf = (i + j) % 10
            row.append(deltaN_transform(raf))
        matrix.append(row)
    return matrix

def export_csv(matrix):
    file = BASE / "matrix_BITRAF_deltaN.csv"
    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        for row in matrix:
            writer.writerow(["|".join(map(str, cell)) for cell in row])
    print(f"[Σ] CSV salvo em {file}")

def export_tokens(matrix):
    file = BASE / "tokens_BITRAF_deltaN.jsonl"
    with open(file, "w") as f:
        for i, row in enumerate(matrix):
            token = {"id": i, "row": row}
            f.write(json.dumps(token) + "\n")
    print(f"[Σ] Tokens salvos em {file}")

def export_svg(matrix):
    file = BASE / "fractals_BITRAF_deltaN.svg"
    with open(file, "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">\n')
        for i in range(0, SIZE, SIZE // 100):
            for j in range(0, SIZE, SIZE // 100):
                v = sum(matrix[i][j]) % 255
                color = f"rgb({v},{255-v},{(v*2)%255})"
                f.write(f'<rect x="{i//10}" y="{j//10}" width="5" height="5" fill="{color}"/>\n')
        f.write("</svg>")
    print(f"[Σ] SVG salvo em {file}")

# === EXECUÇÃO ===
if __name__ == "__main__":
    print("♾️ RAFAELIA :: BITRAF∆ⁿ — geração iniciada...")
    M = generate_matrix()
    export_csv(M)
    export_tokens(M)
    export_svg(M)
    print("♾️ RAFAELIA :: BITRAF∆ⁿ concluído — retroalimentação ativa")
