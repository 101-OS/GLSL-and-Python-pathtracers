import tkinter as tk
from PIL import Image, ImageTk
import math

# Vector helpers
dot = lambda a, b: sum(i * j for i, j in zip(a, b))
sub = lambda a, b: [i - j for i, j in zip(a, b)]
add = lambda a, b: [i + j for i, j in zip(a, b)]
mul = lambda a, s: [i * s for i in a]
norm = lambda v: [i / (l := math.sqrt(dot(v, v))) for i in v] if dot(v, v) else v
reflect = lambda I, N: sub(I, mul(N, 2 * dot(I, N)))

def refract(I, N, eta):
    cosi = -max(-1, min(1, dot(I, N)))
    if cosi < 0: return refract(I, [-n for n in N], 1 / eta)
    k = 1 - eta * eta * (1 - cosi * cosi)
    return add(mul(I, eta), mul(N, eta * cosi - math.sqrt(k))) if k > 0 else None

def hit_sphere(ro, rd, c, r):
    oc = sub(ro, c)
    b = dot(rd, oc)
    h = b * b - dot(oc, oc) + r * r
    if h < 0: return None
    t = -b - math.sqrt(h)
    if t < .001: return None
    p = add(ro, mul(rd, t))
    return t, p, norm(sub(p, c))

def hit_plane(ro, rd, p0, n):
    d = dot(rd, n)
    if abs(d) < 1e-6: return None
    t = dot(sub(p0, ro), n) / d
    if t < .001: return None
    return t, add(ro, mul(rd, t)), n

objects = [
    {'t': 's', 'c': [0, -0.5, 3], 'r': 0.5, 'col': [1, 0, 0], 'refl': 0.5, 'refr': 0, 'ior': 1},
    {'t': 's', 'c': [1, 0, 4], 'r': 0.7, 'col': [0, 1, 0], 'refl': 0.2, 'refr': 0.8, 'ior': 1.5},
    {'t': 's', 'c': [-1, 0, 4], 'r': 0.7, 'col': [0.5, 0.5, 1], 'refl': 0.9, 'refr': 0, 'ior': 1},
    {'t': 'p', 'p': [0, -1, 0], 'n': [0, 1, 0], 'col': [0.8, 0.8, 0.8], 'refl': 0.1, 'refr': 0, 'ior': 1}
]

def trace(ro, rd, d=0):
    if d > 5: return [0, 0, 0]
    tmin, hit, N, obj = 1e9, None, None, None
    for o in objects:
        r = hit_sphere(ro, rd, o['c'], o['r']) if o['t'] == 's' else hit_plane(ro, rd, o['p'], o['n'])
        if r and r[0] < tmin: tmin, hit, N, obj = r[0], r[1], r[2], o
    if not obj: return [0.7, 0.9, 1.0]  # background
    col, refl, refr, ior = obj['col'], obj['refl'], obj['refr'], obj['ior']
    L = norm([5, 5, -10])
    light = max(0, dot(N, L))
    bias = 1e-4
    rcol = trace(add(hit, mul(N, bias)), reflect(rd, N), d + 1) if refl else [0, 0, 0]
    tcol = [0, 0, 0]
    if refr:
        refr_dir = refract(rd, N, ior)
        if refr_dir: tcol = trace(add(hit, mul(N, -bias)), refr_dir, d + 1)
    return [min(1, col[i] * light * (1 - refl - refr) + refl * rcol[i] + refr * tcol[i]) for i in range(3)]

w, h = 320, 240
root = tk.Tk()
root.title('Raytracer')

# Create PIL image and ImageTk object separately
img = Image.new("RGB", (w, h))
tkimg = ImageTk.PhotoImage(img)

label = tk.Label(root, image=tkimg)
label.pack()

buf = [[[0, 0, 0] for _ in range(w)] for _ in range(h)]
cnt = [[0] * w for _ in range(h)]
cam = [0, 0, 0]
last = [0, 0, 0]

def render():
    global tkimg, img, last
    move = cam != last
    for y in range(h):
        for x in range(w):
            dx, dy = (x - w / 2) / w, (h / 2 - y) / h
            col = trace(cam, norm([dx, dy, 1]))
            if move:
                buf[y][x], cnt[y][x] = col, 1
            else:
                buf[y][x] = [buf[y][x][i] + col[i] for i in range(3)]
                cnt[y][x] += 1
            avg = [min(255, int(255 * buf[y][x][i] / cnt[y][x])) for i in range(3)]
            img.putpixel((x, y), tuple(avg))
    tkimg = ImageTk.PhotoImage(img)
    label.config(image=tkimg)
    label.image = tkimg
    last[:] = cam[:]
    root.after(1, render)

render()
root.mainloop()








