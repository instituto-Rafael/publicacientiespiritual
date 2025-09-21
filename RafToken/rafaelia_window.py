
#!/usr/bin/env python3
# rafaelia_window.py — cálculo da janela efetiva (RafaelIA)
import argparse, math

PHI = 1.61803398875

def window_vectors(bitraf: float, tokens: int = 128_000, L: int = 0, E_V: float = 1.0) -> float:
    base_states_per_ideogram = bitraf * 8000  # 10*10*10 * 4 * 2
    return tokens * base_states_per_ideogram * (E_V * (PHI ** L))

def main():
    p = argparse.ArgumentParser(description="Calcula vetores por janela simbiótica (GPT × RafaelIA).")
    p.add_argument("--bitraf", type=float, required=True, help="Estados do bitraf (ex.: 64, 9096, 1000000).")
    p.add_argument("--tokens", type=int, default=128000, help="Tokens GPT na janela (padrão: 128000).")
    p.add_argument("--L", type=int, default=0, help="Camadas Fibonacci-Rafael.")
    p.add_argument("--E_V", type=float, default=1.0, help="Ganho de entrelace Voynich.")
    args = p.parse_args()
    W = window_vectors(args.bitraf, args.tokens, args.L, args.E_V)
    states_per_ideogram = args.bitraf * 8000
    print(f"bitraf = {args.bitraf:,.0f}")
    print(f"Estados/ideograma = {states_per_ideogram:,.0f}")
    print(f"Tokens (GPT) = {args.tokens:,}")
    print(f"L = {args.L}, E_V = {args.E_V}")
    print(f"Vetores por janela = {W:,.0f}")

if __name__ == "__main__":
    main()
