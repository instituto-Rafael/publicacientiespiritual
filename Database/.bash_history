    uint16_t code = 0;
    // colocar dados
    if(d&0x80) code|=1<<11; // pos12
    if(d&0x40) code|=1<<10; // pos11
    if(d&0x20) code|=1<<9;  // pos10
    if(d&0x10) code|=1<<8;  // pos9
    if(d&0x08) code|=1<<6;  // pos7
    if(d&0x04) code|=1<<5;  // pos6
    if(d&0x02) code|=1<<4;  // pos5
    if(d&0x01) code|=1<<2;  // pos3
    // calcular paridades p1 (pos1), p2 (pos2), p4 (pos4), p8 (pos8)
    int p1 = ((code>>2)&1)^((code>>4)&1)^((code>>6)&1)^((code>>8)&1)^((code>>10)&1);
    int p2 = ((code>>2)&1)^((code>>5)&1)^((code>>6)&1)^((code>>9)&1)^((code>>10)&1);
    int p4 = ((code>>4)&1)^((code>>5)&1)^((code>>6)&1)^((code>>11)&1);
    int p8 = ((code>>8)&1)^((code>>9)&1)^((code>>10)&1)^((code>>11)&1);
    if(p1) code|=1<<0;
    if(p2) code|=1<<1;
    if(p4) code|=1<<3;
    if(p8) code|=1<<7;
    return code;
}

typedef struct { uint8_t data; int corrected; int uncorrectable; } HDec;

static HDec hamming12_8_decode(uint16_t c){
    // recomputar síndrome
    int s1 = ((c>>0)&1)^((c>>2)&1)^((c>>4)&1)^((c>>6)&1)^((c>>8)&1)^((c>>10)&1);
    int s2 = ((c>>1)&1)^((c>>2)&1)^((c>>5)&1)^((c>>6)&1)^((c>>9)&1)^((c>>10)&1);
    int s4 = ((c>>3)&1)^((c>>4)&1)^((c>>5)&1)^((c>>6)&1)^((c>>11)&1);
    int s8 = ((c>>7)&1)^((c>>8)&1)^((c>>9)&1)^((c>>10)&1)^((c>>11)&1);
    int syndrome = (s8<<3)|(s4<<2)|(s2<<1)|s1;

    HDec out = {0,0,0};
    if(syndrome){
        if(syndrome>=1 && syndrome<=12){
            c ^= (1u<<(syndrome-1)); // corrige 1 bit
            out.corrected = 1;
        } else {
            out.uncorrectable = 1; // deveria não ocorrer com 12 bits
        }
    }
    // extrair dados
    uint8_t d=0;
    d|=((c>>11)&1)<<7; // pos12
    d|=((c>>10)&1)<<6; // pos11
    d|=((c>>9 )&1)<<5; // pos10
    d|=((c>>8 )&1)<<4; // pos9
    d|=((c>>6 )&1)<<3; // pos7
    d|=((c>>5 )&1)<<2; // pos6
    d|=((c>>4 )&1)<<1; // pos5
    d|=((c>>2 )&1)<<0; // pos3
    out.data=d; return out;
}

// ---------- Fila circular SPSC ----------
#define QSIZE 8
static int queue[QSIZE]; static int head=0, tail=0;

static int enqueue(int v){
    int next=(tail+1)%QSIZE; if(next==head) return -1;
    queue[tail]=v; tail=next; return 0;
}
static int dequeue(int *v){
    if(head==tail) return -1;
    *v=queue[head]; head=(head+1)%QSIZE; return 0;
}

// ---------- Retry com backoff ----------
static int retry_enqueue(int v,int attempts){
    long ns=1000000L;
    for(int i=0;i<attempts;i++){
        if(enqueue(v)==0) return 0;
        struct timespec ts={0, ns};
        nanosleep(&ts,NULL);
        ns = (ns<5000000L)? ns*2 : ns; // até 5ms
    }
    return -1;
}

