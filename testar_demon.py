#!/usr/bin/env python3
"""
Teste rápido do detector de Demon
"""

import subprocess
import time
import os
from pathlib import Path

print("🧪 TESTE RÁPIDO DO DETECTOR DE DEMON")
print("="*60)

# 1. Captura screenshot atual
print("\n📸 Capturando screenshot...")
subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/test_demon.png"], check=True)
subprocess.run(["adb", "pull", "/sdcard/test_demon.png", "."], check=True)
subprocess.run(["adb", "shell", "rm", "/sdcard/test_demon.png"], check=True)

print("✅ Screenshot capturada: test_demon.png")

# 2. Testa detector
print("\n🔍 Testando detector...")

from main import DemonDetector
import json

# Carrega config
config_file = "config_farming_adb.json"
if Path(config_file).exists():
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
        regiao = config.get("regiao_botao_demon", {"x": 1800, "y": 500, "width": 80, "height": 80})
        usar_deteccao = config.get("usar_deteccao_demon", True)
else:
    print("❌ Config não encontrado!")
    exit(1)

print(f"\n⚙️  Configuração:")
print(f"   Usar detecção: {usar_deteccao}")
print(f"   Região: x={regiao['x']}, y={regiao['y']}, w={regiao['width']}, h={regiao['height']}")

# Cria detector
detector = DemonDetector(regiao)

# Testa com debug
print(f"\n🔍 Testando detecção (modo DEBUG)...")
resultado = detector.is_demon_available("test_demon.png", debug=True)

print(f"\n{'='*60}")
print(f"🎯 RESULTADO:")
print(f"{'='*60}")

if resultado:
    print("✅ DEMON ESTÁ DISPONÍVEL!")
    print("   O bot deveria clicar agora")
else:
    print("❌ DEMON EM COOLDOWN")
    print("   Bot vai esperar ficar disponível")

print(f"\n📁 Imagens debug salvas em: debug_demon/")
print(f"   - demon_roi.png (região do botão)")
print(f"   - demon_mask.png (máscara de detecção)")

print(f"\n💡 Verifique as imagens:")
print(f"   - demon_roi.png deve mostrar o botão Demon")
print(f"   - demon_mask.png deve ter pixels brancos se botão ativo")

# Cleanup
try:
    os.remove("test_demon.png")
except:
    pass
