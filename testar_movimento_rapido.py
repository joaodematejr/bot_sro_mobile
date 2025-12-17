#!/usr/bin/env python3
"""
Teste rápido do sistema de movimento - captura tela e analisa
"""

import subprocess
import cv2
import numpy as np
from pathlib import Path

def capturar_tela():
    """Captura a tela do dispositivo via ADB"""
    try:
        result = subprocess.run(
            ['adb', 'exec-out', 'screencap', '-p'],
            capture_output=True
        )
        if result.returncode == 0:
            nparr = np.frombuffer(result.stdout, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
    except Exception as e:
        print(f"Erro ao capturar tela: {e}")
    return None

def main():
    print("=" * 60)
    print("🧪 TESTE RÁPIDO DO SISTEMA DE MOVIMENTO")
    print("=" * 60)
    
    # Captura tela
    print("\n📸 Capturando tela do dispositivo...")
    img = capturar_tela()
    
    if img is None:
        print("❌ Falha ao capturar tela!")
        return
    
    print(f"✅ Tela capturada: {img.shape}")
    
    # Região do minimapa (do config)
    x, y, w, h = 231, 255, 200, 200
    minimapa = img[y:y+h, x:x+w]
    
    # Converte para HSV
    hsv = cv2.cvtColor(minimapa, cv2.COLOR_BGR2HSV)
    
    # Ranges HSV para vermelho (atualizados)
    lower1 = np.array([0, 30, 30])
    upper1 = np.array([15, 255, 255])
    lower2 = np.array([165, 30, 30])
    upper2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask_mobs = cv2.bitwise_or(mask1, mask2)
    
    # Conta total de mobs
    mobs_total = cv2.countNonZero(mask_mobs)
    
    # Centro do minimapa e raio
    centro_x, centro_y = 100, 100  # Centro do minimapa 200x200
    raio = 50
    
    # Máscara de proximidade
    mask_perto = np.zeros_like(mask_mobs)
    cv2.circle(mask_perto, (centro_x, centro_y), raio, 255, -1)
    mobs_perto = cv2.bitwise_and(mask_mobs, mask_perto)
    mobs_atual = cv2.countNonZero(mobs_perto)
    
    # Thresholds (atualizados)
    PIXELS_POR_MOB = 15
    max_mobs_seguro = 4
    min_mobs_para_ficar = 2
    
    threshold_perigo = max_mobs_seguro * PIXELS_POR_MOB  # 60
    threshold_poucos = min_mobs_para_ficar * PIXELS_POR_MOB  # 30
    
    print(f"\n📊 RESULTADOS:")
    print(f"   🔴 Mobs total no minimapa: {mobs_total} pixels")
    print(f"   🎯 Mobs perto (raio {raio}px): {mobs_atual} pixels")
    print(f"\n⚙️ THRESHOLDS:")
    print(f"   🚨 Perigo: > {threshold_perigo} pixels ({max_mobs_seguro} mobs)")
    print(f"   🔍 Poucos: < {threshold_poucos} pixels ({min_mobs_para_ficar} mobs)")
    
    # Decisão
    print(f"\n🎮 DECISÃO:")
    if mobs_atual > threshold_perigo:
        print(f"   🚨 PERIGO! {mobs_atual} pixels → Precisa FUGIR")
    elif mobs_atual < threshold_poucos:
        print(f"   🔍 POUCOS MOBS! {mobs_atual} pixels → Precisa BUSCAR mais")
    else:
        print(f"   ✅ ÁREA BOA! {mobs_atual} pixels → Pode ficar")
    
    # Salva debug
    debug_folder = Path("debug_movimento")
    debug_folder.mkdir(exist_ok=True)
    
    cv2.imwrite(str(debug_folder / "minimapa_original.png"), minimapa)
    cv2.imwrite(str(debug_folder / "mask_mobs.png"), mask_mobs)
    
    # Visualização com raio
    vis = minimapa.copy()
    cv2.circle(vis, (centro_x, centro_y), raio, (0, 255, 0), 2)
    cv2.putText(vis, f"{mobs_atual}px", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imwrite(str(debug_folder / "minimapa_com_raio.png"), vis)
    
    print(f"\n💾 Debug salvo em: {debug_folder}/")
    print("=" * 60)

if __name__ == "__main__":
    main()
