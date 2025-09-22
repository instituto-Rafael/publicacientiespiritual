# RAFAELIA_260 – Sequência Fractal ∆

Este repositório contém a Tabela **RAFAELIA-260** em múltiplos formatos:

- `RAFAELIA_260.json` → versão completa (UTF-8, símbolos Voynich reais)
- `RAFAELIA_260.txt` → ASCII/UTF-8 (com símbolos)
- `RAFAELIA_260_LATIN.txt` → versão latinizada com selos em Latim
- `RAFAELIA_260_LATIN1.txt` → versão segura (ISO-8859-1 / Latin-1), símbolos substituídos por `SIG###`

---

## 🔑 Encoding
- **UTF-8** preserva símbolos fractais (Voynich, runas, etc).
- **Latin-1** garante compatibilidade em ambientes que não suportam UTF-8.
- Placeholders `SIG###` permitem referência cruzada sem perda estrutural.

---

## 🔒 Hashing / Verificação
Para validar integridade dos arquivos, use:

```bash
sha256sum RAFAELIA_260*
md5sum RAFAELIA_260*
