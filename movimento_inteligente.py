"""
Sistema de Movimento Automático Inteligente
Analisa minimapa e move personagem para áreas com mais mobs
"""
import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict
from pathlib import Path
import time
import math


class MovimentoInteligente:
    """Sistema de movimento automático baseado em análise do minimapa"""
    
    def __init__(self, adb, config: Dict):
        """
        Args:
            adb: Conexão ADB
            config: Configuração com região do minimapa e joystick
        """
        self.adb = adb
        
        # Região do minimapa
        regiao = config.get('regiao_minimap', {})
        self.minimap_x = regiao.get('x', 231)
        self.minimap_y = regiao.get('y', 255)
        self.minimap_w = regiao.get('width', 200)
        self.minimap_h = regiao.get('height', 200)
        
        # Joystick virtual
        self.joystick_x = config.get('joystick_centro_x', 150)
        self.joystick_y = config.get('joystick_centro_y', 850)
        self.joystick_raio = config.get('joystick_raio', 80)
        
        # Configurações de movimento
        movimento_config = config.get('movimento_automatico_config', {})
        self.min_mobs_para_ficar = movimento_config.get('min_mobs_area', 2)
        self.max_mobs_seguro = movimento_config.get('max_mobs_seguro', 5)  # NOVO: limite máximo
        self.raio_busca = movimento_config.get('raio_busca_pixels', 80)
        self.tempo_movimento = movimento_config.get('tempo_movimento_segundos', 2.5)
        self.intervalo_verificacao = movimento_config.get('intervalo_verificacao', 30)        
        # Configurações de kiting
        self.usar_kiting = movimento_config.get('usar_kiting', False)
        self.kiting_raio = movimento_config.get('kiting_raio_pixels', 40)
        self.kiting_duracao_passo = movimento_config.get('kiting_duracao_passo', 0.8)
        self.kiting_num_passos = movimento_config.get('kiting_num_passos', 8)        
        # Estado
        self.ultimo_movimento = 0
        self.ultimo_kiting = 0
        self.posicao_atual_estimada = (self.minimap_w // 2, self.minimap_h // 2)
        self.historico_densidade = []
        
        # Debug
        self.debug_folder = Path("debug_movimento")
        self.debug_folder.mkdir(exist_ok=True)
        
        print("🚶 Sistema de Movimento Inteligente inicializado")
        print(f"   Minimapa: ({self.minimap_x}, {self.minimap_y}) {self.minimap_w}x{self.minimap_h}")
        print(f"   Joystick: ({self.joystick_x}, {self.joystick_y}) raio={self.joystick_raio}")
        print(f"   Min mobs: {self.min_mobs_para_ficar}, Verificação: {self.intervalo_verificacao}s")
        if self.usar_kiting:
            print(f"   🔄 Kiting habilitado: raio={self.kiting_raio}px, {self.kiting_num_passos} passos")
    
    def analisar_densidade_mobs(self, screenshot_path: str, debug: bool = False) -> Dict:
        """
        Analisa densidade de mobs em diferentes direções do minimapa
        
        Returns:
            Dict com densidade em cada direção e recomendação de movimento
        """
        img = cv2.imread(screenshot_path)
        if img is None:
            return {'precisa_mover': False, 'mobs_atual': 0}
        
        # Recorta minimapa
        minimap = img[self.minimap_y:self.minimap_y+self.minimap_h,
                     self.minimap_x:self.minimap_x+self.minimap_w]
        
        if debug:
            cv2.imwrite(str(self.debug_folder / "minimap_completo.png"), minimap)
        
        # Converte para HSV
        hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
        
        # Detecta mobs (vermelho)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_mobs = cv2.bitwise_or(mask1, mask2)
        
        # Centro do minimapa (posição do player)
        centro_x = self.minimap_w // 2
        centro_y = self.minimap_h // 2
        
        # Analisa densidade em 8 direções ao redor do player
        direcoes = {
            'norte':     (0, -1),
            'nordeste':  (1, -1),
            'leste':     (1, 0),
            'sudeste':   (1, 1),
            'sul':       (0, 1),
            'sudoeste':  (-1, 1),
            'oeste':     (-1, 0),
            'noroeste':  (-1, -1)
        }
        
        densidade_por_direcao = {}
        melhor_direcao = None
        max_densidade = 0
        direcao_fuga = None  # NOVO: direção para fugir se muito perigoso
        min_densidade = float('inf')
        
        # Analisa cada direção
        for nome, (dx, dy) in direcoes.items():
            # Define região circular na direção
            angulo = math.atan2(dy, dx)
            
            # Cria máscara circular nessa direção
            mask_direcao = np.zeros_like(mask_mobs)
            
            # Preenche setor circular
            for r in range(30, self.raio_busca):  # De 30 a raio_busca pixels do centro
                for theta in np.linspace(angulo - np.pi/4, angulo + np.pi/4, 20):
                    x = int(centro_x + r * np.cos(theta))
                    y = int(centro_y + r * np.sin(theta))
                    
                    if 0 <= x < self.minimap_w and 0 <= y < self.minimap_h:
                        cv2.circle(mask_direcao, (x, y), 5, 255, -1)
            
            # Conta mobs nessa direção
            mobs_direcao = cv2.bitwise_and(mask_mobs, mask_direcao)
            pixels_vermelho = cv2.countNonZero(mobs_direcao)
            
            densidade_por_direcao[nome] = pixels_vermelho
            
            # Melhor direção: mais mobs, mas NÃO mais que o limite seguro
            if pixels_vermelho > max_densidade and pixels_vermelho <= self.max_mobs_seguro * 50:
                max_densidade = pixels_vermelho
                melhor_direcao = nome
            
            # Direção de fuga: MENOS mobs (para fugir se necessário)
            if pixels_vermelho < min_densidade:
                min_densidade = pixels_vermelho
                direcao_fuga = nome
            
            if debug:
                # Salva máscara de cada direção
                cv2.imwrite(str(self.debug_folder / f"direcao_{nome}.png"), mobs_direcao)
        
        # Conta mobs próximos ao player (raio de 30 pixels)
        mask_perto = np.zeros_like(mask_mobs)
        cv2.circle(mask_perto, (centro_x, centro_y), 30, 255, -1)
        mobs_perto = cv2.bitwise_and(mask_mobs, mask_perto)
        mobs_atual = cv2.countNonZero(mobs_perto)
        
        # ========= LÓGICA DE SEGURANÇA =========
        # 1. PERIGO: Se tem MUITOS mobs perto → FUGIR
        em_perigo = mobs_atual > self.max_mobs_seguro * 50
        
        # 2. POUCOS: Se tem poucos mobs → BUSCAR área melhor
        poucos_mobs = mobs_atual < self.min_mobs_para_ficar * 50
        
        # 3. DECISÃO:
        if em_perigo:
            # FUGIR para onde tem MENOS mobs
            precisa_mover = True
            melhor_direcao = direcao_fuga
            print(f"🚨 PERIGO! {mobs_atual} pixels de mobs → Fugindo para {direcao_fuga}")
        elif poucos_mobs and max_densidade > mobs_atual * 1.5:
            # BUSCAR área com mais mobs (mas não perigosa)
            precisa_mover = True
            print(f"🔍 Poucos mobs ({mobs_atual}) → Indo para {melhor_direcao} ({max_densidade} pixels)")
        else:
            # FICAR: área está boa
            precisa_mover = False
            print(f"✅ Área boa ({mobs_atual} pixels) → Ficando aqui")
        
        resultado = {
            'precisa_mover': precisa_mover,
            'mobs_atual': mobs_atual,
            'melhor_direcao': melhor_direcao,
            'densidade_direcao': densidade_por_direcao,
            'max_densidade': max_densidade,
            'em_perigo': em_perigo,
            'direcao_fuga': direcao_fuga
        }
        
        if debug:
            # Desenha análise no minimapa
            minimap_debug = minimap.copy()
            
            # Círculo ao redor do player
            cv2.circle(minimap_debug, (centro_x, centro_y), 30, (0, 255, 255), 2)
            
            # Seta para melhor direção
            if melhor_direcao and precisa_mover:
                dx, dy = direcoes[melhor_direcao]
                fim_x = int(centro_x + dx * 50)
                fim_y = int(centro_y + dy * 50)
                cv2.arrowedLine(minimap_debug, (centro_x, centro_y), (fim_x, fim_y), 
                               (0, 255, 0), 3, tipLength=0.3)
                cv2.putText(minimap_debug, melhor_direcao, (fim_x, fim_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.imwrite(str(self.debug_folder / "analise_movimento.png"), minimap_debug)
            cv2.imwrite(str(self.debug_folder / "mobs_detectados.png"), mask_mobs)
        
        return resultado
    
    def mover_para_direcao(self, direcao: str, duracao: float = 2.5) -> bool:
        """
        Move o personagem na direção especificada usando joystick
        
        Args:
            direcao: norte, sul, leste, oeste, nordeste, sudeste, noroeste, sudoeste
            duracao: tempo de movimento em segundos
            
        Returns:
            True se movimento foi executado
        """
        # Mapeamento de direções para coordenadas do joystick
        direcoes_joystick = {
            'norte':     (0, -1),
            'nordeste':  (0.7, -0.7),
            'leste':     (1, 0),
            'sudeste':   (0.7, 0.7),
            'sul':       (0, 1),
            'sudoeste':  (-0.7, 0.7),
            'oeste':     (-1, 0),
            'noroeste':  (-0.7, -0.7)
        }
        
        if direcao not in direcoes_joystick:
            print(f"⚠️  Direção inválida: {direcao}")
            return False
        
        dx, dy = direcoes_joystick[direcao]
        
        # Calcula posição no joystick (80% do raio para movimento mais suave)
        offset_x = int(dx * self.joystick_raio * 0.8)
        offset_y = int(dy * self.joystick_raio * 0.8)
        
        target_x = self.joystick_x + offset_x
        target_y = self.joystick_y + offset_y
        
        print(f"🚶 Movendo para {direcao}...")
        print(f"   Joystick: ({target_x}, {target_y}) por {duracao}s")
        
        # Toca no joystick e arrasta
        self.adb.swipe(self.joystick_x, self.joystick_y, target_x, target_y, 
                       duration=int(duracao * 1000))
        
        return True
    
    def fazer_kiting(self, duracao_total: float = 6.0) -> bool:
        """
        Executa movimento circular (kiting) para agregar mobs
        Move em círculo pequeno ao redor da posição atual
        
        Args:
            duracao_total: tempo total do movimento circular em segundos
            
        Returns:
            True se kiting foi executado
        """
        print(f"\n🔄 Iniciando kiting circular para agregar mobs...")
        
        # Define 8 direções para fazer um círculo
        direcoes_circulo = [
            ('norte', 0, -1),
            ('nordeste', 0.7, -0.7),
            ('leste', 1, 0),
            ('sudeste', 0.7, 0.7),
            ('sul', 0, 1),
            ('sudoeste', -0.7, 0.7),
            ('oeste', -1, 0),
            ('noroeste', -0.7, -0.7)
        ]
        
        # Executa movimento em cada direção
        for i, (nome, dx, dy) in enumerate(direcoes_circulo[:self.kiting_num_passos]):
            # Calcula posição no joystick (usa raio menor para círculo pequeno)
            offset_x = int(dx * self.kiting_raio)
            offset_y = int(dy * self.kiting_raio)
            
            target_x = self.joystick_x + offset_x
            target_y = self.joystick_y + offset_y
            
            # Move nessa direção por tempo curto
            self.adb.swipe(self.joystick_x, self.joystick_y, target_x, target_y,
                          duration=int(self.kiting_duracao_passo * 1000))
            
            # Pequena pausa entre passos
            time.sleep(0.1)
        
        print(f"   ✅ Kiting concluído - {self.kiting_num_passos} passos em círculo")
        return True
    
    def verificar_e_mover(self, screenshot_path: str, debug: bool = False) -> bool:
        """
        Verifica se precisa mover e executa movimento se necessário
        
        Returns:
            True se moveu, False se ficou parado
        """
        # Verifica tempo desde último movimento
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_movimento < self.intervalo_verificacao:
            return False
        
        # Analisa densidade
        analise = self.analisar_densidade_mobs(screenshot_path, debug=debug)
        
        # Registra no histórico
        self.historico_densidade.append({
            'timestamp': tempo_atual,
            'mobs_atual': analise['mobs_atual'],
            'melhor_direcao': analise.get('melhor_direcao')
        })
        
        # Mantém apenas últimas 10 análises
        if len(self.historico_densidade) > 10:
            self.historico_densidade.pop(0)
        
        if debug:
            print(f"\n🔍 Análise de Movimento:")
            print(f"   Mobs perto: {analise['mobs_atual']} pixels")
            print(f"   Precisa mover: {analise['precisa_mover']}")
            if analise['precisa_mover']:
                print(f"   Melhor direção: {analise['melhor_direcao']} ({analise['max_densidade']} pixels)")
                print(f"   Densidade por direção:")
                for dir, dens in sorted(analise['densidade_direcao'].items(), key=lambda x: x[1], reverse=True):
                    print(f"      {dir:10s}: {dens:4d} pixels")
        
        # Move se necessário
        if analise['precisa_mover'] and analise['melhor_direcao']:
            # Aumenta a duração se for fuga
            duracao = self.tempo_movimento * (1.4 if analise.get('em_perigo') else 1.0)
            self.mover_para_direcao(analise['melhor_direcao'], duracao)
            self.ultimo_movimento = tempo_atual
            return True
        else:
            # Se área está boa mas detecta mobs distantes, faz kiting para agregar
            if self.usar_kiting and tempo_atual - self.ultimo_kiting >= 60:  # Kiting a cada 60s
                # Verifica se tem mobs na área mas poucos perto
                densidade_total = sum(analise['densidade_direcao'].values())
                if densidade_total > 100 and analise['mobs_atual'] < self.min_mobs_para_ficar * 30:
                    print(f"\n🔄 Detectados mobs distantes ({densidade_total} pixels) - fazendo kiting")
                    self.fazer_kiting()
                    self.ultimo_kiting = tempo_atual
                    self.ultimo_movimento = tempo_atual
                    return True
            
            if debug:
                print(f"   ✅ Área boa, ficando no local")
            self.ultimo_movimento = tempo_atual
            return False
    
    def get_estatisticas(self) -> Dict:
        """Retorna estatísticas do sistema de movimento"""
        if not self.historico_densidade:
            return {'movimentos': 0, 'media_mobs': 0}
        
        media_mobs = np.mean([h['mobs_atual'] for h in self.historico_densidade])
        
        return {
            'total_analises': len(self.historico_densidade),
            'media_mobs_area': media_mobs,
            'ultimo_movimento': time.strftime('%H:%M:%S', time.localtime(self.ultimo_movimento)) if self.ultimo_movimento > 0 else 'Nunca'
        }
