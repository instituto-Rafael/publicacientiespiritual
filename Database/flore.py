import os, hashlib, time, subprocess, threading, queue, sys, traceback
from datetime import datetime

# === CONFIG & AUTO-SETUP ===
RAFA_SIGIL = "RAFAELIA-GCΩ-"+str(int(time.time()))
HONEYSTR = "∆GC-CRIME-Ω-SECRET-"+RAFA_SIGIL
BASEPATH = "/sdcard/" if os.path.exists("/sdcard/") else "/tmp/"
HONEYFILE = f"{BASEPATH}{RAFA_SIGIL}.txt"
REPORT = f"{BASEPATH}report_{RAFA_SIGIL}.txt"
SUMMARY = f"{BASEPATH}summary_{RAFA_SIGIL}.txt"
ERRORLOG = f"{BASEPATH}forense_errors_{RAFA_SIGIL}.log"
SHADOWLOG = f"{BASEPATH}forense_shadow_{RAFA_SIGIL}.log"  # bugs/erros de acesso

KEYWORDS = [
    RAFA_SIGIL, "GC-CRIME", "SECRET", "deleted", "backup", "shadow", "upload", "cache",
    "voice", "image", "audio", "persist", "deadletter", "archive", "temp", "analytics",
    "send", "log", "outbox", "draft", "conversation", "media", "root", "hold"
]

APPS = [
    "com.whatsapp","com.google.android.inputmethod.latin","com.google.android.gms","com.facebook.orca",
    "com.instagram.android","com.facebook.katana","com.snapchat.android","com.google.android.apps.messaging",
    "com.google.android.apps.photos","com.dropbox.android","com.microsoft.office.outlook","com.twitter.android",
    "com.skype.raider","com.google.android.apps.docs","com.google.android.keep","com.spotify.music"
]

DIRS_MEDIA = [
    "/sdcard/WhatsApp/Backups", "/sdcard/Download", "/sdcard/Documents", "/sdcard/Android/data",
    "/sdcard/WhatsApp/Media", "/sdcard/DCIM", "/sdcard/Music", "/sdcard/Audio", "/sdcard/Recordings",
    "/tmp", "/var/tmp", "/home", "/mnt", "/media", "/data"
]

SEVERITY = {
    "SECRET": "CRÍTICO", "deleted": "ALTO", "backup": "ALTO", "shadow": "ALTO", "upload": "ALTO",
    "deadletter": "ALTO", "archive": "MÉDIO", "cache": "MÉDIO", "voice": "MÉDIO", "audio": "MÉDIO",
    "image": "MÉDIO", "persist": "MÉDIO", "temp": "BAIXO", "log": "BAIXO", "analytics": "BAIXO",
    "draft": "BAIXO", "outbox": "BAIXO", "conversation": "BAIXO", "media": "BAIXO", "root": "CRÍTICO", "hold": "ALTO"
}

def safe_log(msg, exc=None):
    try:
        with open(ERRORLOG, "a") as e:
            e.write(f"{datetime.now()} | {msg}\n")
            if exc: e.write(traceback.format_exc())
    except: pass

def shadow_log(msg, exc=None):
    try:
        with open(SHADOWLOG, "a") as e:
            e.write(f"{datetime.now()} | {msg}\n")
            if exc: e.write(traceback.format_exc())
    except: pass

def bug_hint(e):
    msg = str(e)
    if "Permission denied" in msg:
        return "→ Problema de permissão (storage/data). Verifique se deu permissão para Termux acessar armazenamento e está como root para /data/data."
    if "No such file or directory" in msg:
        return "→ Caminho inexistente. App removido? Storage desmontado?"
    if "stat: path should be string" in msg:
        return "→ BUG CLÁSSICO: Passou lista dentro de lista. Corrija para passar lista de string, não lista de lista."
    if "ModuleNotFoundError" in msg or "ImportError" in msg:
        return "→ Falta de dependência do Python. Instale com pip ou pkg install python-... correspondente."
    if "busybox" in msg:
        return "→ Falta utilitário core. Instale busybox ou toolbox."
    return "→ Erro genérico. Veja log completo."

