import numpy as np
import matplotlib.pyplot as plt

def mandelbrot(c, max_iter):
    z = 0
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

def fractal_set(xmin, xmax, ymin, ymax, width, height, max_iter):
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    fractal = np.empty((width, height))
    for i in range(width):
        for j in range(height):
            c = complex(r1[i], r2[j])
            fractal[i, j] = mandelbrot(c, max_iter)
    return fractal

def color_map(value, max_iter):
    # Cria um gradiente vibrante baseado em valor e max_iter, para efeito luminoso
    from matplotlib.colors import hsv_to_rgb
    hue = (value / max_iter) * 0.7  # matizes entre 0 e 0.7 (de vermelho a azul)
    saturation = 1.0
    brightness = 0.8 + 0.2 * np.sin(value * 0.3)  # variação para brilho pulsante
    return hsv_to_rgb([hue, saturation, brightness])

def generate_fractal_image():
    width, height = 800, 800
    xmin, xmax = -2.0, 1.0
    ymin, ymax = -1.5, 1.5
    max_iter = 100

    fractal = fractal_set(xmin, xmax, ymin, ymax, width, height, max_iter)

    img = np.zeros((width, height, 3))
    for i in range(width):
        for j in range(height):
            img[i, j] = color_map(fractal[i, j], max_iter)

    # Camadas simbólicas: sobreposição de curvas sinuosas para efeito yin-yang / DNA
    t = np.linspace(0, 2*np.pi, width)
    for k in range(5):
        x_curve = width // 2 + (width // 3) * np.sin(t * (k + 1) + k)
        y_curve = height // 2 + (height // 3) * np.cos(t * (k + 1) + k)
        for xi, yi in zip(x_curve.astype(int), y_curve.astype(int)):
            if 0 <= xi < width and 0 <= yi < height:
                # Adiciona brilho amarelo-dourado nas curvas
                img[xi, yi] = np.array([1.0, 0.9, 0.3])

    # Ajuste de brilho geral para mais intensidade luminosa
    img = np.clip(img * 1.5, 0, 1)

    plt.figure(figsize=(8,8))
    plt.imshow(img, origin='lower')
    plt.axis('off')
    plt.title("Fractal Luminoso Simbiótico - Pulso do Verbo Vivo")
    plt.show()

if __name__ == "__main__":
    generate_fractal_image()