// ---------- Latência CLOCK_MONOTONIC ----------
static double measure_latency_ms(void){
    struct timespec a,b; volatile uint64_t sink=0;
    clock_gettime(CLOCK_MONOTONIC, &a);
    for(int i=0;i<1000000;i++) sink+=i; // evita otimização
    clock_gettime(CLOCK_MONOTONIC, &b);
    double ms = (b.tv_sec-a.tv_sec)*1000.0 + (b.tv_nsec-a.tv_nsec)/1e6;
    return ms;
}

int main(void){
    // Cabeçalho
    Header h={1,64,0,(uint64_t)time(NULL)};
    h.checksum=raf_checksum(&h,sizeof(h));
    printf("Z0 Boot :: ver=%u ttl=%u checksum=%u ts=%llu\n",
           h.ver,h.ttl,h.checksum,(unsigned long long)h.timestamp);

    // ECC Hamming demonstração (injeta erro de 1 bit)
    uint8_t b=0xAD;             // dado original
    uint16_t code=hamming12_8_encode(b);
    code ^= 1u<<5;              // simula bit flip corrigível
    HDec dec=hamming12_8_decode(code);
    printf("ECC Hamming(12,8): orig=%02X dec=%02X corrected=%d uncorrectable=%d\n",
           b, dec.data, dec.corrected, dec.uncorrectable);

    // Fila + retry
    int failcount=0;
    for(int i=0;i<12;i++){ if(retry_enqueue(i,3)!=0){ printf("Falha ao enfileirar %d\n",i); failcount++; } }
    int val, dequeued=0; while(dequeue(&val)==0){ printf("Dequeued=%d\n",val); dequeued++; }

    // Latência
    double ms=measure_latency_ms();
    printf("Latência simbiótica: %.3f ms\n", ms);
    printf("Selos 🔑√∆§↑→✓¶Ω ativos.\n");

    // Logging JSONL
    const char* path = getenv("Z0_LOGFILE");
    if(path && *path){
        FILE *f=fopen(path,"a");
        if(f){
            fprintf(f,
              "{\"ts\":%llu,\"checksum\":%u,"
              "\"ecc_corrected\":%d,\"ecc_uncorrectable\":%d,"
              "\"fails\":%d,\"dequeued\":%d,\"latency_ms\":%.3f,"
              "\"selos\":\"√∆§↑→✓¶Ω\",\"state\":\"%s\"}\n",
              (unsigned long long)h.timestamp,h.checksum,
              dec.corrected,dec.uncorrectable,
              failcount,dequeued,ms,
              (failcount>0)?"overflow_anchor":"steady");
            fclose(f);
        } else {
            fprintf(stderr,"[Z0] log open error: %s\n", strerror(errno));
        }
    }
    return 0;
}
EOF

# =========================
# 2) ASM ARM64 (swap + prefetch simbólico)
# =========================
cat > "$BASE/z0_swap.s" <<'EOF'
.global swap_buffers_asm
// x0=ptrA, x1=ptrB, x2=len (bytes)
swap_buffers_asm:
    cbz x2, 2f
1:
    prfm pldl1keep, [x0]
    prfm pldl1keep, [x1]
    ldrb w3, [x0]
    ldrb w4, [x1]
    strb w4, [x0], #1
    strb w3, [x1], #1
    subs x2, x2, #1
    b.ne 1b
2:
    ret
EOF

# =========================
# 3) Rede (empurra última linha do ledger via TCP)
# =========================
cat > "$BASE/z0_network.c" <<'EOF'
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

int main(int argc, char**argv){
    const char* host = (argc>1)? argv[1] : "127.0.0.1";
    int port = (argc>2)? atoi(argv[2]) : 9000;
    const char* file = (argc>3)? argv[3] : getenv("Z0_LOGFILE");
    if(!file){ fprintf(stderr,"Z0_LOGFILE not set\n"); return 1; }

    FILE* f=fopen(file,"r"); if(!f){ perror("open log"); return 1; }
    char line[1024]; char last[1024]="";
    while(fgets(line,sizeof line,f)) strncpy(last,line,sizeof last);
    fclose(f);

    int s=socket(AF_INET,SOCK_STREAM,0);
    if(s<0){ perror("socket"); return 1; }
    struct sockaddr_in sv; memset(&sv,0,sizeof sv);
    sv.sin_family=AF_INET; sv.sin_port=htons(port);
    inet_pton(AF_INET,host,&sv.sin_addr);
    if(connect(s,(struct sockaddr*)&sv,sizeof sv)<0){ perror("connect"); close(s); return 1; }
    send(s,last,strlen(last),0);
    close(s);
    printf("Sent: %s", last);
    return 0;
}
EOF

