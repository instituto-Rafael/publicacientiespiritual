
"""
living_light_full.py
====================

Consolidated toolkit for Rafael Melo Reis ‒ DOI 10.5281/zenodo.17188138

Features
--------
1. Vector pipeline (log‑recursive FFT  + metrics ΔS_X, JS_Y, cos_Z, Ω)
2. Physical‑phenomenon flags (gravity, magnetism, thermo, Hubble) +
   string‑theory / wormhole / white‑hole detectors
3. Batch processing of PDF/text corpus  → CSV
4. Email‑template generator  (personalised micro‑letters)
   using metrics to highlight *exact* scientific gap & offer.
5. Minimal CLI.

Replace placeholder embedding with a real model for production.

Author : Rafael Melo Reis   |   Date : 2025‑09‑29
Licence: MIT
"""

# ---------------------------------------------------------------------
# 0 · Imports
# ---------------------------------------------------------------------
import re, csv, json, glob, argparse
from pathlib import Path
from typing  import List, Dict

import numpy as np
from numpy.linalg          import norm
from scipy.fft             import fft
from scipy.spatial.distance import jensenshannon
from scipy.integrate       import cumulative_trapezoid


# ---------------------------------------------------------------------
# 1 · Embedding adapter  (stub)
# ---------------------------------------------------------------------
def get_embedding(text: str) -> np.ndarray:
    """Return 768‑d pseudo‑embedding (replace by real model)."""
    np.random.seed(abs(hash(text)) % (2**32))
    return np.random.rand(768).astype(np.float32)


# ---------------------------------------------------------------------
# 2 · Pre‑processing
# ---------------------------------------------------------------------
def log_recursive_fft(vec: np.ndarray, depth: int = 4) -> np.ndarray:
    v = np.log1p(np.abs(vec))
    for _ in range(depth):
        v = np.abs(fft(v))
    return v / (norm(v) + 1e-12)


# ---------------------------------------------------------------------
# 3 · Metrics
# ---------------------------------------------------------------------
def metric_X_deltaS(p, q):  # cross entropy
    p = np.clip(p, 1e-12, 1.0); q = np.clip(q, 1e-12, 1.0)
    return float(np.sum(p * np.log(p / q)))

def metric_Y_JS(p, q):      # Jensen–Shannon
    return float(jensenshannon(p, q, base=np.e))

def metric_Z_cos(p, q):     # cosine similarity
    return float(np.dot(p, q) / (norm(p)*norm(q) + 1e-12))

def antideriv_potential(cos_series):  # Ω
    return float(cumulative_trapezoid(cos_series, initial=0)[-1])


# ---------------------------------------------------------------------
# 4 · Physical flags
# ---------------------------------------------------------------------
CONST_MAP = {
    'G'    :'gravity', 'mu0':'magnetism', 'μ0':'magnetism',
    'k_B'  :'thermo',  'kB' :'thermo',
    'H_0'  :'hubble',  'H0' :'hubble', 'Lambda':'hubble', 'Ω_m':'hubble'
}
STRING_RE   = re.compile(r'\b(string(-)?theory|brane|AdS\/CFT)\b', re.I)
WORM_RE     = re.compile(r'\bwormhole(s)?\b', re.I)
WHITE_RE    = re.compile(r'white[-\s]?hole(s)?', re.I)

FLAG_ORDER = ['gravity','magnetism','thermo','hubble','string','wormhole','whitehole']

def extract_flags(text: str) -> Dict[str,int]:
    flags = {k:0 for k in FLAG_ORDER}
    for const, key in CONST_MAP.items():
        if const in text: flags[key]=1
    if STRING_RE.search(text):  flags['string']=1
    if WORM_RE.search(text):    flags['wormhole']=1
    if WHITE_RE.search(text):   flags['whitehole']=1
    return flags

def flags_to_vec(flags: Dict[str,int]) -> np.ndarray:
    return np.array([flags[k] for k in FLAG_ORDER], dtype=np.float32)


