
"""
patch.py  –  Living‑Light × Literature Mapper
---------------------------------------------
Compute semantic + physical‑phenomenon similarity between a reference
text (e.g. your Living‑Light DOI abstract) and a set of papers.

Features
========
• Embedding adapter (placeholder `get_embedding`)
• Log‑scale recursive FFT normalisation
• Metrics:
    ΔS_X  – cross entropy
    JS_Y  – Jensen‑Shannon divergence
    cos_Z – cosine similarity
• Antiderivative Ω (semantic convergence potential)
• Extraction of physical constants & terms from LaTeX snippets
    • Gravity      (G)
    • Magnetism    (μ0, B‑field)
    • Thermodynamics (k_B, dS/dE)
    • Cosmology / Hubble (H_0, Λ, Ω_m)
• Detection flags for:
    • String theory (strings, branes, AdS/CFT…)
    • Wormholes
    • White holes
• Pipeline utilities + CSV export.

Author : Rafael Melo Reis  (2025‑09‑29)
License: MIT
"""

import re
import json
import csv
import numpy as np
from pathlib import Path
from typing import List, Dict
from numpy.linalg import norm
from scipy.fft import fft
from scipy.spatial.distance import jensenshannon
from scipy.integrate import cumulative_trapezoid

# ----------------------------------------------------------------------
# 0. Embedding adapter  (replace with real model call)
# ----------------------------------------------------------------------
def get_embedding(text: str) -> np.ndarray:
    """Return a dummy 768‑d vector for demo purposes.
    Replace by a true embedding call (e.g. OpenAI, HuggingFace)."""
    np.random.seed(abs(hash(text)) % (2**32))
    return np.random.rand(768).astype(np.float32)

# ----------------------------------------------------------------------
# 1. Pre‑processing – log + recursive FFT
# ----------------------------------------------------------------------
def log_recursive_fft(vec: np.ndarray, depth: int = 4) -> np.ndarray:
    v = np.log1p(np.abs(vec))
    for _ in range(depth):
        v = np.abs(fft(v))
    return v / (norm(v) + 1e-12)

# ----------------------------------------------------------------------
# 2. Metrics X, Y, Z, Ω
# ----------------------------------------------------------------------
def metric_X_deltaS(p, q):
    p = np.clip(p, 1e-12, 1.0)
    q = np.clip(q, 1e-12, 1.0)
    return float(np.sum(p * np.log(p / q)))

def metric_Y_JS(p, q):
    return float(jensenshannon(p, q, base=np.e))

def metric_Z_cos(p, q):
    denom = (norm(p) * norm(q) + 1e-12)
    return float(np.dot(p, q) / denom)

def antideriv_potential(cos_series: List[float]) -> float:
    return float(cumulative_trapezoid(cos_series, initial=0)[-1])

# ----------------------------------------------------------------------
# 3. Physical‑term extraction
# ----------------------------------------------------------------------
CONST_MAP = {
    'G':        'gravity',
    'mu0':      'magnetism',
    'μ0':       'magnetism',
    'k_B':      'thermo',
    'kB':       'thermo',
    'H_0':      'hubble',
    'Lambda':   'hubble',
    'Ω_m':      'hubble',
    'H0':       'hubble'
}

STRING_TERMS   = re.compile(r'\b(string(-)?theory|brane|AdS\/CFT)\b', re.I)
WORMHOLE_TERMS = re.compile(r'\bwormhole(s)?\b', re.I)
WHITEHOLE_TERMS= re.compile(r'white[-\s]?hole(s)?', re.I)

def extract_terms(text_or_latex: str) -> Dict[str, int]:
    flags = {'gravity':0, 'magnetism':0, 'thermo':0, 'hubble':0,
             'string':0, 'wormhole':0, 'whitehole':0}
    # constants
    for const, key in CONST_MAP.items():
        if const in text_or_latex:
            flags[key] = 1
    # keywords
    if STRING_TERMS.search(text_or_latex):   flags['string'] = 1
    if WORMHOLE_TERMS.search(text_or_latex): flags['wormhole'] = 1
    if WHITEHOLE_TERMS.search(text_or_latex):flags['whitehole'] = 1
    return flags

def one_hot_flags(flag_dict: Dict[str,int]) -> np.ndarray:
    order = ['gravity','magnetism','thermo','hubble',
             'string','wormhole','whitehole']
    return np.array([flag_dict[k] for k in order], dtype=np.float32)

# ----------------------------------------------------------------------
# 4. Main processing function
# ----------------------------------------------------------------------
def process_document(text: str, reference_vec: np.ndarray) -> Dict[str,float]:
    vec_raw  = get_embedding(text)
    vec_proc = log_recursive_fft(vec_raw)

    flags    = extract_terms(text)
    vec_phys = one_hot_flags(flags)

    full_vec = np.concatenate([vec_proc, vec_phys])
    ref_full = np.concatenate([reference_vec, np.zeros_like(vec_phys)])

    X  = metric_X_deltaS(full_vec, ref_full)
    Y  = metric_Y_JS(full_vec, ref_full)
    Z  = metric_Z_cos(full_vec, ref_full)
    Ω  = antideriv_potential([Z])

    return dict(ΔS_X=X, JS_Y=Y, cos_Z=Z, Omega=Ω, **flags)

# ----------------------------------------------------------------------
# 5. Batch utility + CSV export
# ----------------------------------------------------------------------
def batch_process(texts: List[str],
                  ids:   List[str],
                  ref_text: str,
                  csv_path: Path):
    ref_vec = log_recursive_fft(get_embedding(ref_text))
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ['id','ΔS_X','JS_Y','cos_Z','Omega',
                  'gravity','magnetism','thermo','hubble',
                  'string','wormhole','whitehole']
        writer.writerow(header)
        for doc_id, txt in zip(ids, texts):
            m = process_document(txt, ref_vec)
            row = [doc_id] + [m[k] for k in header[1:]]
            writer.writerow(row)

# ----------------------------------------------------------------------
# 6. CLI minimal
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse, glob
    ap = argparse.ArgumentParser(description="Living‑Light literature mapper")
    ap.add_argument('--ref',  required=True, help='reference text file')
    ap.add_argument('--src',  required=True, help='glob for source txt files (e.g. "./papers/*.txt")')
    ap.add_argument('--out',  default='metrics.csv', help='output CSV')
    args = ap.parse_args()

    ref_text  = Path(args.ref).read_text()
    file_list = sorted(glob.glob(args.src))
    ids  = [Path(p).stem for p in file_list]
    txts = [Path(p).read_text() for p in file_list]

    batch_process(txts, ids, ref_text, Path(args.out))
    print(f"[✓] metrics saved → {args.out}")