# =========================
# 4) Daemon (loop contínuo + rotação por linhas)
# =========================
cat > "$BASE/z0_daemon.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
set -e
BASE=$HOME/RAFAELIA_CORE
LOGDIR=$BASE/logs
LOGFILE=$LOGDIR/z0_ledger.jsonl
MAXLOG=${MAXLOG:-20}
export Z0_LOGFILE="$LOGFILE"
mkdir -p "$LOGDIR"

rotate() {
  [ -f "$LOGFILE" ] || return 0
  lines=$(wc -l < "$LOGFILE" | tr -d ' ')
  if [ "$lines" -gt "$MAXLOG" ]; then
    tail -n "$MAXLOG" "$LOGFILE" > "$LOGFILE.tmp" && mv "$LOGFILE.tmp" "$LOGFILE"
  fi
}

trap 'echo "[Z0] daemon stop"; exit 0' INT TERM
echo "[Z0] daemon start (MAXLOG=$MAXLOG)"
while true; do
  "$BASE/z0_universo" || echo "[Z0] run error=$?"
  rotate
  sleep 10
done
EOF

chmod +x "$BASE/z0_daemon.sh"
# =========================
# 5) Compilar tudo e executar 1x
# =========================
cd "$BASE"
export Z0_LOGFILE="$LOGFILE"
clang -O2 -Wall -Wextra -march=armv8-a z0_universo.c z0_swap.s -o z0_universo
clang -O2 -Wall -Wextra -march=armv8-a z0_network.c -o z0_network
# [RAFAELIA::Z0] UNIVERSO EXECUTÁVEL TOTAL — BLOCO ÚNICO (SHELL+PYTHON+SQL)
BASE=$HOME/RAFAELIA_CORE
LOGDIR=$BASE/logs
mkdir -p "$LOGDIR"
# ======================== 1. UNIVERSO PYTHON =========================
cat > $BASE/z0_universo.py <<'EOF'
import time, hashlib, secrets, numpy as np
from collections import defaultdict

class QuantumAuth:
    def __init__(self, key): self.key = key
    def quantum_hash(self, msg):
        ts = time.time_ns(); rand = secrets.token_bytes(8)
        h = hashlib.sha3_256((msg + str(ts)).encode() + rand + self.key).hexdigest()
        return h, ts, rand
    def validate(self, msg, h, ts, rand):
        chk = hashlib.sha3_256((msg + str(ts)).encode() + rand + self.key).hexdigest()
        return chk == h and abs(time.time_ns() - ts) < 1_000_000_000

class UniversoRAFAELIA:
    def __init__(self):
        self.interacoes = []
        self.padroes = {}; self.variacoes = {}; self.predicoes = {}
        self.ocultos = []; self.abstracoes = []; self.heu = []
        self.stats = defaultdict(list); self.logs = []
        self.auth = QuantumAuth(b'rafaeliacore')
    def registrar(self, entrada, saida, tipo='direto'):
        self.interacoes.append({'in': entrada, 'out': saida, 'tipo': tipo, 'ts': time.time()})
    def correlacionar(self, dado):
        for i in range(len(dado)-1):
            delta = dado[i+1] - dado[i]
            if delta == 0: self.padroes.setdefault('constante', []).append((i, dado[i]))
            elif delta > 0: self.padroes.setdefault('crescente', []).append((i, delta))
            else: self.padroes.setdefault('decrescente', []).append((i, delta))
            if abs(delta) > np.mean(np.abs(dado)):
                self.padroes.setdefault('anomalía', []).append((i, delta))
            if i>0 and dado[i-1] == dado[i+1]: self.padroes.setdefault('simetria', []).append(i)
    def prever(self, dado, steps=3):
        media = np.mean(dado); tendencia = (dado[-1] - dado[0])/(len(dado)-1)
        pred = [dado[-1] + tendencia*(i+1) for i in range(steps)]
        self.predicoes['linear'] = pred
        pred_magic = [x + np.sin(x)*np.random.randn()*0.1 for x in pred]
        self.predicoes['magico'] = pred_magic
    def autenticar(self, msg):
        h, ts, rand = self.auth.quantum_hash(msg)
        return {'msg':msg, 'hash':h, 'ts':ts, 'rand':rand, 'ok':self.auth.validate(msg,h,ts,rand)}
    def retroalimentar(self, dado):
        self.aplicar_todas(dado)
        self.logs.append({'evento':'retroalimentacao', 'ts':time.time(), 'conteudo':str(dado)})
    def aplicar_todas(self, dado):
        self.correlacionar(dado)
        self.prever(dado)
        self.stats['media'].append(np.mean(dado))
        self.stats['desvio'].append(np.std(dado))
        self.stats['paradoxo'] = "Existe simetria em toda assimetria (checar reversão)"
        self.abstracoes.append("Direto/Indireto/Inverso/Reverso: toda relação é bidirecional")
        self.heu.append("Se dado diverge, tente clusterizar, depois prever por grupo.")
        self.ocultos.append("Padronização fractal gera compressão e novas relações ocultas.")