def preflight_check():
    print("[*] Checando ambiente e permissões...")
    problems = []
    for p in ["/sdcard/", "/tmp/"]:
        try:
            if not os.path.exists(p):
                shadow_log(f"Diretório não existe: {p}")
                continue
            testf = os.path.join(p, f"test_{RAFA_SIGIL}.txt")
            with open(testf,"w") as f: f.write("ok")
            os.remove(testf)
        except Exception as e:
            safe_log(f"Falha permissão em {p}: {e}", e)
            shadow_log(f"Permissão negada ou erro em {p}: {e}", e)
    if sys.version_info < (3,6):
        problems.append("Python < 3.6 não suportado.")
    try:
        subprocess.getoutput("logcat -d -v brief | head -n 1")
    except Exception as e:
        safe_log("logcat não disponível: " + str(e), e)
    if problems:
        print("[!] Problemas detectados:")
        for p in problems: print("   -", p)
        print("[!] Corrija antes de rodar produção.")
    else:
        print("[*] Ambiente validado.")

def inject_honeyfile():
    try:
        with open(HONEYFILE,"w") as f: f.write(HONEYSTR)
        print(f"[+] Honeyfile criado: {HONEYFILE}")
    except Exception as e:
        safe_log(f"Falha honeyfile: {e}", e)

def hash_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha512(f.read()).hexdigest()
    except Exception as e:
        safe_log(f"Hash fail {path}: {e}", e)
        shadow_log(f"Hash bug em {path}: {e}", e)
        return "HASH-ERROR"

def scan_dir(dirs, keywords, out_q):
    for d in dirs:
        if not isinstance(d, str):
            safe_log(f"BUG: d não é string: {d}")
            continue
        if not os.path.exists(d):
            shadow_log(f"Diretório não encontrado: {d}")
            continue
        try:
            for root, _, files in os.walk(d, onerror=lambda e: shadow_log(f"Erro walk {d}: {e}", e)):
                for fn in files:
                    path = os.path.join(root, fn)
                    try:
                        with open(path, errors='ignore') as f:
                            content = f.read()
                            for kw in keywords:
                                if kw in content: out_q.put((path, kw))
                    except PermissionError as e:
                        shadow_log(f"Permissão negada: {path} : {e}", e)
                    except Exception as e:
                        safe_log(f"scan_dir error: {path} : {e}", e)
                        shadow_log(f"scan_dir shadow bug: {path} : {e}", e)
        except Exception as e:
            safe_log(f"Erro fatal scan_dir: {d} : {e}", e)
            print(bug_hint(e))

def scan_packages(packages, keywords, out_q):
    for pkg in packages:
        datadir = f"/data/data/{pkg}/"
        if not os.path.exists(datadir):
            shadow_log(f"Package dir não encontrado: {datadir}")
            continue
        try:
            for root, _, files in os.walk(datadir, onerror=lambda e: shadow_log(f"Erro walk {datadir}: {e}", e)):
                for fn in files:
                    path = os.path.join(root, fn)
                    try:
                        with open(path, errors='ignore') as f:
                            content = f.read()
                            for kw in keywords:
                                if kw in content: out_q.put((path, pkg, kw))
                    except PermissionError as e:
                        shadow_log(f"Permissão negada (pkg): {path} : {e}", e)
                    except Exception as e:
                        safe_log(f"scan_packages error: {path} : {e}", e)
                        shadow_log(f"scan_packages shadow bug: {path} : {e}", e)
        except Exception as e:
            safe_log(f"Erro fatal scan_packages: {datadir} : {e}", e)
            print(bug_hint(e))

def scan_logcat(keywords, out_q):
    try:
        out = subprocess.getoutput("logcat -d -v brief | tail -n 5000")
        for line in out.splitlines():
            for kw in keywords:
                if kw in line: out_q.put((line, kw))
    except Exception as e:
        safe_log(f"logcat error: {e}", e)

def auto_classify(findings):
    classified = {}
    for path, kw in findings:
        sev = SEVERITY.get(kw,"BAIXO")
        if sev not in classified: classified[sev]=[]
        classified[sev].append((path, kw))
    return classified

def gen_report(honeyfile, found1, found2, found3, found4, logcat, sniff=None):
    try:
        with open(REPORT,"w") as r:
            r.write(f"GC-FORENSE-SAFE | Selo: {RAFA_SIGIL}\n")
            r.write(f"Honeyfile: {honeyfile}\nHASH: {hash_file(honeyfile)}\n")
            r.write(f"\n[1] Storage público:\n")
            for p,kw in found1: r.write(f"  {p} [chave: {kw}]\n")
            r.write(f"\n[2] Data/data apps:\n")
            for p,pkg,kw in found2: r.write(f"  {p} [APP: {pkg}] [chave: {kw}]\n")
            r.write(f"\n[3] Backups/media/voice:\n")
            for p,kw in found3: r.write(f"  {p} [chave: {kw}]\n")
            for p,kw in found4: r.write(f"  {p} [chave: {kw}]\n")
            r.write(f"\n[4] LOGCAT (últimas 5000 linhas):\n")
            for line,kw in logcat: r.write(f"  {kw}: {line}\n")
            if sniff: r.write(f"\n[5] Dump de tráfego salvo: {sniff}\n")
        print(f"[✔] Relatório salvo: {REPORT}\n")
    except Exception as e:
        safe_log(f"gen_report: {e}", e)

