#!/usr/bin/env python3
"""
Calibra a região correta do botão Demon
"""
import cv2
import subprocess
import json

print("🎯 CALIBRADOR DE REGIÃO DO BOTÃO DEMON")
print("="*60)

# Captura screenshot atual
print("\n📸 Capturando screenshot do dispositivo...")
subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/calibrar.png"], check=True)
subprocess.run(["adb", "pull", "/sdcard/calibrar.png", "."], check=True)
subprocess.run(["adb", "shell", "rm", "/sdcard/calibrar.png"], check=True)

# Carrega imagem
img = cv2.imread("calibrar.png")
h, w = img.shape[:2]
print(f"✅ Screenshot: {w}x{h}")

# Coordenadas do botão Demon (do config)
demon_x = 1830
demon_y = 552

print(f"\n📍 Coordenada do clique: ({demon_x}, {demon_y})")
print(f"\n💡 O botão Demon está centralizado nessa posição?")
print(f"   Vou testar diferentes tamanhos de região ao redor desse ponto:\n")

# Testa diferentes tamanhos
tamanhos = [
    (30, 30, "Muito pequeno"),
    (40, 40, "Pequeno"),
    (50, 50, "Médio-pequeno"),
    (60, 60, "Médio"),
    (80, 80, "Grande (atual)"),
    (100, 100, "Muito grande")
]

for width, height, desc in tamanhos:
    # Centraliza região no ponto de clique
    x = demon_x - width // 2
    y = demon_y - height // 2
    
    # Recorta
    roi = img[y:y+height, x:x+width]
    
    # Salva
    filename = f"demon_regiao_{width}x{height}.png"
    cv2.imwrite(filename, roi)
    
    # Desenha retângulo na imagem completa
    img_copy = img.copy()
    cv2.rectangle(img_copy, (x, y), (x+width, y+height), (0, 255, 0), 2)
    cv2.putText(img_copy, f"{width}x{height}", (x, y-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imwrite(f"preview_{width}x{height}.png", img_copy)
    
    print(f"   {desc:15s} ({width}x{height}): região=({x}, {y}) → {filename}")

print(f"\n📁 Arquivos gerados:")
print(f"   - demon_regiao_*.png → Região recortada")
print(f"   - preview_*.png → Screenshot com retângulo verde")
print(f"\n🔍 PRÓXIMOS PASSOS:")
print(f"   1. Abra os arquivos preview_*.png")
print(f"   2. Veja qual retângulo verde cobre APENAS o botão Demon")
print(f"   3. Anote o tamanho que funcionou melhor")
print(f"   4. Me diga qual tamanho usar (ex: 40x40, 50x50, etc)")
print(f"\n💡 DICA: O ideal é que o retângulo cubra:")
print(f"   - TODO o ícone do botão quando ele está VISÍVEL")
print(f"   - O MÍNIMO possível da interface ao redor")
