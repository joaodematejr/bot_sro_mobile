#!/usr/bin/env python3
"""
Diagnóstico do Minimapa - Verifica por que mobs não são detectados
Executa uma captura e testa diferentes ranges HSV
"""
import cv2
import numpy as np
import subprocess
import json
from pathlib import Path

print("🔍 DIAGNÓSTICO DE DETECÇÃO NO MINIMAPA")
print("=" * 60)

# Carrega config
with open("config_farming_adb.json", 'r') as f:
    config = json.load(f)

# Região do minimapa
regiao = config.get('regiao_minimap', {})
minimap_x = regiao.get('x', 150)
minimap_y = regiao.get('y', 258)
minimap_w = regiao.get('width', 200)
minimap_h = regiao.get('height', 200)

print(f"\n📍 Região do minimapa configurada:")
print(f"   X: {minimap_x}, Y: {minimap_y}")
print(f"   Largura: {minimap_w}, Altura: {minimap_h}")

# Captura screenshot
device = config.get('adb_device', '')
print(f"\n📱 Capturando screenshot do dispositivo: {device}")

try:
    if device:
        subprocess.run(['adb', '-s', device, 'shell', 'screencap', '-p', '/sdcard/diag_screen.png'], check=True)
        subprocess.run(['adb', '-s', device, 'pull', '/sdcard/diag_screen.png', 'diag_screen.png'], check=True)
    else:
        subprocess.run(['adb', 'shell', 'screencap', '-p', '/sdcard/diag_screen.png'], check=True)
        subprocess.run(['adb', 'pull', '/sdcard/diag_screen.png', 'diag_screen.png'], check=True)
    print("   ✅ Screenshot capturada: diag_screen.png")
except Exception as e:
    print(f"   ❌ Erro ao capturar: {e}")
    print("   Tentando usar última screenshot disponível...")

# Carrega imagem
img = cv2.imread('diag_screen.png')
if img is None:
    print("❌ Não foi possível carregar a imagem")
    exit(1)

print(f"\n📐 Tamanho da tela: {img.shape[1]}x{img.shape[0]}")

# Verifica se região está dentro da imagem
if minimap_x + minimap_w > img.shape[1] or minimap_y + minimap_h > img.shape[0]:
    print(f"⚠️  PROBLEMA: Região do minimapa está FORA da tela!")
    print(f"   Tela: {img.shape[1]}x{img.shape[0]}")
    print(f"   Região: x={minimap_x} até {minimap_x + minimap_w}, y={minimap_y} até {minimap_y + minimap_h}")

# Recorta minimapa
minimap = img[minimap_y:minimap_y+minimap_h, minimap_x:minimap_x+minimap_w]
cv2.imwrite('diag_minimap.png', minimap)
print(f"\n✅ Minimapa recortado salvo: diag_minimap.png")
print(f"   Tamanho: {minimap.shape[1]}x{minimap.shape[0]}")

# Converte para HSV
hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)

# Testa diferentes ranges de vermelho
print("\n🔴 TESTANDO DETECÇÃO DE VERMELHO:")
print("-" * 60)

ranges_para_testar = [
    # Nome, lower1, upper1, lower2, upper2
    ("Config atual", 
     config.get('cores_minimap', {}).get('inimigos', {}).get('hsv_min', [0, 100, 100]),
     config.get('cores_minimap', {}).get('inimigos', {}).get('hsv_max', [10, 255, 255]),
     [170, 100, 100], [180, 255, 255]),
    
    ("Vermelho amplo (S/V baixos)",
     [0, 50, 50], [10, 255, 255],
     [170, 50, 50], [180, 255, 255]),
    
    ("Vermelho muito amplo",
     [0, 30, 30], [15, 255, 255],
     [165, 30, 30], [180, 255, 255]),
    
    ("Só vermelho puro (alto S/V)",
     [0, 150, 150], [10, 255, 255],
     [170, 150, 150], [180, 255, 255]),
    
    ("Vermelho escuro incluído",
     [0, 100, 50], [10, 255, 255],
     [170, 100, 50], [180, 255, 255]),
]

melhor_range = None
melhor_pixels = 0

