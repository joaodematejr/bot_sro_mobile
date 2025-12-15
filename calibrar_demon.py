#!/usr/bin/env python3
"""
Calibrador do Detector de Demon
Ajusta região e limiares HSV para detecção precisa
"""

import cv2
import numpy as np
import json
from pathlib import Path

def calibrar_regiao():
    """Ajuda a definir a região do botão Demon"""
    
    print("\n" + "="*70)
    print("🔍 CALIBRADOR DE REGIÃO DO BOTÃO DEMON")
    print("="*70)
    
    # Solicita screenshot
    print("\n📸 Primeiro, tire uma screenshot com o botão Demon VISÍVEL")
    print("   Execute no terminal:")
    print("   adb shell screencap -p /sdcard/demon_calibracao.png")
    print("   adb pull /sdcard/demon_calibracao.png .")
    
    input("\n⏸️  Pressione ENTER quando tiver a screenshot pronta...")
    
    # Carrega imagem
    screenshot_path = "demon_calibracao.png"
    
    if not Path(screenshot_path).exists():
        print(f"\n❌ Arquivo {screenshot_path} não encontrado!")
        return
    
    img = cv2.imread(screenshot_path)
    
    if img is None:
        print(f"\n❌ Erro ao carregar {screenshot_path}!")
        return
    
    print(f"\n✅ Screenshot carregada: {img.shape[1]}x{img.shape[0]}")
    
    # Região sugerida (ajustar conforme posição do botão)
    print("\n📍 Posição atual do botão Demon no config:")
    print("   X: 1830, Y: 552")
    print("\n💡 Região sugerida (40x40 pixels ao redor):")
    print("   x: 1810, y: 532, width: 40, height: 40")
    
    # Testa região
    x, y, w, h = 1810, 532, 80, 80
    
    roi = img[y:y+h, x:x+w]
    
    # Salva ROI
    cv2.imwrite("demon_roi_preview.png", roi)
    print(f"\n✅ Região recortada salva: demon_roi_preview.png")
    print(f"   Verifique se capturou o botão Demon corretamente!")
    
    # Mostra cores HSV da região
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    print(f"\n🎨 Análise de cores HSV:")
    print(f"   H (Matiz): min={hsv[:,:,0].min()}, max={hsv[:,:,0].max()}")
    print(f"   S (Saturação): min={hsv[:,:,1].min()}, max={hsv[:,:,1].max()}")
    print(f"   V (Valor/Brilho): min={hsv[:,:,2].min()}, max={hsv[:,:,2].max()}")
    
    # Pergunta se quer ajustar
    print(f"\n❓ Deseja ajustar a região? (s/n)")
    if input("➡️  ").lower() == 's':
        print("\n📐 Digite as novas coordenadas:")
        try:
            x = int(input("   X (canto superior esquerdo): "))
            y = int(input("   Y (canto superior esquerdo): "))
            w = int(input("   Width (largura): "))
            h = int(input("   Height (altura): "))
            
            # Testa nova região
            roi = img[y:y+h, x:x+w]
            cv2.imwrite("demon_roi_preview.png", roi)
            
            print(f"\n✅ Nova região salva: demon_roi_preview.png")
            
        except ValueError:
            print("❌ Valores inválidos!")
            return
    
    # Salva no config
    config_file = "config_farming_adb.json"
    
    if Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config["regiao_botao_demon"] = {
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "descricao": "Região do botão Demon para detecção visual"
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Região salva no {config_file}!")
    
    return {"x": x, "y": y, "width": w, "height": h}


def calibrar_hsv():
    """Ajusta limiares HSV para detecção do botão ativo"""
    
    print("\n" + "="*70)
    print("🎨 CALIBRADOR DE LIMIARES HSV")
    print("="*70)
    
    print("\n📸 Você precisa de 2 screenshots:")
    print("   1. demon_ativo.png - Botão DISPONÍVEL (sem cooldown)")
    print("   2. demon_cooldown.png - Botão EM COOLDOWN (cinza/escuro)")
    
    input("\n⏸️  Pressione ENTER quando tiver as screenshots prontas...")
    
    # Analisa botão ativo
    if not Path("demon_ativo.png").exists():
        print("\n❌ demon_ativo.png não encontrada!")
        return
    
    img_ativo = cv2.imread("demon_ativo.png")
    
    # Usa região do config ou padrão
    config_file = "config_farming_adb.json"
    if Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            regiao = config.get("regiao_botao_demon", {"x": 1810, "y": 532, "width": 40, "height": 40})
    else:
        regiao = {"x": 1810, "y": 532, "width": 40, "height": 40}
    
    x, y, w, h = regiao["x"], regiao["y"], regiao["width"], regiao["height"]
    
    roi_ativo = img_ativo[y:y+h, x:x+w]
    hsv_ativo = cv2.cvtColor(roi_ativo, cv2.COLOR_BGR2HSV)
    
    print(f"\n🟢 BOTÃO ATIVO:")
    print(f"   H: {hsv_ativo[:,:,0].min()}-{hsv_ativo[:,:,0].max()}")
    print(f"   S: {hsv_ativo[:,:,1].min()}-{hsv_ativo[:,:,1].max()}")
    print(f"   V: {hsv_ativo[:,:,2].min()}-{hsv_ativo[:,:,2].max()}")
    
    # Calcula valores médios e desvio
    h_mean = hsv_ativo[:,:,0].mean()
    s_mean = hsv_ativo[:,:,1].mean()
    v_mean = hsv_ativo[:,:,2].mean()
    
    print(f"\n   Médias: H={h_mean:.0f}, S={s_mean:.0f}, V={v_mean:.0f}")
    
    # Analisa cooldown se disponível
    if Path("demon_cooldown.png").exists():
        img_cooldown = cv2.imread("demon_cooldown.png")
        roi_cooldown = img_cooldown[y:y+h, x:x+w]
        hsv_cooldown = cv2.cvtColor(roi_cooldown, cv2.COLOR_BGR2HSV)
        
        print(f"\n🔴 BOTÃO EM COOLDOWN:")
        print(f"   H: {hsv_cooldown[:,:,0].min()}-{hsv_cooldown[:,:,0].max()}")
        print(f"   S: {hsv_cooldown[:,:,1].min()}-{hsv_cooldown[:,:,1].max()}")
        print(f"   V: {hsv_cooldown[:,:,2].min()}-{hsv_cooldown[:,:,2].max()}")
    
    # Sugere limiares
    print(f"\n💡 LIMIARES SUGERIDOS:")
    
    # Para botão laranja/dourado ativo
    lower_h = max(0, int(h_mean - 10))
    upper_h = min(179, int(h_mean + 10))
    lower_s = max(0, int(s_mean * 0.6))
    upper_s = 255
    lower_v = max(0, int(v_mean * 0.6))
    upper_v = 255
    
    print(f"\n   Lower HSV: [{lower_h}, {lower_s}, {lower_v}]")
    print(f"   Upper HSV: [{upper_h}, {upper_s}, {upper_v}]")
    
    # Testa máscara
    mask = cv2.inRange(hsv_ativo, 
                       np.array([lower_h, lower_s, lower_v]),
                       np.array([upper_h, upper_s, upper_v]))
    
    cv2.imwrite("demon_mask_test.png", mask)
    
    pixels_detectados = cv2.countNonZero(mask)
    total_pixels = w * h
    percentual = (pixels_detectados / total_pixels) * 100
    
    print(f"\n🔍 TESTE:")
    print(f"   Pixels detectados: {pixels_detectados}/{total_pixels} ({percentual:.1f}%)")
    print(f"   Limiar: 15% (ativo se >= 15%)")
    print(f"   Status: {'✅ DETECTADO' if percentual >= 15 else '❌ NÃO DETECTADO'}")
    
    print(f"\n💾 Máscara salva: demon_mask_test.png")
    print(f"   (branco = detectado, preto = não detectado)")
    
    # Opção de ajuste manual
    print(f"\n❓ Limiares OK ou quer ajustar? (ok/ajustar)")
    if input("➡️  ").lower() == 'ajustar':
        print("\n📐 Digite os novos limiares HSV:")
        try:
            print("   Lower HSV:")
            lower_h = int(input("     H (0-179): "))
            lower_s = int(input("     S (0-255): "))
            lower_v = int(input("     V (0-255): "))
            
            print("   Upper HSV:")
            upper_h = int(input("     H (0-179): "))
            upper_s = int(input("     S (0-255): "))
            upper_v = int(input("     V (0-255): "))
            
        except ValueError:
            print("❌ Valores inválidos!")
            return
    
    print(f"\n💡 Para aplicar, edite main.py na classe DemonDetector:")
    print(f"   self.lower_active = np.array([{lower_h}, {lower_s}, {lower_v}])")
    print(f"   self.upper_active = np.array([{upper_h}, {upper_s}, {upper_v}])")


def menu_principal():
    """Menu principal do calibrador"""
    
    while True:
        print("\n" + "="*70)
        print("🔧 CALIBRADOR DO DETECTOR DE DEMON")
        print("="*70)
        print("\n1. 📍 Calibrar região do botão")
        print("2. 🎨 Calibrar limiares HSV")
        print("3. 🧪 Testar detecção completa")
        print("0. ❌ Sair")
        
        escolha = input("\n➡️  Escolha: ").strip()
        
        if escolha == '0':
            break
        
        elif escolha == '1':
            calibrar_regiao()
            input("\n⏸️  Pressione ENTER para continuar...")
        
        elif escolha == '2':
            calibrar_hsv()
            input("\n⏸️  Pressione ENTER para continuar...")
        
        elif escolha == '3':
            testar_deteccao()
            input("\n⏸️  Pressione ENTER para continuar...")
        
        else:
            print("❌ Opção inválida!")


def testar_deteccao():
    """Testa detecção em screenshot real"""
    
    print("\n🧪 TESTE DE DETECÇÃO")
    print("="*70)
    
    screenshot = input("\n📸 Caminho da screenshot: ").strip()
    
    if not Path(screenshot).exists():
        print(f"❌ {screenshot} não encontrado!")
        return
    
    # Importa detector
    from main import DemonDetector
    import json
    
    # Carrega config
    config_file = "config_farming_adb.json"
    if Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            regiao = config.get("regiao_botao_demon", {"x": 1810, "y": 532, "width": 40, "height": 40})
    else:
        regiao = {"x": 1810, "y": 532, "width": 40, "height": 40}
    
    # Cria detector
    detector = DemonDetector(regiao)
    
    # Testa
    resultado = detector.is_demon_available(screenshot, debug=True)
    
    print(f"\n🔍 RESULTADO:")
    print(f"   Status: {'✅ DEMON DISPONÍVEL' if resultado else '❌ EM COOLDOWN'}")
    print(f"\n📁 Imagens debug salvas em: debug_demon/")
    print(f"   - demon_roi.png (região recortada)")
    print(f"   - demon_mask.png (máscara HSV)")


if __name__ == "__main__":
    menu_principal()
