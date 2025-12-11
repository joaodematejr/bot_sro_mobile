#!/usr/bin/env python3
"""
Calibrador de Região de EXP
Ajuda a encontrar onde aparece o texto de EXP após matar inimigos
"""

import subprocess
import sys
from PIL import Image

ADB_DEVICE = "192.168.240.112:5555"

def capturar_screenshot():
    """Captura screenshot via ADB"""
    try:
        temp_path = '/sdcard/screen.png'
        
        # Captura
        subprocess.run(
            ['adb', '-s', ADB_DEVICE, 'shell', 'screencap', '-p', temp_path],
            capture_output=True,
            timeout=5
        )
        
        # Puxa o arquivo
        subprocess.run(
            ['adb', '-s', ADB_DEVICE, 'pull', temp_path, '/tmp/calibrar_exp.png'],
            capture_output=True,
            timeout=5
        )
        
        # Limpa
        subprocess.run(
            ['adb', '-s', ADB_DEVICE, 'shell', 'rm', temp_path],
            capture_output=True,
            timeout=2
        )
        
        return Image.open('/tmp/calibrar_exp.png')
    
    except Exception as e:
        print(f"❌ Erro ao capturar screenshot: {e}")
        return None

def mostrar_regioes_sugeridas(largura, altura):
    """Mostra regiões típicas onde o EXP aparece"""
    print("\n📍 Regiões Sugeridas:")
    print("=" * 60)
    
    # Região centro-superior (mais comum)
    x1 = int(largura * 0.3)
    y1 = int(altura * 0.15)
    w1 = int(largura * 0.4)
    h1 = int(altura * 0.15)
    print(f"1. Centro-Superior (comum):")
    print(f"   x={x1}, y={y1}, largura={w1}, altura={h1}")
    
    # Região centro
    x2 = int(largura * 0.25)
    y2 = int(altura * 0.35)
    w2 = int(largura * 0.5)
    h2 = int(altura * 0.2)
    print(f"\n2. Centro (alternativo):")
    print(f"   x={x2}, y={y2}, largura={w2}, altura={h2}")
    
    # Região superior completa
    x3 = 0
    y3 = 0
    w3 = largura
    h3 = int(altura * 0.3)
    print(f"\n3. Topo Completo (amplo):")
    print(f"   x={x3}, y={y3}, largura={w3}, altura={h3}")

def salvar_regiao_config(x, y, largura, altura):
    """Salva região no config"""
    import json
    
    config_file = 'config_farming_adb.json'
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except:
        print("⚠️  Config não encontrado, criando configuração básica...")
        config = {}
    
    config['regiao_exp'] = {
        'x': x,
        'y': y,
        'largura': largura,
        'altura': altura
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Região salva em {config_file}!")

def main():
    print("🎯 Calibrador de Região de EXP")
    print("=" * 60)
    print()
    print("Este script ajuda a encontrar onde aparece o EXP após combate")
    print()
    
    # Captura screenshot
    print("📸 Capturando screenshot...")
    screenshot = capturar_screenshot()
    
    if not screenshot:
        print("❌ Falha ao capturar screenshot!")
        return
    
    largura, altura = screenshot.size
    print(f"✅ Screenshot capturado: {largura}x{altura}")
    
    # Salva para referência
    screenshot.save('screenshot_exp_referencia.png')
    print(f"💾 Screenshot salvo como: screenshot_exp_referencia.png")
    
    # Mostra sugestões
    mostrar_regioes_sugeridas(largura, altura)
    
    print("\n" + "=" * 60)
    print("📝 INSTRUÇÕES:")
    print("=" * 60)
    print("1. Mate alguns inimigos no jogo para ver o texto de EXP")
    print("2. Abra 'screenshot_exp_referencia.png' em um editor de imagens")
    print("3. Use a ferramenta de seleção para medir a região do texto de EXP")
    print("4. Anote as coordenadas: X, Y, Largura, Altura")
    print("5. Execute este script novamente com os valores")
    print()
    
    # Pergunta se quer configurar agora
    print("Deseja configurar a região agora? (s/n): ", end='')
    resposta = input().strip().lower()
    
    if resposta == 's':
        print("\n📝 Digite as coordenadas da região:")
        try:
            x = int(input("  X (canto esquerdo): "))
            y = int(input("  Y (canto superior): "))
            largura = int(input("  Largura: "))
            altura = int(input("  Altura: "))
            
            # Valida
            if x < 0 or y < 0 or largura <= 0 or altura <= 0:
                print("❌ Valores inválidos!")
                return
            
            if x + largura > screenshot.size[0] or y + altura > screenshot.size[1]:
                print("❌ Região fora dos limites da tela!")
                return
            
            # Mostra preview da região
            regiao = screenshot.crop((x, y, x + largura, y + altura))
            regiao.save('preview_regiao_exp.png')
            print(f"\n💾 Preview salvo como: preview_regiao_exp.png")
            print("   Abra este arquivo para verificar se a região está correta!")
            
            print("\nRegião correta? (s/n): ", end='')
            confirma = input().strip().lower()
            
            if confirma == 's':
                salvar_regiao_config(x, y, largura, altura)
                
                print("\n✅ Configuração completa!")
                print("\n📊 Agora você pode:")
                print("   1. Rodar o bot normalmente")
                print("   2. O bot detectará automaticamente o EXP após cada combate")
                print("   3. As métricas mostrarão tempo estimado até próximo level")
            else:
                print("\n❌ Configuração cancelada. Execute novamente para tentar outra região.")
        
        except ValueError:
            print("❌ Valores inválidos! Use apenas números inteiros.")
        except KeyboardInterrupt:
            print("\n\n❌ Cancelado pelo usuário.")
    else:
        print("\n💡 Dica: Use as sugestões acima ou:")
        print(f"   python3 {sys.argv[0]}")
        print("   e escolha 's' para configurar manualmente")

if __name__ == '__main__':
    main()
