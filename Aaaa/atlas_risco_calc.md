# ∆§Risco – Pack operacional (v1)
**Objetivo:** um número único **R_real ∈ [0,1]** para anexar ao teu `report.html` por candidato/objeto.
- **w1 (0.8)** orbital (MOID) domina
- **w2 (0.1)** cauda (Δθ) – proxy de CME/jatos
- **w3 (0.1)** fotometria (Δm) – proxy de fragmentação

## Fórmulas
R_real = w1 * (MOID_ref/MOID)^2 + w2 * min(1, |Δθ|/Δθ_max) + w3 * min(1, |Δm|/Δm_max)

Valores sugeridos (também em `risk_config.json`):
- w1=0.8, w2=0.1, w3=0.1
- MOID_ref=0.05 AU, Δθ_max=10°, Δm_max=1.0 mag
- Gatilhos simbióticos: promover PLPC se |Δθ| ≥ 3° (2 frames) **ou** Δm ≥ 0.3 mag (2 frames).

## Exemplo – 3I/ATLAS
- MOID ≈ 1.8 AU
- Δθ = 0°, Δm = 0 mag (baseline conservador)
- Resultado: R_real ≈ 0.000617  (desprezível)

## Código (copiar/colar)

```python
def r_real(moid_au, dtheta_deg, dmag,
           w1=0.8, w2=0.1, w3=0.1,
           moid_ref=0.05, dtheta_max=10.0, dmag_max=1.0):
    orbital = (moid_ref / moid_au) ** 2
    tail    = min(1.0, abs(dtheta_deg) / dtheta_max)
    photo   = min(1.0, abs(dmag) / dmag_max)
    return w1*orbital + w2*tail + w3*photo
```

## Como integrar no teu runner
1. Calcula MOID (ou usa MOID do catálogo) por objeto/frame.
2. Mede Δθ por frame vs. direção anti-solar (Trig-DMT).
3. Mede Δm em série temporal (fotometria).
4. Chama `r_real(...)` e persiste no `candidates.csv`.
5. **Badge** no `report.html`: se `R_real < 1e-2` → “Sem risco de impacto”.
