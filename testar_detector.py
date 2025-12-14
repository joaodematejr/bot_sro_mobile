#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Captura tela do Silkroad e testa detector
"""

import os
import sys
from pathlib import Path

# Adiciona diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

def capturar_e_testar():
    """Captura tela e testa detector"""
    
    print("\n" + "="*70)
    print("📸 CAPTURA DE TELA + DETECÇÃO")
    print("="*70)
    
    # Verifica se pyautogui está disponível
    try:
        import pyautogui
    except ImportError:
        print("\n❌ PyAutoGUI não instalado!")
        print("   Instalando...")
        os.system("pip3 install pyautogui pillow -q")
        import pyautogui
    
    print("\n⏰ Capturando tela em 3 segundos...")
    print("   Posicione a janela do Silkroad!")
    
    import time
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Captura tela
    screenshot = pyautogui.screenshot()
    
    # Salva
    screenshot_path = Path("captura_teste.png")
    screenshot.save(screenshot_path)
    
    print(f"✅ Captura salva: {screenshot_path}")
    
    # Testa detector
    from detector_corrigido import testar_com_screenshot
    
    testar_com_screenshot(str(screenshot_path))


if __name__ == "__main__":
    capturar_e_testar()