for nome, l1, u1, l2, u2 in ranges_para_testar:
    mask1 = cv2.inRange(hsv, np.array(l1), np.array(u1))
    mask2 = cv2.inRange(hsv, np.array(l2), np.array(u2))
    mask = cv2.bitwise_or(mask1, mask2)
    
    # Dilata levemente
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    pixels = cv2.countNonZero(mask)
    
    status = "✅" if pixels > 0 else "❌"
    print(f"   {status} {nome}: {pixels} pixels")
    
    if pixels > melhor_pixels:
        melhor_pixels = pixels
        melhor_range = (nome, l1, u1, l2, u2)
    
    # Salva máscara do melhor
    cv2.imwrite(f'diag_mask_{nome.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}.png', mask)

print("-" * 60)

if melhor_pixels > 0:
    print(f"\n🏆 MELHOR RANGE: {melhor_range[0]} com {melhor_pixels} pixels")
    print(f"   HSV Min 1: {melhor_range[1]}")
    print(f"   HSV Max 1: {melhor_range[2]}")
    print(f"   HSV Min 2: {melhor_range[3]}")
    print(f"   HSV Max 2: {melhor_range[4]}")
    
    # Cria máscara final com melhor range
    mask1 = cv2.inRange(hsv, np.array(melhor_range[1]), np.array(melhor_range[2]))
    mask2 = cv2.inRange(hsv, np.array(melhor_range[3]), np.array(melhor_range[4]))
    mask_final = cv2.bitwise_or(mask1, mask2)
    kernel = np.ones((3, 3), np.uint8)
    mask_final = cv2.dilate(mask_final, kernel, iterations=1)
    
    cv2.imwrite('diag_melhor_mask.png', mask_final)
    print(f"\n✅ Máscara do melhor range salva: diag_melhor_mask.png")
    
    # Overlay no minimapa
    overlay = minimap.copy()
    overlay[mask_final > 0] = [0, 0, 255]  # Vermelho no overlay
    cv2.imwrite('diag_overlay.png', overlay)
    print(f"✅ Overlay salvo: diag_overlay.png")
else:
    print("\n❌ NENHUM PIXEL VERMELHO DETECTADO COM NENHUM RANGE!")
    print("   Possíveis causas:")
    print("   1. A região do minimapa está errada (verifique diag_minimap.png)")
    print("   2. O jogo usa cores diferentes de vermelho puro")
    print("   3. O minimapa não tem mobs visíveis no momento")

# Análise de cores presentes no minimapa
print("\n🎨 CORES PREDOMINANTES NO MINIMAPA:")
print("-" * 60)

# Calcula histograma de Hue
h, s, v = cv2.split(hsv)

# Faixas de Hue
hue_ranges = [
    (0, 10, "Vermelho 1"),
    (10, 20, "Laranja"),
    (20, 40, "Amarelo"),
    (40, 80, "Verde"),
    (80, 130, "Ciano/Azul"),
    (130, 170, "Azul/Roxo"),
    (170, 180, "Vermelho 2"),
]

total_pixels = minimap.shape[0] * minimap.shape[1]

for h_min, h_max, nome in hue_ranges:
    mask_h = cv2.inRange(h, h_min, h_max)
    # Só conta se saturação e valor não forem muito baixos (ignora cinza/preto)
    mask_sv = cv2.inRange(s, 50, 255) & cv2.inRange(v, 50, 255)
    mask_final = mask_h & mask_sv
    pixels = cv2.countNonZero(mask_final)
    percent = (pixels / total_pixels) * 100
    bar = "█" * int(percent / 2)
    print(f"   {nome:15s}: {pixels:5d} px ({percent:5.2f}%) {bar}")

print("\n📁 Arquivos de diagnóstico gerados:")
print("   - diag_screen.png (screenshot completa)")
print("   - diag_minimap.png (recorte do minimapa)")
print("   - diag_mask_*.png (máscaras de cada range testado)")
print("   - diag_melhor_mask.png (melhor detecção)")
print("   - diag_overlay.png (overlay visual)")
print("\n💡 Abra diag_minimap.png e verifique se é realmente o minimapa!")
print("   Se não for, ajuste regiao_minimap no config_farming_adb.json")
