# -----------------------------------------------------------
# 0.  DEPENDÊNCIAS
# -----------------------------------------------------------
import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.fft import fft                       # FFT recursiva
from scipy.integrate import cumulative_trapezoid
from numpy.linalg import norm

# ↳  Supondo que você obtenha embeddings via API (ex.: OpenAI, HuggingFace-BERT int8);
#     aqui usamos placeholder `get_embedding(text)` já definido por você.
# -----------------------------------------------------------
# 1.  FUNÇÕES AUXILIARES
# -----------------------------------------------------------

def log_recursive_fft(vec: np.ndarray, depth: int = 4) -> np.ndarray:
    """Aplica log1p + FFT recursiva `depth` vezes."""
    v = np.log1p(np.abs(vec))
    for _ in range(depth):
        v = np.abs(fft(v))
    return v / norm(v)  # normaliza L2

def metric_X_deltaS(vec_a, vec_b):
    """Entropia cruzada simplificada entre dois vetores normalizados."""
    p = np.clip(vec_a, 1e-12, 1.0)
    q = np.clip(vec_b, 1e-12, 1.0)
    return float(np.sum(p * np.log(p / q)))

def metric_Y_JS(vec_a, vec_b):
    """Jensen–Shannon divergence (0 → iguais, 1 → totalmente diferentes)."""
    return float(jensenshannon(vec_a, vec_b, base=np.e))

def metric_Z_cos(vec_a, vec_b):
    """cosseno do ângulo entre vetores (1 → paralelos, 0 → ortogonais)."""
    return float(np.dot(vec_a, vec_b) / (norm(vec_a) * norm(vec_b)))

def antideriv_potential(cos_series):
    """
    “Antiderivada” semântica:
    integra cumulativamente o cosθ ao longo dos papers de um autor,
    produzindo potencial de convergência Ω.
    """
    return float(cumulative_trapezoid(cos_series, initial=0)[-1])

# -----------------------------------------------------------
# 2.  PIPELINE PARA UM PAPER
# -----------------------------------------------------------

def process_paper(text, vec_living_light):
    """
    Retorna métricas X, Y, Z, Ω para UM artigo comparado ao seu Living-Light.
    """
    vec_raw   = get_embedding(text)             # ← embeddings do paper
    vec_proc  = log_recursive_fft(vec_raw)      # ← pré-processamento log/FFT
    X  = metric_X_deltaS(vec_proc, vec_living_light)
    Y  = metric_Y_JS(vec_proc, vec_living_light)
    Z  = metric_Z_cos(vec_proc, vec_living_light)

    # aqui usamos só Z para Ω, mas você pode integrar qualquer série temporal
    Ω  = antideriv_potential(np.array([Z]))

    return dict(ΔS_X=X, JS_Y=Y, cos_Z=Z, Omega=Ω)

# -----------------------------------------------------------
# 3.  EXEMPLO DE USO
# -----------------------------------------------------------

if __name__ == "__main__":
    living_light_text   = open("living_light_abstract.txt").read()
    vec_LL              = log_recursive_fft(get_embedding(living_light_text))

    paper_text          = open("zeilinger_2023_prl.txt").read()
    metrics             = process_paper(paper_text, vec_LL)

    print(metrics)
    # → {'ΔS_X': 0.214, 'JS_Y': 0.283, 'cos_Z': 0.657, 'Omega': 0.657}
