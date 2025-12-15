#!/usr/bin/env python3
"""
Testa detector usando a imagem berzek.png inteira
"""
from main import DemonDetector
import cv2

# Carrega imagem para ver tamanho
img = cv2.imread("img/berzek.png")
h, w = img.shape[:2]
print(f"📐 Tamanho de berzek.png: {w}x{h}")

# Define região como a imagem toda
regiao = {
    "x": 0,
    "y": 0,
    "width": w,
    "height": h
}

print(f"⚙️  Usando região: x={regiao['x']}, y={regiao['y']}, w={regiao['width']}, h={regiao['height']}")

# Cria detector
detector = DemonDetector(regiao)

# Testa
print(f"\n🔍 Testando detecção na imagem inteira...")
resultado = detector.is_demon_available("img/berzek.png", debug=True)

print(f"\n{'='*60}")
if resultado:
    print("✅ BOTÃO DETECTADO COMO DISPONÍVEL!")
else:
    print("❌ BOTÃO NÃO DETECTADO")

print(f"\n📁 Verifique debug_demon/ para ver:")
print(f"   demon_saturation.png - Saturação (cores)")
print(f"   demon_brightness.png - Brilho")
print(f"   demon_mask.png - Resultado final (branco = detectado)")
