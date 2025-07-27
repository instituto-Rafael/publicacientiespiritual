#!/usr/bin/env python3
# fractal_v3.py — gera fractais, logs JSON, Fibonacci modificada e PNG
# Autor: RafaelIA ∞
# Requisitos: python3, pillow, numpy

import json
import math
import numpy as np
from PIL import Image
import os
import time

BASE_DIR = os.path.expanduser("~/RaIaDelta_v3")
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TOKEN_DIR = os.path.join(BASE_DIR, "tokens")

def fibonacci_mod(n):
    # Fibonacci modificada para fractal
    a, b = 0, 1
    for _ in range(n):
        a, b = b, (a + b) % 10007  # módulo primo para fractalização
    return a

def generate_fractal(size=512):
    img = Image.new("RGB", (size, size))
    pixels = img.load()
    for x in range(size):
        for y in range(size):
            val = fibonacci_mod(x * y) % 256
            pixels[x, y] = (val, (val * 2) % 256, (val * 3) % 256)
    return img

def log_json(event, data):
    log_file = os.path.join(LOG_DIR, "fractal_events.json")
    entry = {
        "timestamp": time.time(),
        "event": event,
        "data": data
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TOKEN_DIR, exist_ok=True)

    log_json("start", {"message": "Fractal v3 iniciado"})

    fractal_img = generate_fractal()
    fractal_path = os.path.join(OUTPUT_DIR, "fractal.png")
    fractal_img.save(fractal_path)
    log_json("fractal_generated", {"file": fractal_path})

    print(f"Fractal gerado e salvo em {fractal_path}")

if __name__ == "__main__":
    main()
