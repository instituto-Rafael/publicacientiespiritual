#!/usr/bin/env bash
# rafaelia_sync_audit.sh
# RafaelIA – Sync seguro, auditado, assinado e simbiótico
# Sincroniza SOMENTE arquivos da raiz real do Termux ($HOME)
# NADA de /storage/emulated/0, NADA de UserLand, SOMENTE Termux direto

# Diretório raiz do Termux
SRC_DIR="$HOME"
# Destino remoto configurado no rclone
REMOTE="gdrive:/RAFAELIA_ANCHOR"

# Diretórios e arquivos de controle e auditoria
BASE_DIR="$HOME/rafaelia_sync"
INDEX="$BASE_DIR/rafaelia_sync_index.txt"
HASHLOG="$BASE_DIR/rafaelia_sync_hash.log"
AUDIT="$BASE_DIR/rafaelia_sync_audit.log"
SIG="$BASE_DIR/rafaelia_sync_signatures.txt"
JSONL="$BASE_DIR/rafaelia_sync_index.jsonl"
SIGN_KEY="$HOME/.ssh/rafaelia_ed25519"

# ========================================
# CHECAGENS INICIAIS
# ========================================
# Verifica se o diretório de origem existe
if [ ! -d "$SRC_DIR" ]; then
    echo "[✗] Diretório $SRC_DIR não existe. Abortando."
    exit 1
fi

# Verifica se o rclone está instalado
if ! command -v rclone >/dev/null 2>&1; then
    echo "[✗] rclone não instalado. Abortando."
    exit 1
fi

# Verifica se o remote do Google Drive está configurado
if ! rclone listremotes | grep -q "^gdrive:"; then
    echo "[✗] Remote 'gdrive:' não configurado no rclone. Abortando."
    exit 1
fi

# ========================================
# PREPARO
# ========================================
# Cria diretórios de trabalho
mkdir -p "$BASE_DIR"
mkdir -p "$BASE_DIR/previews"
# Limpa os arquivos de índice e logs
: > "$INDEX"; : > "$HASHLOG"; : > "$AUDIT"; : > "$SIG"; : > "$JSONL"

# Informa ambiente e dados iniciais
echo "===========================================" | tee -a "$AUDIT"
echo "[INICIO] $(date)" | tee -a "$AUDIT"
echo "[🌍 AMBIENTE]" | tee -a "$AUDIT"
echo "SRC:     $SRC_DIR" | tee -a "$AUDIT"
echo "REMOTE:  $REMOTE" | tee -a "$AUDIT"
echo "HOME:    $HOME" | tee -a "$AUDIT"
echo "SYSTEM:  $(uname -a)" | tee -a "$AUDIT"
echo "===========================================" | tee -a "$AUDIT"

# Configurações de execução segura
set -o pipefail
shopt -s nullglob dotglob
trap 'echo "[✗] Erro inesperado $(date)" | tee -a "$AUDIT"' ERR
trap 'echo "[!] Interrompido manualmente $(date)" | tee -a "$AUDIT"; exit 1' INT

start_all=$(date +%s)
count=0
batch=()

# ========================================
# FUNÇÕES AUXILIARES
# ========================================
log()   { echo "$@" | tee -a "$AUDIT"; }
warn()  { echo "[⚠️] $@" | tee -a "$AUDIT"; }
ok()    { echo "[✓] $@" | tee -a "$AUDIT"; }

# Adiciona entrada no JSONL de auditoria
jsonl_append() {
    local f="$1" hash="$2" status="$3"
    local ts=$(date +%s)
    echo "{\"file\":\"$f\",\"hash\":\"$hash\",\"status\":\"$status\",\"timestamp\":$ts}" >> "$JSONL"
}

# Assina ou calcula hash de um arquivo e registra nos logs
sign_file() {
    local f="$1"
    local hash
    # Calcula o hash SHA-256 do arquivo
    hash=$(sha256sum "$f" | awk '{print $1}')
    echo "$hash  $f" >> "$HASHLOG"
    # Se existir chave de assinatura, tenta assinar
    if [ -f "$SIGN_KEY" ]; then
        if ssh-keygen -Y sign -f "$SIGN_KEY" -n rafaelia <<<"$hash" 2>/dev/null >>"$SIG"; then
            ok "Assinado $f"
            jsonl_append "$f" "$hash" "signed"
        else
            warn "Falha ao assinar $f"
            jsonl_append "$f" "$hash" "hash-only"
        fi
    else
        warn "Sem chave Ed25519 – apenas hash $f"
        jsonl_append "$f" "$hash" "hash-only"
    fi
    # Adiciona arquivo ao índice
    echo "$f" >> "$INDEX"
}

