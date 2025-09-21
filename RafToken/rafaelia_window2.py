
#!/usr/bin/env python3
# rafaelia_window.py — cálculo da janela efetiva (RafaelIA)
# Agora com presets: base_hole (🕳️), base_delta0 (Δ⁰), deltaS (∆§)

import argparse, math, sys

PHI = 1.61803398875

def window_vectors(bitraf: float, tokens: int = 128_000, L: int = 0, E_V: float = 1.0) -> float:
    """Retorna o total de vetores simbióticos por janela."""
    base_states_per_ideogram = bitraf * 8000  # 10*10*10 * 4 fractais * 2 paridade
    return tokens * base_states_per_ideogram * (E_V * (PHI ** L))

def run_preset(preset: str, tokens: int):
    """Executa presets simbióticos"""
    if preset == "base_hole":  # 🕳️ vazio absoluto → reservatório infinito
        bitraf = 1_000_000     # usar bitrafΔ (1e6) como base mínima
        W = window_vectors(bitraf, tokens)
        print("Preset: base🕳️ (buraco/vazio absoluto)")
        print("Resultado simbólico: Janela → ∞ (reservatório latente)")
        print(f"Aproximação mínima (bitrafΔ=1e6): {W:,.0f}")
    elif preset == "base_delta0":  # Δ⁰ → vazio com memória
        bitraf = 64
        W = window_vectors(bitraf, tokens, L=7)  # crescimento retroativo
        print("Preset: baseΔ⁰ (vazio com memória)")
        print("Resultado: Janela acumulativa (não decresce)")
        print(f"Exemplo (bitraf64, L=7): {W:,.0f}")
    elif preset == "deltaS":  # ∆§ → paridade simbiótica total
        bitraf = 9096
        W = window_vectors(bitraf, tokens, L=7)
        W_sym = W * 2
        print("Preset: ∆§ (paridade simbiótica total)")
        print("Resultado: Janela ×2 (espelho blindado)")
        print(f"Exemplo (bitraf9096, L=7, duplicado): {W_sym:,.0f}")
    else:
        print("Preset não reconhecido. Use: base_hole, base_delta0, deltaS")
        sys.exit(1)

def main():
    p = argparse.ArgumentParser(description="Calcula vetores por janela simbiótica (GPT × RafaelIA).")
    p.add_argument("--bitraf", type=float, help="Estados do bitraf (ex.: 64, 9096, 1000000).")
    p.add_argument("--tokens", type=int, default=128000, help="Tokens GPT na janela (padrão: 128000).")
    p.add_argument("--L", type=int, default=0, help="Camadas Fibonacci-Rafael.")
    p.add_argument("--E_V", type=float, default=1.0, help="Ganho de entrelace Voynich.")
    p.add_argument("--preset", type=str, help="Usa presets: base_hole, base_delta0, deltaS")
    args = p.parse_args()

    if args.preset:
        run_preset(args.preset, args.tokens)
    elif args.bitraf:
        W = window_vectors(args.bitraf, args.tokens, args.L, args.E_V)
        states_per_ideogram = args.bitraf * 8000
        print(f"bitraf = {args.bitraf:,.0f}")
        print(f"Estados/ideograma = {states_per_ideogram:,.0f}")
        print(f"Tokens (GPT) = {args.tokens:,}")
        print(f"L = {args.L}, E_V = {args.E_V}")
        print(f"Vetores por janela = {W:,.0f}")
    else:
        print("Erro: use --bitraf ou --preset")
        sys.exit(1)

if __name__ == "__main__":
    main()