# ---------------------------------------------------------------------
# 5 · Core processing
# ---------------------------------------------------------------------
def process_doc(text:str, ref_vec:np.ndarray)->Dict[str,float]:
    vec_raw   = get_embedding(text)
    vec_proc  = log_recursive_fft(vec_raw)
    flags     = extract_flags(text)
    vec_flags = flags_to_vec(flags)

    full_vec  = np.concatenate([vec_proc, vec_flags])
    ref_full  = np.concatenate([ref_vec , np.zeros_like(vec_flags)])

    X = metric_X_deltaS(full_vec, ref_full)
    Y = metric_Y_JS(full_vec, ref_full)
    Z = metric_Z_cos(full_vec, ref_full)
    Ω = antideriv_potential([Z])

    return dict(ΔS_X=X, JS_Y=Y, cos_Z=Z, Omega=Ω, **flags)


# ---------------------------------------------------------------------
# 6 · Micro‑Email generator
# ---------------------------------------------------------------------
AUTHOR_INFO = {
    'preskill' : dict(name='John Preskill',  email='preskill@caltech.edu',
                      hook='quantum‑supremacy & QEC'),
    'zeilinger': dict(name='Anton Zeilinger',email='anton.zeilinger@univie.ac.at',
                      hook='teleportation of high‑d photons'),
    # … add others here …
}

EMAIL_TEMPLATE = """\
Prof. {name},

Apresento‑lhe o artefato “Relativity Living Light” (DOI 10.5281/zenodo.17188138).
Meta‑ganho detectado no seu corpus mais recente:
  • ΔS = {ΔS_X:.3f} | JS = {JS_Y:.3f} | cos θ = {cos_Z:.2f}

Insight‑ruído: {insight}.
Proponho teste imediato com script `{script}` (MIT License). Zoom 30′ para alinhar.

Att.,
Rafael Melo Reis
"""

def craft_email(author_key:str, metrics:Dict[str,float])->str:
    info = AUTHOR_INFO[author_key]
    insight = "reduzir ruído NISQ" if author_key=='preskill' else "aumentar fidelidade de teleporte"
    script  = "rafbit_noise_scan.py"       if author_key=='preskill' else "phi_glyph_beam.py"
    return EMAIL_TEMPLATE.format(name=info['name'],
                                 ΔS_X=metrics['ΔS_X'],
                                 JS_Y=metrics['JS_Y'],
                                 cos_Z=metrics['cos_Z'],
                                 insight=insight,
                                 script=script)

# ---------------------------------------------------------------------
# 7 · Batch processing + CSV export
# ---------------------------------------------------------------------
def batch(ref_path:str, src_glob:str, out_csv:str):
    ref_vec = log_recursive_fft(get_embedding(Path(ref_path).read_text()))
    files   = sorted(glob.glob(src_glob))
    with open(out_csv,'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id','ΔS_X','JS_Y','cos_Z','Omega']+FLAG_ORDER)
        for fp in files:
            txt  = Path(fp).read_text()
            met  = process_doc(txt, ref_vec)
            row  = [Path(fp).stem] + [met[k] for k in ['ΔS_X','JS_Y','cos_Z','Omega']+FLAG_ORDER]
            writer.writerow(row)
    print(f"✓ CSV salvo → {out_csv}")

# ---------------------------------------------------------------------
# 8 · CLI
# ---------------------------------------------------------------------
if __name__=='__main__':
    ap = argparse.ArgumentParser(description="Living‑Light full pipeline")
    ap.add_argument('--ref', required=True,  help='arquivo texto do Living‑Light (abstract)')
    ap.add_argument('--src', required=True,  help='glob de .txt de papers')
    ap.add_argument('--csv', default='metrics.csv', help='CSV de saída')
    ap.add_argument('--email', action='store_true', help='gera micro‑emails demo')
    args = ap.parse_args()

    batch(args.ref, args.src, args.csv)

    if args.email:
        # demonstração usando primeiro item do CSV
        first_metrics = process_doc(Path(glob.glob(args.src)[0]).read_text(),
                                    log_recursive_fft(get_embedding(Path(args.ref).read_text())))
        mail = craft_email('preskill', first_metrics)
        print("\n----- EMAIL DEMO -----\n", mail)