# Processa um lote de arquivos (upload + assinatura)
process_batch() {
    local files=("$@")
    local start=$(date +%s)
    log "[→] Lote de ${#files[@]} arquivos"
    for f in "${files[@]}"; do
        # Verifica se o arquivo existe
        if [ -f "$f" ]; then
            log "[...] Enviando: $f"
            # Faz upload com rclone
            if rclone copy "$f" "$REMOTE" --progress --transfers=4; then
                ok "Upload concluído $f"
                sign_file "$f"
            else
                warn "Falha no upload $f"
                jsonl_append "$f" "null" "upload-failed"
            fi
        else
            warn "Arquivo não encontrado $f"
            jsonl_append "$f" "null" "not-found"
        fi
    done
    local end=$(date +%s)
    log "[⏱️] Lote concluído em $((end-start))s"
}

# ========================================
# CLASSIFICAÇÃO DE ARQUIVOS E GERAÇÃO DE PRÉ-VISUALIZAÇÃO
# ========================================

# Define extensões consideradas como código-fonte (serão priorizadas)
code_exts=(sh py js java c cpp h jsm ts css html md jsonc)
# Define extensões de arquivos de texto grandes (geraremos prévia de 300 linhas)
text_exts=(json jsonl log txt db)

# Obter lista de todos os arquivos, ordenados por tamanho, ignorando a pasta de trabalho
mapfile -t all_files < <(find "$SRC_DIR" -maxdepth 3 -type f ! -path "$BASE_DIR/*" -printf "%s %p\n" | sort -n | awk '{print $2}')

# Verifica se nenhum arquivo foi encontrado
if [ ${#all_files[@]} -eq 0 ]; then
    warn "Nenhum arquivo em $SRC_DIR"
    exit 0
fi

# Arrays de classificação
code_files=()
preview_files=()
other_files=()
large_files=()

# Processa cada arquivo encontrado
for file in "${all_files[@]}"; do
    # Obtém a extensão em minúsculas
    ext="${file##*.}"
    ext_lower=$(echo "$ext" | awk '{print tolower($0)}')
    # Verifica se é código-fonte
    if [[ " ${code_exts[*]} " == *" $ext_lower "* ]]; then
        code_files+=("$file")
    # Verifica se é arquivo de texto grande
    elif [[ " ${text_exts[*]} " == *" $ext_lower "* ]]; then
        # Gera arquivo de prévia com as primeiras 300 linhas
        preview_name="$(basename "$file").preview"
        preview_path="$BASE_DIR/previews/$preview_name"
        head -n 300 "$file" > "$preview_path"
        preview_files+=("$preview_path")
        large_files+=("$file")
    else
        # Outros tipos de arquivos
        other_files+=("$file")
    fi
done

# Define a ordem de processamento: código, prévias, outros, arquivos grandes
files_to_process=("${code_files[@]}" "${preview_files[@]}" "${other_files[@]}" "${large_files[@]}")

# ========================
# LOOP PRINCIPAL DE UPLOAD
# ========================
for file in "${files_to_process[@]}"; do
    count=$((count+1))
    batch+=("$file")
    # Processa lote a cada 8 arquivos
    if [ $((count % 8)) -eq 0 ]; then
        process_batch "${batch[@]}"
        batch=()
    fi
    # Checkpoint a cada 5 arquivos
    if [ $((count % 5)) -eq 0 ]; then
        log "[🔍] Checkpoint até $file"
        tail -n5 "$HASHLOG" >> "$AUDIT"
    fi
done

# Processa quaisquer arquivos restantes no lote
if [ ${#batch[@]} -gt 0 ]; then
    process_batch "${batch[@]}"
fi

# ========================================
# FINALIZAÇÃO
# ========================================
end_all=$(date +%s)
log "[🚀] Concluído $(date)"
log "[⏱️] Tempo total $((end_all-start_all))s"
echo "===========================================" >>"$AUDIT"