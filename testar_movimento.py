#!/usr/bin/env python3
"""
Testa o sistema de Movimento Automático Inteligente
"""
import subprocess
import json
from movimento_inteligente import MovimentoInteligente


class FakeADB:
    """Classe fake para testar sem ADB real"""
    def swipe(self, x1, y1, x2, y2, duration):
        print(f"   SWIPE: ({x1},{y1}) → ({x2},{y2}) durante {duration}ms")
        return True


print("🧪 TESTE DO MOVIMENTO AUTOMÁTICO INTELIGENTE")
print("="*80)

# Carrega config
with open("config_farming_adb.json", 'r') as f:
    config = json.load(f)

# Cria sistema de movimento (com ADB fake para teste)
adb_fake = FakeADB()
movimento = MovimentoInteligente(adb_fake, config)

# Captura screenshot atual
print("\n📸 Capturando screenshot do dispositivo...")
subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/test_movimento.png"], check=True)
subprocess.run(["adb", "pull", "/sdcard/test_movimento.png", "."], check=True)
subprocess.run(["adb", "shell", "rm", "/sdcard/test_movimento.png"], check=True)

print("✅ Screenshot capturada: test_movimento.png")

# Analisa densidade de mobs
print("\n🔍 Analisando densidade de mobs no minimapa...")
analise = movimento.analisar_densidade_mobs("test_movimento.png", debug=True)

print(f"\n📊 RESULTADO DA ANÁLISE:")
print("-"*80)
print(f"  Mobs na área atual: {analise['mobs_atual']} pixels vermelhos")
print(f"  Precisa mover: {'✅ SIM' if analise['precisa_mover'] else '❌ NÃO'}")

if analise['precisa_mover']:
    print(f"  Melhor direção: {analise['melhor_direcao']}")
    print(f"  Densidade máxima: {analise['max_densidade']} pixels")
    print(f"\n  Densidade por direção:")
    for dir, dens in sorted(analise['densidade_direcao'].items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(dens / 10)
        print(f"    {dir:10s}: {bar} {dens:4d} pixels")
else:
    print(f"  ✅ Área atual tem boa densidade de mobs!")
    print(f"  Densidade por direção:")
    for dir, dens in sorted(analise['densidade_direcao'].items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(dens / 10) if dens > 0 else ""
        print(f"    {dir:10s}: {bar} {dens:4d} pixels")

print(f"\n📁 Imagens de debug salvas em: debug_movimento/")
print(f"  - minimap_completo.png (minimapa extraído)")
print(f"  - mobs_detectados.png (pixels vermelhos = mobs)")
print(f"  - analise_movimento.png (minimapa com seta de direção)")
print(f"  - direcao_*.png (análise por cada direção)")

# Teste de movimento
if analise['precisa_mover']:
    print(f"\n🎯 TESTE DE MOVIMENTO:")
    print("-"*80)
    print(f"  Executando movimento para: {analise['melhor_direcao']}")
    movimento.mover_para_direcao(analise['melhor_direcao'], duracao=2.5)
    print(f"\n💡 NOTA: Movimento executado com ADB fake (não moveu de verdade)")
    print(f"  Para mover de verdade, use no bot em modo normal")
else:
    print(f"\n✅ Não é necessário mover - ficando no local")

# Estatísticas
print(f"\n📊 ESTATÍSTICAS:")
print("-"*80)
stats = movimento.get_estatisticas()
for key, value in stats.items():
    print(f"  {key}: {value}")

print(f"\n{'='*80}")
print(f"✅ Teste concluído!")
print(f"{'='*80}")

# Cleanup
import os
try:
    os.remove("test_movimento.png")
except:
    pass
