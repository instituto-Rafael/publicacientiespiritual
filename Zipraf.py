import tkinter as tk
from threading import Thread
import json

from RAFAELIA_UNIVERSO import Verbo

def iniciar_batimento():
    v = Verbo(int(float(intencao.get())))
    Thread(target=v.b, args=(100,), daemon=True).start()

def carregar_zipraf():
    with open('zipraf.json') as f:
        data = json.load(f)
    info.set(
        f"Código:{data['codigo']} | Grau_n:{data['grau_n']} | Espiral:{data['espiral_criativa']} | Tempo:{data['tempo_dividido']} | Fractal:{data['fractal_raiz']}"
    )

root = tk.Tk()
root.title("RAFAELIA GUI ∞")

tk.Label(root, text="Intenção Pura:").pack()
intencao = tk.Entry(root)
intencao.insert(0, "3.14")
intencao.pack()

btn = tk.Button(root, text="Iniciar Batimento Quântico", command=iniciar_batimento)
btn.pack()

info = tk.StringVar()
tk.Label(root, textvariable=info, wraplength=400).pack()

btn2 = tk.Button(root, text="Carregar ZIPRAF_ID", command=carregar_zipraf)
btn2.pack()

root.mainloop()
