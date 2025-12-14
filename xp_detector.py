#!/usr/bin/env python3
"""
XP Gain Detector - Detecta quantidade exata de EXP ganho via OCR
Analisa screenshots de exp_gain para extrair valores numéricos
"""

import cv2
import numpy as np
import pytesseract
from pathlib import Path
from typing import Optional, List, Tuple
import re


class XPGainDetector:
    """Detecta e extrai valores de XP ganho de screenshots"""
    
    def __init__(self):
        # Configuração OCR otimizada para números
        self.ocr_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789+.,'
        
        # Padrões de XP ganho
        self.xp_patterns = [
            r'(\d+[\d,]*)\s*EXP',  # "1234 EXP"
            r'EXP\s*[+:]?\s*(\d+[\d,]*)',  # "EXP: 1234"
            r'\+\s*(\d+[\d,]*)',  # "+1234"
            r'(\d{2,})'  # Qualquer número com 2+ dígitos
        ]
    
    def detect_xp_from_image(self, image_path: str) -> Optional[float]:
        """
        Detecta valor de XP ganho em uma imagem
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Valor de XP detectado ou None
        """
        try:
            # Carrega imagem
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Pré-processamento para OCR
            processed = self._preprocess_for_ocr(img)
            
            # Aplica OCR
            text = pytesseract.image_to_string(processed, config=self.ocr_config)
            
            # Extrai número
            xp_value = self._parse_xp_value(text)
            
            return xp_value
            
        except Exception as e:
            return None
    
    def _preprocess_for_ocr(self, img: np.ndarray) -> np.ndarray:
        """
        Pré-processa imagem para melhorar OCR de números
        - Converte para grayscale
        - Aumenta contraste
        - Aplica threshold
        - Redimensiona
        """
        # Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aumenta contraste com CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Threshold adaptativo
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Inverte se necessário (texto branco em fundo escuro)
        if np.mean(thresh) < 127:
            thresh = cv2.bitwise_not(thresh)
        
        # Redimensiona 2x para melhorar OCR
        h, w = thresh.shape
        thresh = cv2.resize(thresh, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
        
        # Remove ruído
        thresh = cv2.medianBlur(thresh, 3)
        
        return thresh
    
    def _parse_xp_value(self, text: str) -> Optional[float]:
        """
        Extrai valor numérico de XP do texto OCR
        Tenta múltiplos padrões e retorna o maior valor encontrado
        """
        text = text.strip()
        
        if not text:
            return None
        
        values = []
        
        # Tenta cada padrão
        for pattern in self.xp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove vírgulas e converte
                    value = float(match.replace(',', ''))
                    
                    # Filtro de sanidade (XP razoável: 1 a 99999)
                    if 1 <= value <= 99999:
                        values.append(value)
                except:
                    continue
        
        # Retorna maior valor encontrado
        if values:
            return max(values)
        
        return None
    
    def process_folder(self, folder_path: str, limit: int = None) -> List[Tuple[str, float]]:
        """
        Processa pasta de screenshots e extrai valores de XP
        
        Args:
            folder_path: Caminho da pasta com screenshots
            limit: Número máximo de imagens a processar
            
        Returns:
            Lista de (filename, xp_value)
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            return []
        
        results = []
        
        # Lista arquivos PNG
        png_files = sorted(folder.glob("*.png"))
        
        if limit:
            png_files = png_files[:limit]
        
        print(f"\n🔍 Processando {len(png_files)} imagens...")
        
        for i, filepath in enumerate(png_files, 1):
            xp_value = self.detect_xp_from_image(str(filepath))
            
            if xp_value:
                results.append((filepath.name, xp_value))
                print(f"  [{i}/{len(png_files)}] {filepath.name}: +{xp_value:.0f} XP")
            else:
                if i % 10 == 0:
                    print(f"  [{i}/{len(png_files)}] Processando...")
        
        return results
    
    def get_statistics(self, xp_values: List[float]) -> dict:
        """Calcula estatísticas dos valores de XP"""
        if not xp_values:
            return {}
        
        import statistics
        
        return {
            'total': sum(xp_values),
            'count': len(xp_values),
            'mean': statistics.mean(xp_values),
            'median': statistics.median(xp_values),
            'min': min(xp_values),
            'max': max(xp_values),
            'stdev': statistics.stdev(xp_values) if len(xp_values) > 1 else 0
        }


def test_xp_detector():
    """Testa detector de XP em pasta de screenshots"""
    detector = XPGainDetector()
    
    # Processa pasta exp_ganho_treino
    results = detector.process_folder("exp_ganho_treino", limit=50)
    
    if results:
        print(f"\n✓ {len(results)} valores detectados")
        
        xp_values = [xp for _, xp in results]
        stats = detector.get_statistics(xp_values)
        
        print("\n📊 Estatísticas:")
        print(f"  Total XP: {stats['total']:.0f}")
        print(f"  Média: {stats['mean']:.2f} XP")
        print(f"  Mediana: {stats['median']:.0f} XP")
        print(f"  Min: {stats['min']:.0f} XP")
        print(f"  Max: {stats['max']:.0f} XP")
        print(f"  Desvio padrão: {stats['stdev']:.2f}")
    else:
        print("\n✗ Nenhum valor de XP detectado")
        print("⚠️  Certifique-se que:")
        print("  1. As imagens estão em PNG válido")
        print("  2. Tesseract está instalado")
        print("  3. A região capturada contém o texto de XP")


if __name__ == "__main__":
    test_xp_detector()
