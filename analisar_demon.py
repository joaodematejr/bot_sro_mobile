#!/usr/bin/env python3
"""
Analisa as imagens de debug do Demon para ajustar thresholds
"""
import cv2
import numpy as np
from pathlib import Path

debug_folder = Path("debug_demon")

# Verifica se existem imagens
roi_path = debug_folder / "demon_roi.png"
mask_path = debug_folder / "demon_mask.png"
brightness_path = debug_folder / "demon_brightness.png"

if not roi_path.exists():
    print("❌ Não encontrei demon_roi.png")
    print("   Execute: python3 testar_demon.py primeiro")
    exit(1)

# Carrega ROI
roi = cv2.imread(str(roi_path))
print("📊 ANÁLISE DA REGIÃO DO BOTÃO DEMON")
print("="*60)
print(f"Tamanho da ROI: {roi.shape[1]}x{roi.shape[0]} pixels")

# Converte para HSV
hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(hsv)

# Estatísticas do canal V (brilho)
print(f"\n📈 Estatísticas de BRILHO (canal V):")
print(f"   Mínimo: {v.min()}")
print(f"   Máximo: {v.max()}")
print(f"   Média: {v.mean():.1f}")
print(f"   Mediana: {np.median(v):.1f}")

# Testa diferentes thresholds
total_pixels = roi.shape[0] * roi.shape[1]
print(f"\n🔍 Teste de THRESHOLDS (total: {total_pixels} pixels):")

thresholds = [30, 50, 70, 100, 120, 150]
for thresh in thresholds:
    pixels_acima = np.sum(v > thresh)
    percentual = (pixels_acima / total_pixels) * 100
    status = "✅ DETECTARIA" if percentual >= 30 else "❌ NÃO DETECTARIA"
    print(f"   Threshold {thresh:3d}: {pixels_acima:4d} pixels ({percentual:5.1f}%) - {status}")

# Análise de cores
print(f"\n🎨 Estatísticas de COR (canal H):")
print(f"   Mínimo: {h.min()}")
print(f"   Máximo: {h.max()}")
print(f"   Média: {h.mean():.1f}")

print(f"\n💧 Estatísticas de SATURAÇÃO (canal S):")
print(f"   Mínimo: {s.min()}")
print(f"   Máximo: {s.max()}")
print(f"   Média: {s.mean():.1f}")

# Mostra histograma simplificado de brilho
print(f"\n📊 Distribuição de BRILHO:")
ranges = [(0, 50), (50, 100), (100, 150), (150, 200), (200, 255)]
for min_val, max_val in ranges:
    count = np.sum((v >= min_val) & (v < max_val))
    percent = (count / total_pixels) * 100
    bar = "█" * int(percent / 2)
    print(f"   {min_val:3d}-{max_val:3d}: {bar} {percent:5.1f}%")

# Recomendação
print(f"\n💡 RECOMENDAÇÃO:")
pixels_muito_brilhantes = np.sum(v > 150)
pixels_brilhantes = np.sum(v > 100)
pixels_medios = np.sum(v > 50)

if pixels_muito_brilhantes > total_pixels * 0.3:
    print("   ⚠️  Região MUITO BRILHANTE - botão parece estar DISPONÍVEL")
    print(f"   Sugestão: usar threshold=150, percentual=30%")
elif pixels_brilhantes > total_pixels * 0.3:
    print("   ⚡ Região BRILHANTE - botão parece estar DISPONÍVEL")
    print(f"   Sugestão: usar threshold=100, percentual=30%")
elif pixels_medios > total_pixels * 0.5:
    print("   ⚠️  Região com brilho MÉDIO - pode ser fundo/interface")
    print(f"   Sugestão: usar threshold=120, percentual=40%")
else:
    print("   🌑 Região ESCURA - botão parece estar AUSENTE")
    print(f"   Sugestão: usar threshold=100, percentual=30%")

print(f"\n📁 Verifique as imagens em debug_demon/")
print(f"   demon_roi.png - Mostra a região capturada")
print(f"   demon_mask.png - Mostra pixels detectados (branco)")
print(f"   demon_brightness.png - Mostra mapa de brilho")
