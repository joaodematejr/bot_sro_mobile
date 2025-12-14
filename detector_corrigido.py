#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector Visual Corrigido - Conta objetos REAIS
Agrupa pixels próximos em objetos únicos
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

class DetectorVisualCorrigido:
    """Detector que conta objetos reais, não pixels"""
    
    def __init__(self):
        # Parâmetros de agrupamento (OTIMIZADOS PARA MINIMAPA)
        self.min_blob_area = 20  # Mobs no minimapa são pequenos!
        self.max_blob_area = 500  # Área máxima pequena (é minimapa)
        self.min_circularity = 0.5  # Muito circular (pontos no minimapa)
        self.min_saturation = 200  # Saturação ALTA (cores vivas)
        
    def detectar_objetos_reais(self, image_path: str, crop_minimap: bool = True):
        """
        Detecta objetos REAIS agrupando pixels próximos
        Retorna contagem precisa de cada tipo
        
        Args:
            image_path: Caminho da imagem
            crop_minimap: Se True, recorta apenas o minimapa antes de analisar
        """
        img = cv2.imread(image_path)
        
        if img is None:
            print(f"❌ Erro ao abrir: {image_path}")
            return None
        
        # Recorta minimapa se solicitado
        if crop_minimap:
            # Coordenadas do config_farming_adb.json
            minimap_x = 150
            minimap_y = 150
            minimap_w = 200
            minimap_h = 200
            
            # Recorta região do minimapa
            img = img[minimap_y:minimap_y+minimap_h, minimap_x:minimap_x+minimap_w]
            
            print(f"📍 Analisando apenas o MINIMAPA ({minimap_w}x{minimap_h})")
        
        # Converte para HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define ranges de cor (OTIMIZADOS PARA MINIMAPA)
        ranges_cores = {
            'vermelho_mob': [
                # Mobs no minimapa são vermelho MUITO BRILHANTE
                ([0, 200, 200], [10, 255, 255]),     # Vermelho baixo
                ([170, 200, 200], [180, 255, 255])   # Vermelho alto
            ],
            'azul': [
                # Items/NPCs azul SATURADO
                ([100, 180, 180], [130, 255, 255])
            ],
            'amarelo': [
                # Player (você) - amarelo MUITO BRILHANTE
                ([20, 200, 200], [35, 255, 255])
            ],
            'verde': [
                # Party members - verde SATURADO
                ([45, 180, 180], [75, 255, 255])
            ]
        }
        
        resultados = {}
        img_debug = img.copy()
        
        for cor_nome, ranges in ranges_cores.items():
            # Cria máscara combinada
            mask_combined = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            for (lower, upper) in ranges:
                lower_np = np.array(lower)
                upper_np = np.array(upper)
                mask = cv2.inRange(hsv, lower_np, upper_np)
                mask_combined = cv2.bitwise_or(mask_combined, mask)
            
            # Remove ruído (MAIS AGRESSIVO)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask_combined = cv2.morphologyEx(mask_combined, cv2.MORPH_OPEN, kernel, iterations=2)
            mask_combined = cv2.morphologyEx(mask_combined, cv2.MORPH_CLOSE, kernel)
            
            # Dilata levemente para unir pixels próximos
            mask_combined = cv2.dilate(mask_combined, kernel, iterations=1)
            
            # Encontra contornos (objetos separados)
            contours, _ = cv2.findContours(
                mask_combined, 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filtra contornos válidos
            objetos_validos = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filtra por área
                if area < self.min_blob_area or area > self.max_blob_area:
                    continue
                
                # Calcula circularidade
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # Aceita objetos minimamente circulares
                if circularity >= self.min_circularity:
                    objetos_validos.append(contour)
                    
                    # Desenha no debug
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    if cor_nome == 'vermelho_mob':
                        cor_debug = (0, 0, 255)  # Vermelho
                    elif cor_nome == 'azul':
                        cor_debug = (255, 0, 0)  # Azul
                    elif cor_nome == 'amarelo':
                        cor_debug = (0, 255, 255)  # Amarelo
                    else:
                        cor_debug = (0, 255, 0)  # Verde
                    
                    cv2.rectangle(img_debug, (x, y), (x+w, y+h), cor_debug, 2)
                    cv2.putText(
                        img_debug, 
                        f"{area:.0f}px", 
                        (x, y-5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.4, 
                        cor_debug, 
                        1
                    )
            
            resultados[cor_nome] = len(objetos_validos)
        
        # Salva imagem debug
        debug_dir = Path("debug_deteccao")
        debug_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salva minimapa cortado também
        if crop_minimap:
            minimap_path = debug_dir / f"minimap_{timestamp}.jpg"
            cv2.imwrite(str(minimap_path), img)
            
            # Limpa imagens antigas (mantém apenas 10)
            self._cleanup_old_images(debug_dir, pattern="minimap_*.jpg", max_keep=10)
        
        debug_path = debug_dir / f"deteccao_{timestamp}.jpg"
        cv2.imwrite(str(debug_path), img_debug)
        
        # Limpa detecções antigas (mantém apenas 10)
        self._cleanup_old_images(debug_dir, pattern="deteccao_*.jpg", max_keep=10)
        
        return resultados, debug_path
    
    def _cleanup_old_images(self, folder: Path, pattern: str = "*.jpg", max_keep: int = 10):
        """Remove imagens antigas mantendo apenas as N mais recentes"""
        try:
            images = sorted(folder.glob(pattern), key=lambda x: x.stat().st_mtime)
            
            if len(images) > max_keep:
                to_remove = len(images) - max_keep
                for img in images[:to_remove]:
                    img.unlink()
        except Exception as e:
            pass  # Silencioso
    
    def analisar_contexto(self, resultados: dict) -> dict:
        """
        Interpreta os resultados e define contexto
        """
        mobs = resultados.get('vermelho_mob', 0)
        items = resultados.get('azul', 0)
        markers = resultados.get('amarelo', 0)
        npcs = resultados.get('verde', 0)
        
        contexto = {
            'situacao': '',
            'acao_recomendada': '',
            'prioridade': 0
        }
        
        # Análise de situação
        if mobs >= 5:
            contexto['situacao'] = 'PERIGO - Muitos mobs'
            contexto['acao_recomendada'] = 'AOE / Fugir'
            contexto['prioridade'] = 3
        elif mobs >= 3:
            contexto['situacao'] = 'Combate intenso'
            contexto['acao_recomendada'] = 'Combate multi-target'
            contexto['prioridade'] = 2
        elif mobs >= 1:
            contexto['situacao'] = 'Combate normal'
            contexto['acao_recomendada'] = 'Atacar mobs'
            contexto['prioridade'] = 1
        else:
            contexto['situacao'] = 'Área limpa'
            contexto['acao_recomendada'] = 'Explorar / Coletar items'
            contexto['prioridade'] = 0
        
        # Items no chão
        if items >= 3:
            contexto['acao_recomendada'] += ' + Coletar items'
        
        return contexto


def testar_com_screenshot(image_path: str):
    """Testa detector com uma screenshot"""
    
    print("\n" + "="*70)
    print("🔍 DETECTOR VISUAL CORRIGIDO")
    print("="*70)
    
    detector = DetectorVisualCorrigido()
    
    print(f"\n📸 Analisando: {image_path}")
    
    result = detector.detectar_objetos_reais(image_path)
    
    if result is None:
        print("\n❌ Erro ao processar imagem!")
        print("   Verifique se o arquivo existe e é uma imagem válida")
        return
    
    resultados, debug_path = result
    
    print("\n📊 OBJETOS DETECTADOS (REAIS):")
    print("-" * 70)
    
    print(f"  🔴 Mobs (vermelho): {resultados['vermelho_mob']}")
    print(f"  🔵 Items/NPCs (azul): {resultados['azul']}")
    print(f"  🟡 Markers (amarelo): {resultados['amarelo']}")
    print(f"  🟢 NPCs amigos (verde): {resultados['verde']}")
    
    # Análise de contexto
    contexto = detector.analisar_contexto(resultados)
    
    print("\n🎯 ANÁLISE DO CONTEXTO:")
    print("-" * 70)
    print(f"  Situação: {contexto['situacao']}")
    print(f"  Recomendação: {contexto['acao_recomendada']}")
    print(f"  Prioridade: {'🔥' * contexto['prioridade'] if contexto['prioridade'] > 0 else '✅'}")
    
    print(f"\n💾 Imagem debug salva: {debug_path}")
    print("   Abra para ver objetos detectados com caixas!")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Usa arquivo passado como argumento
        testar_com_screenshot(sys.argv[1])
    else:
        # Procura última screenshot
        screenshots_dir = Path(".")
        
        # Tenta diferentes extensões
        screenshots = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            screenshots.extend(screenshots_dir.glob(ext))
        
        if screenshots:
            # Ordena por data de modificação
            latest = max(screenshots, key=lambda p: p.stat().st_mtime)
            print(f"\n🔍 Usando screenshot mais recente: {latest}")
            testar_com_screenshot(str(latest))
        else:
            print("\n❌ Nenhuma screenshot encontrada!")
            print("\nUso:")
            print("  python3 detector_corrigido.py screenshot.png")
            print("\nOu coloque uma imagem .png/.jpg na pasta atual")
