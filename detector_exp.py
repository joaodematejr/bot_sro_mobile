#!/usr/bin/env python3
"""
Detector de EXP após combate
Usa OCR para capturar a quantidade de EXP ganha
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import re

class DetectorEXP:
    def __init__(self):
        """Inicializa o detector de EXP"""
        # Região CENTRALIZADA onde aparece o texto de EXP (otimizado para 1920x993)
        # Centro da tela: onde aparece "EXP 25528" com seta verde (30% largura x 20% altura)
        self.regiao_exp = {
            'x': 672,
            'y': 397,
            'largura': 576,
            'altura': 198
        }
    
    def calibrar_regiao(self, screenshot, x, y, largura, altura):
        """
        Define a região onde aparece o texto de EXP
        
        Args:
            screenshot: PIL Image da tela completa
            x, y: Coordenadas do canto superior esquerdo
            largura, altura: Dimensões da região
        """
        self.regiao_exp = {
            'x': x,
            'y': y,
            'largura': largura,
            'altura': altura
        }
        print(f"✓ Região de EXP calibrada: ({x}, {y}) {largura}x{altura}")
    
    def extrair_regiao_exp(self, screenshot):
        """Extrai apenas a região do texto de EXP"""
        if self.regiao_exp['largura'] == 0:
            # Se não calibrado, usa região padrão no centro
            w, h = screenshot.size
            self.regiao_exp = {
                'x': int(w * 0.35),
                'y': int(h * 0.35),
                'largura': int(w * 0.30),
                'altura': int(h * 0.20)
            }
        
        return screenshot.crop((
            self.regiao_exp['x'],
            self.regiao_exp['y'],
            self.regiao_exp['x'] + self.regiao_exp['largura'],
            self.regiao_exp['y'] + self.regiao_exp['altura']
        ))
    
    def preprocessar_para_ocr(self, imagem):
        """
        Preprocessa imagem para melhorar OCR
        Otimizado para texto azul em caixa alta com números
        """
        # Converte PIL para numpy
        img_np = np.array(imagem.convert('RGB'))
        
        # Converte para escala de cinza
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # THRESHOLD INVERTIDO - funciona melhor para texto azul escuro
        # Detecta pixels ESCUROS (texto) em fundo claro
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        # Limpa ruído com operação morfológica
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Redimensiona 4x para melhor OCR (otimizado via testes)
        h, w = thresh.shape
        resized = cv2.resize(thresh, (w*4, h*4), interpolation=cv2.INTER_CUBIC)
        
        return Image.fromarray(resized)
    
    def detectar_exp_ganho(self, screenshot, debug=False):
        """
        Detecta quanto EXP foi ganho na tela
        
        Procura por padrões como:
        - "EXP +1234"
        - "+1234 EXP"
        - "Ganhou 1234 EXP"
        
        Args:
            screenshot: PIL Image da tela
            debug: Se True, salva imagens de debug
        
        Returns:
            int: Quantidade de EXP ganho, ou None se não detectado
        """
        # Extrai região
        regiao = self.extrair_regiao_exp(screenshot)
        
        # Preprocessa
        processada = self.preprocessar_para_ocr(regiao)
        
        if debug:
            regiao.save('debug_exp_original.png')
            processada.save('debug_exp_processada.png')
        
        # OCR otimizado para números - tenta múltiplas configurações
        configs_ocr = [
            '--psm 6 --oem 3',  # Assume bloco uniforme de texto
            '--psm 7 --oem 3',  # Linha única de texto
            '--psm 11 --oem 3', # Texto esparso sem ordem
            '--psm 6 --oem 3 -c tessedit_char_whitelist=EXP+0123456789 ',  # Apenas EXP e números
        ]
        
        texto_completo = ""
        for config in configs_ocr:
            texto = pytesseract.image_to_string(processada, config=config)
            texto_completo += " " + texto
            
            if debug and texto.strip():
                print(f"  📝 OCR ({config[:10]}): {texto.strip()[:50]}")
        
        if debug and not texto_completo.strip():
            print(f"  📝 Nenhum texto detectado em nenhuma config")
        
        # Procura por números após "EXP" ou "+"
        # Usa texto_completo de todas as tentativas de OCR
        padroes = [
            r'EXP\s*[+]?\s*(\d{3,6})',     # EXP +25528 ou EXP 25528
            r'(\d{3,6})\s*EXP',             # 25528 EXP  
            r'\+\s*(\d{3,6})',              # +25528
            r'(\d{4,6})',                    # 25528 direto (4-6 dígitos)
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto_completo, re.IGNORECASE)
            if match:
                exp = int(match.group(1))
                # Valida faixa razoável (100 a 999999)
                if 100 <= exp <= 999999:
                    if debug:
                        print(f"  ✓ EXP detectado: {exp} (padrão: {padrao})")
                    return exp
        
        if debug:
            print("  ✗ Nenhum EXP detectado")
        
        return None
    
    def detectar_exp_com_timeout(self, bot_adb, timeout=3.0, intervalo=0.3, debug=False):
        """
        Tenta detectar EXP múltiplas vezes durante um período
        
        Útil porque o texto de EXP pode aparecer e desaparecer rapidamente
        
        Args:
            bot_adb: Instância do bot com método screenshot
            timeout: Tempo máximo para tentar (segundos)
            intervalo: Intervalo entre tentativas (segundos)
            debug: Modo debug
        
        Returns:
            int: Maior valor de EXP detectado, ou None
        """
        import time
        
        valores_detectados = []
        tempo_inicio = time.time()
        
        while time.time() - tempo_inicio < timeout:
            screenshot = bot_adb.adb.screenshot()
            if screenshot:
                exp = self.detectar_exp_ganho(screenshot, debug=debug)
                if exp is not None:
                    valores_detectados.append(exp)
            
            time.sleep(intervalo)
        
        if valores_detectados:
            # Retorna o valor mais comum (ou o maior se empate)
            from collections import Counter
            contagem = Counter(valores_detectados)
            mais_comum = contagem.most_common(1)[0][0]
            
            if debug:
                print(f"  📊 Valores detectados: {valores_detectados}")
                print(f"  ✓ Valor escolhido: {mais_comum}")
            
            return mais_comum
        
        return None


if __name__ == '__main__':
    """Modo de teste/calibração"""
    import sys
    
    print("🔍 Detector de EXP - Modo Calibração")
    print("=" * 60)
    print()
    print("Este script ajuda a encontrar a região onde aparece o EXP")
    print()
    print("Instruções:")
    print("  1. Mate alguns inimigos para ver o texto de EXP")
    print("  2. Tire um screenshot com ADB")
    print("  3. Use uma ferramenta para medir coordenadas")
    print("  4. Configure a região no config")
    print()
    
    # Exemplo de uso
    detector = DetectorEXP()
    
    # Calibração manual (você ajusta estes valores)
    print("📝 Exemplo de calibração:")
    print("  detector.calibrar_regiao(screenshot, x=500, y=200, largura=400, altura=150)")
    print()
    print("💡 Dica: Use o calibrador_interativo.py para encontrar as coordenadas!")