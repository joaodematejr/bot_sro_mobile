#!/usr/bin/env python3
"""
Testa detector de Demon usando imagem berzek.png
"""
from main import DemonDetector
import json
from pathlib import Path

# Carrega config
config_file = "config_farming_adb.json"
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)
    regiao = config.get("regiao_botao_demon")

print("🧪 TESTE COM IMAGEM BERZEK.PNG")
print("="*60)
print(f"⚙️  Região: x={regiao['x']}, y={regiao['y']}, w={regiao['width']}, h={regiao['height']}")

# Cria detector
detector = DemonDetector(regiao)

# Testa com imagem berzek
print(f"\n🔍 Testando com img/berzek.png (botão DISPONÍVEL)...")
resultado = detector.is_demon_available("img/berzek.png", debug=True)

print(f"\n{'='*60}")
print(f"🎯 RESULTADO:")
print(f"{'='*60}")

if resultado:
    print("✅ DEMON DETECTADO COMO DISPONÍVEL!")
    print("   Bot vai clicar")
else:
    print("❌ DEMON NÃO DETECTADO")
    print("   Bot não vai clicar")

print(f"\n📁 Verifique as imagens em debug_demon/")
print(f"   - demon_roi.png (região do botão)")
print(f"   - demon_mask.png (pixels detectados - branco)")
print(f"   - demon_saturation.png (mapa de saturação)")
print(f"   - demon_brightness.png (mapa de brilho)")
