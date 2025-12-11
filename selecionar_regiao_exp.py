#!/usr/bin/env python3
"""
Ferramenta interativa para marcar região do EXP
Clique e arraste para selecionar a área onde aparece o EXP
"""

import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Força X11 ao invés de Wayland

import cv2
import numpy as np
from PIL import Image
import json

# Variáveis globais para seleção
selecting = False
ix, iy = -1, -1
fx, fy = -1, -1

def mouse_callback(event, x, y, flags, param):
    global selecting, ix, iy, fx, fy, img_display
    
    if event == cv2.EVENT_LBUTTONDOWN:
        selecting = True
        ix, iy = x, y
        fx, fy = x, y
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting:
            fx, fy = x, y
            # Mostra retângulo temporário
            temp = img_display.copy()
            cv2.rectangle(temp, (ix, iy), (fx, fy), (0, 255, 0), 2)
            cv2.imshow('Selecione a região do EXP', temp)
    
    elif event == cv2.EVENT_LBUTTONUP:
        selecting = False
        fx, fy = x, y
        print(f'\n✅ Região selecionada:')
        
        x_min = min(ix, fx)
        y_min = min(iy, fy)
        x_max = max(ix, fx)
        y_max = max(iy, fy)
        
        largura = x_max - x_min
        altura = y_max - y_min
        
        print(f'   X: {x_min}')
        print(f'   Y: {y_min}')
        print(f'   Largura: {largura}')
        print(f'   Altura: {altura}')
        
        # Salva configuração
        config = {
            'regiao_exp': {
                'x': int(x_min),
                'y': int(y_min),
                'largura': int(largura),
                'altura': int(altura)
            }
        }
        
        with open('regiao_exp_selecionada.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f'\n💾 Salvo em: regiao_exp_selecionada.json')
        print(f'\n📋 Copie para o config:')
        print(f'    "regiao_exp": {{"x": {x_min}, "y": {y_min}, "largura": {largura}, "altura": {altura}}}')

# Carrega imagem
print("🎯 Selecionador de Região de EXP")
print("="*60)
print("\nCarregando imagem combate_1765471268_d1.png...")

img_path = 'treino_ml/combate_1765471268_d1.png'
img = Image.open(img_path)
img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# Redimensiona se muito grande
h, w = img_cv.shape[:2]
max_size = 1200
if w > max_size or h > max_size:
    scale = max_size / max(w, h)
    img_cv = cv2.resize(img_cv, (int(w * scale), int(h * scale)))
    print(f"✓ Imagem redimensionada para visualização: {img_cv.shape[1]}x{img_cv.shape[0]}")
    print(f"  (escala: {scale:.2f}x - coordenadas serão ajustadas)")
else:
    scale = 1.0

img_display = img_cv.copy()

print("\n📝 INSTRUÇÕES:")
print("  1. Clique e arraste para selecionar a região do EXP")
print("  2. Solte o mouse para confirmar")
print("  3. Pressione 'q' para sair")
print("  4. Pressione 'r' para resetar seleção")
print()

try:
    cv2.namedWindow('Selecione a região do EXP', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Selecione a região do EXP', mouse_callback)
except Exception as e:
    print(f"❌ Erro ao criar janela: {e}")
    print("\n💡 Tente executar com: GDK_BACKEND=x11 python3 selecionar_regiao_exp.py")
    exit(1)

while True:
    cv2.imshow('Selecione a região do EXP', img_display)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('r'):
        img_display = img_cv.copy()
        ix, iy, fx, fy = -1, -1, -1, -1
        print("\n🔄 Seleção resetada")

cv2.destroyAllWindows()
print("\n✅ Ferramenta fechada")