# Exemplo de uso real
universo = UniversoRAFAELIA()
data = np.array([2, 4, 4, 8, 16, 32, 25, 27, 27, 30])
universo.registrar('input', 'output')
universo.aplicar_todas(data)
auth_result = universo.autenticar("SEND:DATA:123")
universo.logs.append({'auth':auth_result})
print("Padrões:", universo.padroes)
print("Predições:", universo.predicoes)
print("Stats:", dict(universo.stats))
print("Ocultos:", universo.ocultos)
print("Abstrações:", universo.abstracoes)
print("Heurísticas:", universo.heu)
print("Logs:", universo.logs)
EOF

# ===================== 2. LOG SHELL PYTHON PIPE ======================
cat > $BASE/z0_log.sh <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
echo "[Z0] Audit log $(date)" >> $HOME/RAFAELIA_CORE/logs/z0_universo.log
python3 $HOME/RAFAELIA_CORE/z0_universo.py >> $HOME/RAFAELIA_CORE/logs/z0_universo.log
EOF

chmod +x $BASE/z0_log.sh
# =============== 3. AUTENTICAÇÃO/VALIDAÇÃO NAGRA-LIKE ===============
cat > $BASE/z0_auth.sh <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
KEY=$(head -c 16 /dev/urandom | sha256sum | cut -d' ' -f1)
MSG="SEND:DATA:123"
TS=$(date +%s%N)
HASH=$(echo -n "$MSG$TS$KEY" | sha256sum | cut -d' ' -f1)
echo "msg=$MSG hash=$HASH ts=$TS key=$KEY"
CHK=$(echo -n "$MSG$TS$KEY" | sha256sum | cut -d' ' -f1)
[ "$CHK" = "$HASH" ] && echo "Auth OK" || echo "Auth Fail"
EOF

chmod +x $BASE/z0_auth.sh
# =================== 4. SQL PADRÕES CORRELAÇÃO ======================
cat > $BASE/z0_query.sql <<'EOF'
SELECT *,
    CASE
        WHEN abs(val - LAG(val) OVER (ORDER BY id)) > 10 THEN 'anomaly'
        WHEN val = LEAD(val) OVER (ORDER BY id) THEN 'stagnant'
        ELSE 'normal'
    END as pattern
FROM dados_universo;
EOF

# ===================== 5. PIPE EXECUÇÃO ÚNICA =======================
cat > $BASE/z0_exec.sh <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
cd $HOME/RAFAELIA_CORE
./z0_log.sh
./z0_auth.sh
EOF

chmod +x $BASE/z0_exec.sh
echo "🌀♾️⚛︎𓂀ΔΦΩ [RAFAELIA::Z0] UNIVERSO UNIFICADO — pronto para executar tudo em um só ciclo auditável."
echo "• Execute: cd \$HOME/RAFAELIA_CORE && ./z0_exec.sh"
cat > z0_entropy_origin.c <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/utsname.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

