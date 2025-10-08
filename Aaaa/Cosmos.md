∆RafaelVerboΩ — bora cravar o ∆§risco real com conta fria, visível e auditável. Foco: 3I/ATLAS (C/2025 N1), risco para a Terra e adjacências.

1) Risco orbital de impacto (Terra)

Dados-chave públicos e estáveis

Distância mínima Terra–cometa: ≈ 1,8 UA (≈ 269.3 milhões km).

Velocidade interestelar típica perto da órbita da Terra: ~58–60 km/s.

Órbita hiperbólica (visitante, não ligado ao Sol).


Teste 1 — distância vs. incerteza

Mesmo admitindo um termo não-gravitacional extremo (jatos) A₁ ≈ 10⁻⁷ au/d², o desvio integrado em ~120 dias é da ordem de ~10⁵ km (cálculo padrão: ).

Comparado ao percurso de ~2,69×10⁸ km, isso é ~4×10⁻⁴ do gap.

Resultado: o objeto continua centenas de milhões de km longe da Terra.
Conclusão: Risco de impacto: zero operacional.


Teste 2 — MOID normalizado (regra de bolso)

Score ≈ .

Com MOID efetivo >> 0,05 UA (aqui a ordem é ~1,8 UA), o score cai para ~7,7×10⁻⁴ antes de ponderar incerteza; ponderando incerteza realista (≪1), fica <10⁻⁴.
Conclusão: estatisticamente nulo.


2) Riscos “ocultos” que não são impacto

Esses valem monitoramento científico, não pânico:

(A) Fragmentação do núcleo

Pode gerar surtos de brilho e múltiplas plumas.

Risco prático: confundir fragmentos/poeira com “desvio orbital” (falso alarme).

Monitor: fotometria diferencial  > 0,3 mag em ≤24 h, repetido ≥2 frames.


(B) Jatos direcionais / CME

Mudam a cauda/coma, não a órbita de modo perigoso.

Risco prático: interpretar ∆θ (ângulo da cauda vs. anti-solar) como “manobra”.

Monitor:  por ≥2 frames ou ±36 h de um CME.


(C) Química incomum (CO₂/H₂O alta)

Explica atividade longe do Sol; não aumenta risco de impacto.

Risco prático: superestimar tamanho/atividade sem modelar voláteis.


3) Índice ∆§Risco (plug-and-play para teu pipeline)

Quer um número de 0 a 1 para grudar no report.html?

\text{R}_\text{real}= 
w_1 \underbrace{\Big(\tfrac{0{,}05}{\text{MOID}}\Big)^{2}}_{\text{orbital}} \;
+\; w_2 \underbrace{\min\!\Big(1,\tfrac{\Delta \theta}{10^\circ}\Big)}_{\text{cauda/CME}} \;
+\; w_3 \underbrace{\min\!\Big(1,\tfrac{|\Delta m|}{1{,}0}}\Big)_{\text{fragmentação}}

Sugerir , , .

Para 3I/ATLAS:

termo orbital ≈ ~7,7×10⁻⁴,

nenhum pico robusto de  confirmado como anômalo persistente,

sem  repetido grande reportado.
Sai  (redondeando para cima): risco desprezível.



4) Gatilhos de promoção (PLEC/PLPC) — quando “acende”

Promover PLEC (prudência) se: SNR ↑, trilha/estrutura coerente, erro astrométrico ↓.

Promover PLPC (paradoxo) se:  em ≥2 frames ou  mag com repetição.

Ouro investigativo = PLEC=1 ∧ PLPC=1. Ainda assim, risco para a Terra não muda se a geometria continua a >1 UA.


5) Em uma linha

Risco real para a Terra por 3I/ATLAS: ≈ 0.

Risco de interpretação (falso alarme): médio se não filtrar  e  por repetição/seeing.

Risco científico bom (descobertas): alto — plumas discretas, química exótica, resposta a CME.


Se quiser, eu coloco esse cálculo ∆§Risco dentro do teu runner.py (com os pesos e gatilhos acima) e te devolvo um report.html que já sai com a coluna R_real por candidato e um selo “Sem Risco de Impacto” quando .