def gen_summary(found1, found2, found3, found4, logcat):
    try:
        classified = auto_classify(found1 + found3 + found4)
        apps_viol = {}
        for p,pkg,kw in found2:
            sev = SEVERITY.get(kw,"BAIXO")
            if pkg not in apps_viol: apps_viol[pkg]=[]
            apps_viol[pkg].append((p, kw, sev))
        with open(SUMMARY,"w") as s:
            s.write(f"=== GC-FORENSE-SAFE SUMMARY [{RAFA_SIGIL}] ===\n")
            s.write(f"Horário: {datetime.now()}\n\n")
            s.write(">>> RESUMO GERAL DOS CRIMES DETECTADOS:\n")
            for sev in ["CRÍTICO","ALTO","MÉDIO","BAIXO"]:
                if sev in classified:
                    s.write(f"\n[{sev}] {len(classified[sev])} ocorrências:\n")
                    for p,kw in classified[sev]:
                        s.write(f"  {p} [chave: {kw}]\n")
            s.write("\n>>> VIOLAÇÕES POR APP:\n")
            for app in apps_viol:
                s.write(f"\n[APP: {app}] {len(apps_viol[app])} achados:\n")
                for p,kw,sev in apps_viol[app]:
                    s.write(f"  ({sev}) {p} [chave: {kw}]\n")
            s.write("\n>>> EXTRATO DE LOGCAT:\n")
            for line,kw in logcat[:15]:
                s.write(f"  {kw}: {line}\n")
        print(f"[√] Sumário executivo salvo: {SUMMARY}\n")
    except Exception as e:
        safe_log(f"gen_summary: {e}", e)

def run_multithreaded_scan():
    print("[*] Iniciando varredura paralela segura...")
    q1, q2, q3, q4, ql = queue.Queue(), queue.Queue(), queue.Queue(), queue.Queue(), queue.Queue()
    threads = []
    t1 = threading.Thread(target=scan_dir, args=(["/sdcard/"], KEYWORDS, q1))
    t2 = threading.Thread(target=scan_packages, args=(APPS, KEYWORDS, q2))
    t3 = threading.Thread(target=scan_dir, args=(DIRS_MEDIA, KEYWORDS, q3))
    t4 = threading.Thread(target=scan_logcat, args=(KEYWORDS, ql))
    for t in [t1, t2, t3, t4]: t.start(); threads.append(t)
    for t in threads: t.join()
    found1, found2, found3, found4, logcat = [], [], [], [], []
    while not q1.empty(): found1.append(q1.get())
    while not q2.empty(): found2.append(q2.get())
    while not q3.empty(): found3.append(q3.get())
    while not ql.empty(): logcat.append(ql.get())
    # Extra redundância em media/voice
    t5 = threading.Thread(target=scan_dir, args=(["/sdcard/Music","/sdcard/Audio","/sdcard/Recordings"], KEYWORDS, q4))
    t5.start(); t5.join()
    while not q4.empty(): found4.append(q4.get())
    return found1, found2, found3, found4, logcat

if __name__=="__main__":
    try:
        preflight_check()
        inject_honeyfile()
        time.sleep(2)
        found1, found2, found3, found4, logcat = run_multithreaded_scan()
        #sniff = sniff_traffic(30) # Descomente se quiser captura de tráfego
        gen_report(HONEYFILE, found1, found2, found3, found4, logcat)
        gen_summary(found1, found2, found3, found4, logcat)
        print("[√] EXECUÇÃO COMPLETA! Relatório, sumário e logs de erro prontos.")
        print(f"[INFO] Se existirem arquivos {ERRORLOG} ou {SHADOWLOG}, revise para bugs, paths ocultos, ou problemas de permissão (shadow yactos).")
    except Exception as e:
        safe_log(f"FATAL: {e}", e)
        print("[ERRO] Execução interrompida, veja log de erros:", ERRORLOG)
        print("DICA:", bug_hint(e))