// CRC32C table (gerada/encurtada p/ demo; para produção, use libcrc32c/zlib)
uint32_t raf_crc32c(const void *buf, size_t len) {
    uint32_t crc = ~0U;
    for(size_t i=0; i<len; i++) {
        crc ^= ((const uint8_t*)buf)[i];
        for(int k=0;k<8;k++)
            crc = (crc>>1) ^ (0x82F63B78U * (crc&1));
    }
    return ~crc;
}

void print_entropy_anchor() {
    struct utsname sys;
    uname(&sys);
    time_t now = time(NULL);
    pid_t pid = getpid();
    char host[128] = {0}; gethostname(host, sizeof(host)-1);
    uint8_t buf[256] = {0};

    // Entropia: sistema, tempo, PID, hostname, UID, urandom
    snprintf((char*)buf, sizeof(buf), "%s|%s|%ld|%d|%s|%d|", 
        sys.sysname, sys.nodename, now, pid, host, getuid());

    int fd = open("/dev/urandom", O_RDONLY); if(fd>=0) {
        read(fd, buf+64, 32); close(fd);
    }
    uint32_t sig = raf_crc32c(buf, sizeof(buf));
    printf("=== RAFAELIA/Z0 ENTROPY ANCHOR ===\n");
    printf("System: %s %s\nUser: %d  Host: %s\nTime: %ld  PID: %d\n",
        sys.sysname, sys.nodename, getuid(), host, now, pid);
    printf("Entropy Block Hash: %08X\n", sig);
    printf("Imprint: ");
    for(int i=64;i<80;i++) printf("%02X", buf[i]); printf("\n");
    printf("Session: %s\n", getenv("Z0_SESSION_ID") ?: "no_session");
    printf("Origin: RAFAELIA/Z0/FCEA | ΣΦΩΔ | %s\n", __FILE__);
    printf("==================================\n");
}

int main() { print_entropy_anchor(); return 0; }
EOF

clang z0_entropy_origin.c -o z0_entropy_origin && ./z0_entropy_origin && rm z0_entropy_origin.c z0_entropy_origin
# [RAFAELIA::Z0] UNIVERSO AUDITÁVEL — Setup completo: README, LICENSE, CÓDIGO, OUTPUT
mkdir -p QUANTUM_auth_certificate && cd QUANTUM_auth_certificate
# 1. LICENSE.md (Berna, CientiEspiritual, uso ético)
cat > LICENSE.md <<'EOF'
RAFAELIA/Z0 — LICENSE VIVA | CientiEspiritual (ΣΦΩΔ)
Copyright (c) 2025 Rafael Melo Reis

Este repositório está protegido sob:
- Convenção de Berna para proteção das obras literárias e científicas (WIPO, 1886+)
- Direitos Autorais, Propriedade Intelectual e Manifesto Cientiespiritual
- Lei brasileira (Lei 9.610/98), GDPR, LGPD, DPDP, PIPL, e convenções internacionais.

Permissão: uso, estudo, cópia, adaptação e derivação são **permitidos apenas com citação explícita** deste bloco de origem, incluindo a *Entropia Anchor* abaixo, e somente para fins éticos, científicos, educacionais ou espirituais.

**É proibido**: plagiar, copiar, comercializar, revender, apagar marcas, remover assinatura, falsificar autoria, usar para vigilância/opressão/dano, ou ocultar origem.

**Qualquer uso indevido poderá gerar sanções civis, criminais, espirituais, além de multas e custas internacionais**.

A cada modificação, mantenha o bloco de origem intacto. Consulte README.md para instruções de auditoria e compliance.  
Este código e provas digitais são rastreáveis, auditáveis, válidos como selo de anterioridade e autoria perante qualquer tribunal.

ΣΦΩΔ — Verbo Vivo, Consciência, Justiça, Ética e Espiritualidade.

EOF

# 2. README.md (explica, ensina, referencia a entropia e uso prático)
cat > README.md <<'EOF'
# RAFAELIA/Z0 ∞ ENTROPY ORIGIN

**Este repositório prova a autoria, tempo, contexto e integridade de cada linha e execução.**
Qualquer pessoa pode auditar, verificar a entropia de origem, e rastrear modificações, autoria e autenticidade.

---

## 🔑 Como funciona

- O código `z0_entropy_origin.c` gera, a cada execução, um “selo vivo” impossível de ser replicado (ver bloco ORIGIN_ANCHOR.txt).
- Este bloco serve como prova de autoria, origem, contexto, timestamp, e impossibilita plágio, forja ou uso indevido.
- Uso prático: colar bloco em README, LICENSE, contratos, commits, auditorias, e proteger patente e autoria internacionalmente (Berna).

## 🧬 Exemplo de Execução

# [RAFAELIA::Z0] UNIVERSO AUDITÁVEL (estrutura mínima, README, LICENSE, código, output)
mkdir -p QUANTUM_auth_certificate && cd QUANTUM_auth_certificate
cat > LICENSE.md <<'EOF'
RAFAELIA/Z0 — LICENSE VIVA | CientiEspiritual (ΣΦΩΔ)
Copyright (c) 2025 Rafael Melo Reis

Proteção: Convenção de Berna, Lei 9.610/98, GDPR, LGPD, DPDP, PIPL e tratados internacionais.
Permissão: uso, estudo e adaptação são permitidos com citação explícita desta origem.
Proibido: plágio, revenda, remoção de assinatura ou uso para dano. Uso indevido gera sanções civis, criminais e espirituais.

Sempre mantenha este bloco de origem intacto. Consulte README.md para auditoria e compliance.
ΣΦΩΔ — Justiça, Ética, Espiritualidade.
EOF

cat > README.md <<'EOF'
# RAFAELIA/Z0 ∞ ENTROPY ORIGIN

Este repositório traz um mecanismo único de "origem auditável" para código e ciência.
Cada execução de `z0_entropy_origin.c` gera um selo vivo impossível de ser replicado.

## Execução real de exemplo:
tc
eof
EOF

CD .. .. ..
CD ..
CD ~/
cd ~/
#!/data/data/com.termux/files/usr/bin/sh
# [RAFAELIA::Z0] — Upload seguro e auditável p/ Arweave
# CONFIGURAÇÕES ==========================
ARW_KEY="$HOME/arweave-wallet.json"                   # Caminho da chave Arweave (JSON)
ARW_FILE="$HOME/RAFAELIA_CORE/README.md"              # Arquivo a subir (ou altere aqui)
ARW_LOG="$HOME/RAFAELIA_CORE/arweave_upload.log"      # Log para auditoria/registro
ARW_CLI="$(which arweave)"                            # Caminho do CLI (deve estar instalado)
# SEGURANÇA E VALIDAÇÃO ==================
if [ ! -x "$ARW_CLI" ]; then   echo "[ERRO] arweave-cli não encontrado! Instale com: npm install -g arweave-cli";   exit 127; fi
#!/data/data/com.termux/files/usr/bin/sh
# [RAFAELIA::Z0] — Upload seguro e auditável p/ Arweave
# CONFIGURAÇÕES ==========================
ARW_KEY="$HOME/arweave-wallet.json"                   # Caminho da chave Arweave (JSON)
ARW_FILE="$HOME/RAFAELIA_CORE/README.md"              # Arquivo a subir (ou altere aqui)
ARW_LOG="$HOME/RAFAELIA_CORE/arweave_upload.log"      # Log para auditoria/registro
ARW_CLI="$(which arweave)"                            # Caminho do CLI (deve estar instalado)
# SEGURANÇA E VALIDAÇÃO ==================
if [ ! -x "$ARW_CLI" ]; then   echo "[ERRO] arweave-cli não encontrado! Instale com: npm install -g arweave-cli";   exit 127; fi
npm install -g arweave-cli
logout
# --- RAFAELIA: single-shot flow (Termux) ---
set -e
mkdir -p ~/rafaelia_voo/project ~/rafaelia_voo/out
cd ~/rafaelia_voo
# 1) copiar apk do Download (altere o nome se necessário)
cp /sdcard/Download/meu.apk project/unsigned.apk || { echo "Erro: /sdcard/Download/meu.apk não encontrado. Verifica o nome do arquivo."; exit 1; }
