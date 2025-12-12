#!/usr/bin/env python3
"""
Bot ULTRA para Silkroad Origin Mobile via ADB
Controle direto via ADB - muito mais confiável!
"""

import subprocess
import time
import json
import numpy as np
from datetime import datetime
import os
from PIL import Image
import io
import pickle
from detector_exp import DetectorEXP
from ml_avancado import MLAvancado

# Configurações
ARQUIVO_DADOS = "farming_data.json"
ARQUIVO_MODELO = "modelo_ultra_adb.pkl"
ARQUIVO_CONFIG = "config_farming_adb.json"
ADB_DEVICE = "192.168.240.112:5555"

class ConfiguracaoADB:
    """Configurações para controle via ADB"""
    
    def __init__(self):
        self.carregar_config()
    
    def carregar_config(self):
        """Carrega ou cria configuração padrão"""
        default_config = {
            'adb_device': ADB_DEVICE,
            
            # Resolução do dispositivo (detectada automaticamente)
            'screen_width': 1080,
            'screen_height': 2400,
            
            # Joystick (coordenadas absolutas em pixels)
            'joystick_centro_x': 160,
            'joystick_centro_y': 2100,
            'joystick_raio': 80,
            
            # Velocidade
            'velocidade_movimento': 1500,  # ms de swipe
            'intervalo_entre_acoes': 500,  # ms
            
            # Skills (coordenadas absolutas)
            'usar_skills_automaticas': True,
            'intervalo_skills': 3000,  # ms
            'posicoes_skills': [
                {'x': 920, 'y': 1800},  # Skill 1
                {'x': 970, 'y': 1900},  # Skill 2
                {'x': 860, 'y': 1900},  # Skill 3
            ],
            
            # Auto-loot
            'auto_loot': True,
            'posicao_botao_loot': {'x': 540, 'y': 1440},
            
            # Auto-potion
            'auto_potion': True,
            'threshold_hp': 0.5,
            'posicao_hp_bar': {'x': 110, 'y': 120},
            'posicao_botao_potion': {'x': 160, 'y': 2160},
            
            # Barra de XP (para OCR)
            'posicao_xp_bar': {'x': 140, 'y': 2340, 'width': 800, 'height': 50},
            'usar_ocr_xp': True,
            
            # Minimapa (para detecção de inimigos)
            'posicao_minimapa': {'x': 50, 'y': 50, 'width': 200, 'height': 200},
            'usar_minimapa': True,
            'cor_inimigo_minimapa': [255, 0, 0],  # Vermelho (ajuste conforme necessário)
            
            # Detecção
            'verificar_morte': True,
            'cor_morte_rgb': [200, 50, 50],
            
            # Rotação
            'rotacao_areas': True,
            'tempo_max_area': 300,
            'areas_conhecidas': [
                {'x': 30, 'y': 30, 'nome': 'Área Norte'},
                {'x': 70, 'y': 30, 'nome': 'Área Leste'},
                {'x': 50, 'y': 70, 'nome': 'Área Sul'},
            ],
            
            # Anti-AFK
            'anti_afk': True,
            'intervalo_anti_afk': 60,
            
            # Auto-reset câmera
            'auto_reset_camera': True,
            'posicao_botao_camera': {'x': 192, 'y': 150},
            'intervalo_reset_camera': 10,  # segundos
            
            # Treinamento ML
            'salvar_imagens_treino': True,
            'pasta_imagens_treino': 'treino_ml',
            'max_imagens_treino': 100,
            
            # Otimizações de velocidade
            'modo_turbo': True,  # Reduz delays entre ações
            'skip_areas_vazias': True,  # Pula áreas sem inimigos rapidamente
            'priorizar_combate': True,  # Foca em combate ao invés de exploração
            'loot_instantaneo': True,  # Coleta loot sem delay
            'skills_paralelas': True,  # Usa múltiplas skills ao mesmo tempo
            'threshold_inimigos_minimo': 15,  # Mínimo de inimigos para valer a pena
            
            # Métricas
            'arquivo_metricas': 'metricas_bot.json',  # Arquivo JSON para exportar métricas
            'intervalo_salvar_metricas': 5,  # Salva métricas a cada X segundos
            
            # Detector de EXP
            'usar_detector_exp': True,  # Detecta EXP ganho via OCR
            'regiao_exp': {'x': 672, 'y': 397, 'largura': 576, 'altura': 198},  # Região CENTRALIZADA (30% x 20%)
            'exp_necessario_level': 1000000,  # EXP total necessário para próximo level (ajustar)
            'exp_atual_level': 0,  # EXP acumulado no level atual
            
            # ML Avançado
            'usar_ml_avancado': True,  # Sistema ML de otimização
            'treinar_modelos_intervalo': 300,  # Treina modelos a cada 5 min
            'usar_rotas_otimizadas': True,  # Usa rotas recomendadas por ML
            'usar_skills_otimizadas': True,  # Usa rotação de skills otimizada
            'raio_busca_area': 200,  # Raio para buscar próxima melhor área
            
            # Sistema de Análise de Dificuldade
            'monitorar_dificuldade': True,  # Ativa monitoramento de dificuldade
            'limite_perda_vida': 40,  # % vida perdida para considerar "muito forte"
            'max_mortes_area': 2,  # Máximo de mortes antes de evitar área
            'min_combates_analise': 3,  # Mínimo de combates para analisar área
            'recuar_niveis': 5,  # Quantos níveis recuar se área muito forte
            'regiao_vida_bar': {'x': 50, 'y': 50, 'width': 200, 'height': 20},  # Região da barra de vida
            
            # Detecção de Inimigos Perigosos
            'detectar_inimigos_perigosos': True,  # Ativa detecção de inimigos perigosos
            'inimigos_para_fugir': ['Giant', 'Boss', 'Elite', 'Champion'],  # Lista de nomes para fugir
            'regiao_nome_inimigo': {'x': 400, 'y': 100, 'largura': 600, 'altura': 150},  # Região onde aparece nome do inimigo
            'distancia_fuga_segura': 300,  # Distância para fugir do inimigo perigoso
            'intervalo_verificacao_inimigo': 2,  # Segundos entre verificações
        }
        
        loaded_config = {}
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                with open(ARQUIVO_CONFIG, 'r') as f:
                    loaded_config = json.load(f) or {}
            except Exception:
                pass
        
        merged = {**default_config, **loaded_config}
        self.__dict__.update(merged)
        
        # Detecta resolução automaticamente
        self.detectar_resolucao()
        
        # Salva se necessário
        if not os.path.exists(ARQUIVO_CONFIG) or merged.keys() != loaded_config.keys():
            self.salvar_config(merged)
    
    def detectar_resolucao(self):
        """Detecta resolução da tela via ADB"""
        try:
            result = subprocess.run(
                ['adb', '-s', self.adb_device, 'shell', 'wm', 'size'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Output: "Physical size: 1080x2400"
                line = result.stdout.strip()
                if 'x' in line:
                    size = line.split(':')[-1].strip()
                    w, h = map(int, size.split('x'))
                    self.screen_width = w
                    self.screen_height = h
                    print(f"✓ Resolução detectada: {w}x{h}")
        except Exception as e:
            print(f"⚠️  Não foi possível detectar resolução: {e}")
    
    def salvar_config(self, config=None):
        """Salva configuração"""
        if config is None:
            config = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        
        with open(ARQUIVO_CONFIG, 'w') as f:
            json.dump(config, f, indent=2)

class ADBController:
    """Controlador ADB para input e captura"""
    
    def __init__(self, device=ADB_DEVICE):
        self.device = device
        self.verificar_conexao()
    
    def verificar_conexao(self):
        """Verifica se o dispositivo está conectado"""
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if self.device in result.stdout:
                print(f"✅ ADB conectado: {self.device}")
                return True
            else:
                print(f"❌ Dispositivo {self.device} não encontrado!")
                print("\nConecte via: adb connect 192.168.240.112:5555")
                return False
        except Exception as e:
            print(f"❌ Erro ao verificar ADB: {e}")
            return False
    
    def tap(self, x, y):
        """Toca na posição especificada"""
        try:
            subprocess.run(
                ['adb', '-s', self.device, 'shell', 'input', 'tap', str(int(x)), str(int(y))],
                capture_output=True,
                timeout=2
            )
        except Exception as e:
            print(f"⚠️  Erro no tap: {e}")
    
    def swipe(self, x1, y1, x2, y2, duration_ms=500):
        """Swipe (arrasto) de um ponto a outro"""
        try:
            cmd = ['adb', '-s', self.device, 'shell', 'input', 'swipe',
                   str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(int(duration_ms))]
            
            print(f"  🔧 ADB: swipe {int(x1)},{int(y1)} → {int(x2)},{int(y2)} ({int(duration_ms)}ms)")
            
            result = subprocess.run(cmd, capture_output=True, timeout=3)
            
            if result.returncode != 0:
                print(f"  ⚠️  Swipe falhou: {result.stderr.decode()}")
            
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Erro no swipe: {e}")
            return False
    
    def press_and_drag(self, x_start, y_start, x_end, y_end, hold_time_ms=1500):
        """Pressiona, segura e arrasta (para joystick) - usa swipe com duração longa"""
        try:
            print(f"  🔧 ADB: swipe longo {int(x_start)},{int(y_start)} → {int(x_end)},{int(y_end)} ({hold_time_ms}ms)")
            
            # Usa swipe com duração maior - isso mantém o toque pressionado durante todo o trajeto
            # No Android, input swipe X1 Y1 X2 Y2 DURATION significa:
            # - Pressiona em (X1,Y1)
            # - Arrasta até (X2,Y2) durante DURATION ms
            # - Solta
            result = subprocess.run(
                ['adb', '-s', self.device, 'shell', 'input', 'swipe',
                 str(int(x_start)), str(int(y_start)), 
                 str(int(x_end)), str(int(y_end)), 
                 str(int(hold_time_ms))],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                print(f"  ⚠️  Comando falhou: {result.stderr.decode()}")
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️  Erro no press_and_drag: {e}")
            return False
    
    def screenshot(self):
        """Captura screenshot via ADB"""
        try:
            # Método mais confiável: salva no device e puxa
            temp_path = '/sdcard/screen.png'
            
            # Captura e salva no dispositivo
            subprocess.run(
                ['adb', '-s', self.device, 'shell', 'screencap', '-p', temp_path],
                capture_output=True,
                timeout=5
            )
            
            # Puxa o arquivo
            result = subprocess.run(
                ['adb', '-s', self.device, 'pull', temp_path, '/tmp/adb_screen.png'],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0 and os.path.exists('/tmp/adb_screen.png'):
                image = Image.open('/tmp/adb_screen.png')
                
                # Limpa o arquivo do dispositivo
                subprocess.run(
                    ['adb', '-s', self.device, 'shell', 'rm', temp_path],
                    capture_output=True,
                    timeout=2
                )
                
                return image
            else:
                return None
        except Exception as e:
            print(f"⚠️  Erro no screenshot: {e}")
            return None
    
    def get_pixel_color(self, x, y):
        """Obtém cor de um pixel específico"""
        screenshot = self.screenshot()
        if screenshot:
            try:
                pixel = screenshot.getpixel((int(x), int(y)))
                return pixel[:3]  # RGB
            except:
                return None
        return None
    
    def capturar_regiao(self, x, y, width, height):
        """Captura uma região específica da tela"""
        screenshot = self.screenshot()
        if screenshot:
            try:
                return screenshot.crop((x, y, x + width, y + height))
            except:
                return None
        return None

class BotUltraADB:
    """Bot ultra otimizado usando ADB"""
    
    def __init__(self):
        self.config = ConfiguracaoADB()
        self.adb = ADBController(self.config.adb_device)
        
        # ML
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        
        self.X_train = []
        self.y_train = []
        self.modelo = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
        self.modelo_treinado = False
        
        # Estado
        self.pos_x = 50
        self.pos_y = 50
        self.area_atual = 0
        self.tempo_entrada_area = time.time()
        self.ultimo_skill = 0
        self.ultimo_anti_afk = time.time()
        self.ultimo_reset_camera = time.time()
        self.ultimo_salvamento_metricas = time.time()
        self.ultima_screenshot = None
        
        # Detector de EXP
        self.detector_exp = DetectorEXP()
        if self.config.regiao_exp['largura'] > 0:
            self.detector_exp.calibrar_regiao(
                None,
                self.config.regiao_exp['x'],
                self.config.regiao_exp['y'],
                self.config.regiao_exp['largura'],
                self.config.regiao_exp['altura']
            )
        
        # ML Avançado
        self.ml_avancado = None
        if self.config.usar_ml_avancado:
            self.ml_avancado = MLAvancado()
            print("✓ ML Avançado inicializado")
        
        self.ultimo_treino_ml = time.time()
        self.tempo_inicio_area = time.time()
        self.exp_ganho_area = 0
        self.skills_ultima_rotacao = []
        
        # Sistema de Análise de Dificuldade
        self.vida_antes_combate = 100
        self.historico_dificuldade = {}  # {coordenada: {perdas_vida: [], mortes: 0, combates: 0}}
        self.areas_perigosas = set()  # Coordenadas de áreas muito fortes
        self.nivel_recomendado = None  # Nível atual do player
        self.ultima_verificacao_inimigo = time.time()  # Timestamp da última verificação de inimigo perigoso
        self.fugindo_de_inimigo = False  # Flag indicando se está fugindo
        
        # Stats
        self.stats = {
            'tempo_inicio': time.time(),
            'combates': 0,
            'mortes': 0,
            'potions_usadas': 0,
            'skills_usadas': 0,
            'loots_coletados': 0,
            'areas_visitadas': 0,
            'xp_estimado': 0,
            'xp_atual': 0.0,  # Percentual lido via OCR
            'xp_inicial': 0.0,
            'historico_xp': [],  # [(timestamp, xp%)]
            'imagens_salvas': 0,
            'exp_total_ganho': 0,  # EXP real detectado
            'exp_por_combate': [],  # Histórico de EXP por combate
            'exp_atual_level': self.config.exp_atual_level,  # EXP acumulado no level
        }
        
        # Cria pasta de treinamento se necessário
        if self.config.salvar_imagens_treino:
            pasta = self.config.pasta_imagens_treino
            if not os.path.exists(pasta):
                os.makedirs(pasta)
                print(f"✓ Pasta de treinamento criada: {pasta}/")
        
        self.carregar_modelo()
        
        # Captura XP inicial
        if self.config.usar_ocr_xp:
            xp = self.ler_xp_atual()
            if xp is not None:
                self.stats['xp_inicial'] = xp
                self.stats['xp_atual'] = xp
                self.stats['historico_xp'].append((time.time(), xp))
                print(f"✓ XP inicial: {xp:.2f}%")
    
    def mover_joystick(self, angulo, duracao_ms=None, intensidade=1.0, continuo=False):
        """Move usando o joystick via press-and-drag (como no celular)
        
        Args:
            angulo: Direção do movimento em radianos
            duracao_ms: Duração do movimento em milissegundos
            intensidade: Intensidade do movimento (0.0 a 1.0) - distância do centro
            continuo: Se True, mantém movimento contínuo (para ir até área com inimigos)
        """
        if duracao_ms is None:
            duracao_ms = self.config.velocidade_movimento
        
        # Se movimento contínuo, aumenta a duração
        if continuo:
            duracao_ms = int(duracao_ms * 3)  # 3x mais longo para chegar ao destino
            intensidade = 1.0  # Força máxima
        
        # Adiciona variação aleatória para movimento mais natural
        variacao_angulo = np.random.uniform(-0.15, 0.15)  # ±8 graus
        angulo_ajustado = angulo + variacao_angulo
        
        # Adiciona variação na intensidade (70% a 100% do raio)
        intensidade_variada = np.clip(intensidade * np.random.uniform(0.7, 1.0), 0.3, 1.0)
        
        centro_x = self.config.joystick_centro_x
        centro_y = self.config.joystick_centro_y
        raio = self.config.joystick_raio
        
        # Calcula ponto de destino com variação
        raio_efetivo = raio * intensidade_variada
        dest_x = int(centro_x + raio_efetivo * np.cos(angulo_ajustado))
        dest_y = int(centro_y + raio_efetivo * np.sin(angulo_ajustado))
        
        # Adiciona pequena variação no ponto de partida (mais natural)
        inicio_x = int(centro_x + np.random.uniform(-3, 3))
        inicio_y = int(centro_y + np.random.uniform(-3, 3))
        
        movimento_tipo = "CONTÍNUO" if continuo else "normal"
        print(f"  🕹️  Joystick [{movimento_tipo}]: início({inicio_x},{inicio_y}) → destino({dest_x},{dest_y})")
        print(f"  📐 Ângulo: {np.degrees(angulo_ajustado):.1f}° | Intensidade: {intensidade_variada:.1%} | Duração: {duracao_ms}ms")
        
        # Pressiona, arrasta e segura com variação na duração
        duracao_variada = int(duracao_ms * np.random.uniform(0.9, 1.1))
        sucesso = self.adb.press_and_drag(inicio_x, inicio_y, dest_x, dest_y, duracao_variada)
        
        if sucesso:
            print(f"  ✅ Movimento executado!")
        else:
            print(f"  ❌ Movimento falhou!")
        
        # Atualiza posição virtual
        movimento_distancia = 3 if not continuo else 10
        self.pos_x = np.clip(self.pos_x + movimento_distancia * np.cos(angulo), 0, 100)
        self.pos_y = np.clip(self.pos_y + movimento_distancia * np.sin(angulo), 0, 100)
    
    def usar_skill(self, index):
        """Usa skill via tap ADB"""
        if index < len(self.config.posicoes_skills):
            pos = self.config.posicoes_skills[index]
            self.adb.tap(pos['x'], pos['y'])
            self.stats['skills_usadas'] += 1
            print(f"  💥 Skill {index + 1}")
            # Delay reduzido em modo turbo
            delay = 0.1 if self.config.modo_turbo else 0.3
            time.sleep(delay)
    
    def usar_skills_rotacao(self):
        """Usa skills em rotação (paralelo se habilitado, otimizado por ML)"""
        if not self.config.usar_skills_automaticas:
            return
        
        tempo_atual = time.time()
        # Reduz intervalo entre rotações de skills em modo turbo
        intervalo = self.config.intervalo_skills / 1000.0
        if self.config.modo_turbo:
            intervalo *= 0.7  # 30% mais rápido
        
        if tempo_atual - self.ultimo_skill >= intervalo:
            # Tenta obter rotação otimizada por ML
            rotacao_ml = self.obter_rotacao_skills_ml()
            
            if rotacao_ml and len(rotacao_ml) > 0:
                # Usa rotação recomendada pelo ML
                if self.config.skills_paralelas:
                    import threading
                    for skill_id in rotacao_ml:
                        # Converte para int se for string
                        skill_idx = int(skill_id) if isinstance(skill_id, str) else skill_id
                        if skill_idx < len(self.config.posicoes_skills):
                            pos = self.config.posicoes_skills[skill_idx]
                            threading.Thread(target=self.adb.tap, args=(pos['x'], pos['y'])).start()
                            self.registrar_skill_ml(skill_idx, sucesso=True)
                            self.stats['skills_usadas'] += 1
                    print(f"  🤖💥 {len(rotacao_ml)} Skills ML (PARALELO)")
                else:
                    for skill_id in rotacao_ml:
                        # Converte para int se for string
                        skill_idx = int(skill_id) if isinstance(skill_id, str) else skill_id
                        if skill_idx < len(self.config.posicoes_skills):
                            self.usar_skill(skill_idx)
                            self.registrar_skill_ml(skill_idx, sucesso=True)
                    print(f"  🤖💥 Skills ML: {rotacao_ml}")
                
                self.skills_ultima_rotacao = rotacao_ml
            else:
                # Fallback: rotação padrão
                if self.config.skills_paralelas:
                    # Usa todas as skills rapidamente sem esperar
                    import threading
                    for i in range(len(self.config.posicoes_skills)):
                        pos = self.config.posicoes_skills[i]
                        threading.Thread(target=self.adb.tap, args=(pos['x'], pos['y'])).start()
                        self.registrar_skill_ml(i, sucesso=True)
                        self.stats['skills_usadas'] += 1
                    print(f"  💥⚡ {len(self.config.posicoes_skills)} Skills (PARALELO)")
                else:
                    for i in range(len(self.config.posicoes_skills)):
                        self.usar_skill(i)
                        self.registrar_skill_ml(i, sucesso=True)
            
            self.ultimo_skill = tempo_atual
    
    def coletar_loot(self):
        """Coleta loot (múltiplos cliques em modo turbo)"""
        if self.config.auto_loot:
            pos = self.config.posicao_botao_loot
            
            if self.config.loot_instantaneo:
                # Clica múltiplas vezes rapidamente para pegar todo loot
                for _ in range(3):
                    self.adb.tap(pos['x'], pos['y'])
                    time.sleep(0.05)
                print("  💰⚡ Loot x3 (RÁPIDO)")
            else:
                self.adb.tap(pos['x'], pos['y'])
                print("  💰 Loot")
            
            self.stats['loots_coletados'] += 1
    
    def usar_potion(self):
        """Usa potion se HP baixo"""
        if not self.config.auto_potion:
            return
        
        # Verifica HP pela cor da barra
        pos_hp = self.config.posicao_hp_bar
        cor = self.adb.get_pixel_color(pos_hp['x'], pos_hp['y'])
        
        if cor:
            # Se mais vermelho que verde = HP baixo
            if cor[0] > cor[1] * 1.5:
                pos = self.config.posicao_botao_potion
                self.adb.tap(pos['x'], pos['y'])
                self.stats['potions_usadas'] += 1
                print("  🧪 Potion!")
                time.sleep(0.5)
    
    def enviar_notificacao(self, titulo, mensagem):
        """Envia notificação do sistema operacional"""
        try:
            import subprocess
            
            # Notificação Linux (notify-send)
            subprocess.run([
                'notify-send',
                '-u', 'critical',  # Urgência crítica
                '-i', 'dialog-warning',  # Ícone de aviso
                '-t', '10000',  # Duração 10 segundos
                titulo,
                mensagem
            ], check=False, stderr=subprocess.DEVNULL)
            
        except Exception:
            # Se falhar, apenas ignora (não trava o bot)
            pass
    
    def detectar_combate(self, threshold=0.15):
        """Detecta combate por mudança na tela"""
        try:
            import imagehash
            
            screenshot = self.adb.screenshot()
            if not screenshot:
                return False
            
            if self.ultima_screenshot:
                hash1 = imagehash.average_hash(self.ultima_screenshot)
                hash2 = imagehash.average_hash(screenshot)
                diferenca = (hash1 - hash2) / 64.0
                
                self.ultima_screenshot = screenshot
                return diferenca > threshold
            else:
                self.ultima_screenshot = screenshot
                return False
        except:
            return False
    
    def ler_xp_atual(self):
        """Lê a porcentagem de XP atual via OCR"""
        try:
            import pytesseract
            import cv2
        except ImportError:
            return None
        
        try:
            pos = self.config.posicao_xp_bar
            regiao = self.adb.capturar_regiao(
                pos['x'], pos['y'], 
                pos['width'], pos['height']
            )
            
            if regiao is None:
                return None
            
            # Converte para numpy/cv2
            img = np.array(regiao)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            
            # Pre-processamento para melhorar OCR
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            thresh = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            
            # OCR
            config_tesseract = '--psm 7 -c tessedit_char_whitelist=0123456789.%'
            texto = pytesseract.image_to_string(thresh, config=config_tesseract)
            
            # Extrai número
            import re
            match = re.search(r'(\d+\.?\d*)%?', texto)
            if match:
                xp = float(match.group(1))
                if 0 <= xp <= 100:
                    return xp
            
            return None
        except Exception:
            return None
    
    def analisar_minimapa(self):
        """Analisa o minimapa e encontra a direção com mais inimigos"""
        try:
            import cv2
        except ImportError:
            return None
        
        try:
            pos = self.config.posicao_minimapa
            minimapa = self.adb.capturar_regiao(
                pos['x'], pos['y'],
                pos['width'], pos['height']
            )
            
            if minimapa is None:
                return None
            
            # Converte para numpy
            img = np.array(minimapa)
            
            # Detecta pixels vermelhos (inimigos)
            cor_alvo = np.array(self.config.cor_inimigo_minimapa)
            tolerancia = 40
            
            lower = np.clip(cor_alvo - tolerancia, 0, 255)
            upper = np.clip(cor_alvo + tolerancia, 0, 255)
            
            mask = cv2.inRange(img, lower, upper)
            
            # Divide o minimapa em 8 setores (N, NE, E, SE, S, SW, W, NW)
            h, w = mask.shape
            centro_x, centro_y = w // 2, h // 2
            
            setores = {}
            angulos = {
                'N': (0, -np.pi/2),
                'NE': (1, -np.pi/4),
                'E': (2, 0),
                'SE': (3, np.pi/4),
                'S': (4, np.pi/2),
                'SW': (5, 3*np.pi/4),
                'W': (6, np.pi),
                'NW': (7, -3*np.pi/4),
            }
            
            # Conta inimigos por setor
            for nome, (idx, angulo) in angulos.items():
                # Define região do setor (simplificado: quadrantes)
                if idx == 0:  # N
                    regiao = mask[0:centro_y, :]
                elif idx == 1:  # NE
                    regiao = mask[0:centro_y, centro_x:]
                elif idx == 2:  # E
                    regiao = mask[:, centro_x:]
                elif idx == 3:  # SE
                    regiao = mask[centro_y:, centro_x:]
                elif idx == 4:  # S
                    regiao = mask[centro_y:, :]
                elif idx == 5:  # SW
                    regiao = mask[centro_y:, 0:centro_x]
                elif idx == 6:  # W
                    regiao = mask[:, 0:centro_x]
                else:  # NW
                    regiao = mask[0:centro_y, 0:centro_x]
                
                # Conta pixels vermelhos (inimigos)
                count = np.sum(regiao > 0)
                setores[nome] = {'count': count, 'angulo': angulo}
            
            # Encontra setor com mais inimigos
            melhor_setor = max(setores.items(), key=lambda x: x[1]['count'])
            total_inimigos = sum(s['count'] for s in setores.values())
            
            # Retorna info sobre distribuição de inimigos
            # Threshold ajustável baseado em configuração
            threshold_minimo = self.config.threshold_inimigos_minimo if hasattr(self.config, 'threshold_inimigos_minimo') else 10
            
            if melhor_setor[1]['count'] > threshold_minimo:
                # Salva imagem de treinamento se habilitado
                if self.config.salvar_imagens_treino:
                    self.salvar_imagem_treino(minimapa, 'minimapa', melhor_setor[1]['count'])
                
                return {
                    'direcao': melhor_setor[0],
                    'angulo': melhor_setor[1]['angulo'],
                    'inimigos': melhor_setor[1]['count'],
                    'total_inimigos': total_inimigos,
                    'setores': setores,  # Todos os setores para análise
                }
            
            return None
            
        except Exception as e:
            return None
    
    def detectar_nome_inimigo(self):
        """Detecta o nome do inimigo na tela usando OCR"""
        if not self.config.detectar_inimigos_perigosos:
            return None
        
        try:
            import pytesseract
            import cv2
        except ImportError:
            return None
        
        try:
            # Captura região onde aparece o nome do inimigo
            regiao = self.config.regiao_nome_inimigo
            imagem = self.adb.capturar_regiao(
                regiao['x'], regiao['y'],
                regiao['largura'], regiao['altura']
            )
            
            if imagem is None:
                return None
            
            # Preprocessamento para OCR
            img_np = np.array(imagem.convert('RGB'))
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            
            # Threshold para destacar texto
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # Amplia para melhor OCR
            h, w = thresh.shape
            resized = cv2.resize(thresh, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
            
            # OCR
            config = '--psm 7 --oem 3'  # Linha única de texto
            texto = pytesseract.image_to_string(Image.fromarray(resized), config=config)
            
            # Limpa texto
            texto = texto.strip().upper()
            
            if texto:
                # Verifica se contém algum nome perigoso
                for inimigo in self.config.inimigos_para_fugir:
                    if inimigo.upper() in texto:
                        return inimigo
            
            return None
            
        except Exception as e:
            return None
    
    def fugir_de_inimigo_perigoso(self):
        """Foge do inimigo perigoso até estar a uma distância segura"""
        print("\n⚠️  INIMIGO PERIGOSO DETECTADO! FUGINDO...")
        
        # Envia notificação do sistema
        self.enviar_notificacao(
            "⚠️ ALERTA DE PERIGO!",
            "Inimigo perigoso detectado! Bot está fugindo..."
        )
        
        self.fugindo_de_inimigo = True
        
        # Move para trás rapidamente (direção oposta)
        tentativas = 0
        max_tentativas = 10
        
        while tentativas < max_tentativas:
            # Move para trás
            self.mover_direcao(np.pi, duracao=1.0)  # Move para baixo (180°)
            time.sleep(0.3)
            
            # Verifica se ainda detecta o inimigo
            nome_inimigo = self.detectar_nome_inimigo()
            
            if not nome_inimigo:
                print("  ✅ Distância segura alcançada!")
                self.fugindo_de_inimigo = False
                return True
            
            tentativas += 1
            print(f"  🏃 Fugindo... ({tentativas}/{max_tentativas})")
        
        print("  ⚠️  Não conseguiu fugir completamente, continuando farming...")
        self.fugindo_de_inimigo = False
        return False
    
    def verificar_inimigo_perigoso(self):
        """Verifica periodicamente se há inimigo perigoso próximo"""
        if not self.config.detectar_inimigos_perigosos:
            return False
        
        # Verifica apenas em intervalos
        tempo_atual = time.time()
        if tempo_atual - self.ultima_verificacao_inimigo < self.config.intervalo_verificacao_inimigo:
            return False
        
        self.ultima_verificacao_inimigo = tempo_atual
        
        # Detecta nome do inimigo
        nome_inimigo = self.detectar_nome_inimigo()
        
        if nome_inimigo:
            print(f"\n🚨 ALERTA: {nome_inimigo} detectado!")
            
            # Notificação específica com nome do inimigo
            self.enviar_notificacao(
                f"🚨 {nome_inimigo} DETECTADO!",
                f"Inimigo perigoso '{nome_inimigo}' está próximo! Fugindo agora..."
            )
            
            self.fugir_de_inimigo_perigoso()
            return True
        
        return False
    
    def limpar_imagens_antigas(self):
        """Remove imagens antigas mantendo apenas as mais recentes até o limite"""
        try:
            pasta = self.config.pasta_imagens_treino
            if not os.path.exists(pasta):
                return
            
            # Lista todas as imagens PNG
            imagens = [f for f in os.listdir(pasta) if f.endswith('.png')]
            
            if len(imagens) <= self.config.max_imagens_treino:
                return  # Já está dentro do limite
            
            # Ordena por timestamp (extraído do nome do arquivo)
            # Formato: tipo_timestamp_dX.png
            imagens_com_tempo = []
            for img in imagens:
                try:
                    # Extrai timestamp do nome do arquivo
                    partes = img.split('_')
                    if len(partes) >= 2:
                        timestamp = int(partes[1])
                        caminho_completo = os.path.join(pasta, img)
                        imagens_com_tempo.append((timestamp, caminho_completo))
                except:
                    pass
            
            # Ordena do mais antigo para o mais recente
            imagens_com_tempo.sort(key=lambda x: x[0])
            
            # Calcula quantas devem ser deletadas
            qtd_deletar = len(imagens_com_tempo) - self.config.max_imagens_treino
            
            if qtd_deletar > 0:
                print(f"  🗑️  Removendo {qtd_deletar} imagens antigas...")
                
                # Remove as mais antigas
                for i in range(qtd_deletar):
                    try:
                        os.remove(imagens_com_tempo[i][1])
                    except:
                        pass
                
                print(f"  ✅ Mantidas {self.config.max_imagens_treino} imagens mais recentes")
        except Exception as e:
            print(f"  ⚠️  Erro ao limpar imagens: {e}")
    
    def salvar_imagem_treino(self, imagem, tipo, densidade):
        """Salva imagem para treinamento futuro"""
        try:
            # Limpa imagens antigas antes de salvar nova
            self.limpar_imagens_antigas()
            
            pasta = self.config.pasta_imagens_treino
            timestamp = int(time.time())
            nome = f"{tipo}_{timestamp}_d{int(densidade)}.png"
            caminho = os.path.join(pasta, nome)
            
            if isinstance(imagem, np.ndarray):
                # Converte numpy array para PIL Image
                Image.fromarray(imagem).save(caminho)
            else:
                # Já é PIL Image
                imagem.save(caminho)
            
            self.stats['imagens_salvas'] += 1
            
            if self.stats['imagens_salvas'] % 10 == 0:
                print(f"  💾 {self.stats['imagens_salvas']} imagens de treino salvas")
        except Exception as e:
            pass
    
    def detectar_exp_ganho(self, debug=False):
        """Detecta EXP ganho após combate"""
        if not self.config.usar_detector_exp:
            return None
        
        try:
            # Tenta detectar EXP por 2 segundos (texto aparece brevemente)
            exp = self.detector_exp.detectar_exp_com_timeout(
                self, 
                timeout=2.0, 
                intervalo=0.3,
                debug=debug
            )
            
            if exp:
                self.stats['exp_total_ganho'] += exp
                self.stats['exp_por_combate'].append(exp)
                self.stats['exp_atual_level'] += exp
                
                print(f"  💰 EXP Ganho: +{exp:,}")
                print(f"  📊 Total: {self.stats['exp_total_ganho']:,}")
                
                return exp
        except Exception as e:
            if debug:
                print(f"  ⚠️  Erro ao detectar EXP: {e}")
        
        return None
    
    def calcular_tempo_proximo_level(self):
        """Calcula tempo estimado para próximo level baseado em EXP real"""
        if len(self.stats['exp_por_combate']) < 3:
            return None
        
        # Média de EXP por combate (últimos 20)
        ultimos = self.stats['exp_por_combate'][-20:]
        media_exp = sum(ultimos) / len(ultimos)
        
        # EXP restante para completar o level
        exp_restante = self.config.exp_necessario_level - self.stats['exp_atual_level']
        
        if exp_restante <= 0:
            return {'completo': True}
        
        # Combates necessários
        combates_necessarios = exp_restante / media_exp
        
        # Tempo por combate (baseado no histórico)
        tempo_decorrido = time.time() - self.stats['tempo_inicio']
        if self.stats['combates'] > 0:
            tempo_por_combate = tempo_decorrido / self.stats['combates']
        else:
            tempo_por_combate = 60  # Estimativa: 1 min por combate
        
        # Tempo restante em segundos
        segundos_restantes = combates_necessarios * tempo_por_combate
        
        # Converte para formato legível
        dias = int(segundos_restantes // 86400)
        horas = int((segundos_restantes % 86400) // 3600)
        minutos = int((segundos_restantes % 3600) // 60)
        
        # Data estimada
        from datetime import timedelta
        data_estimada = datetime.now() + timedelta(seconds=segundos_restantes)
        
        return {
            'completo': False,
            'exp_restante': int(exp_restante),
            'media_exp_combate': int(media_exp),
            'combates_necessarios': int(combates_necessarios),
            'tempo_restante_segundos': int(segundos_restantes),
            'tempo_restante_formatado': f"{dias}d {horas}h {minutos}min" if dias > 0 else f"{horas}h {minutos}min",
            'data_estimada': data_estimada.strftime('%d/%m/%Y %H:%M'),
            'porcentagem_level': (self.stats['exp_atual_level'] / self.config.exp_necessario_level) * 100
        }
    
    def registrar_dados_ml(self, exp_ganho, tempo_gasto):
        """Registra dados no sistema ML avançado"""
        if not self.ml_avancado:
            return
        
        # Registra rota/posição
        self.ml_avancado.registrar_rota(
            self.pos_x, 
            self.pos_y, 
            exp_ganho, 
            tempo_gasto, 
            self.area_atual
        )
        
        self.exp_ganho_area += exp_ganho
    
    def registrar_skill_ml(self, skill_id, sucesso=True):
        """Registra uso de skill no ML"""
        if not self.ml_avancado:
            return
        
        # Estimativa de damage baseado na skill (ajustar conforme necessário)
        damage_map = {
            1: 150,  # Skill 1
            2: 200,  # Skill 2
            3: 180,  # Skill 3
            4: 250,  # Skill 4
        }
        
        # Cooldowns aproximados (segundos)
        cooldown_map = {
            1: 5,
            2: 8,
            3: 6,
            4: 12,
        }
        
        damage = damage_map.get(skill_id, 100)
        cooldown = cooldown_map.get(skill_id, 5)
        
        self.ml_avancado.registrar_skill(skill_id, damage, cooldown, sucesso)
    
    def obter_proxima_area_ml(self):
        """Obtém próxima melhor área usando ML avançado"""
        if not self.ml_avancado or not self.config.usar_rotas_otimizadas:
            return None
        
        recomendacao = self.ml_avancado.recomendar_proxima_posicao(
            self.pos_x, 
            self.pos_y, 
            self.config.raio_busca_area
        )
        
        if recomendacao:
            x, y, densidade = recomendacao
            print(f"  🎯 ML recomenda: ({x}, {y}) - Densidade: {densidade:.1f} exp/min")
            return (x, y, densidade)
        
        return None
    
    def obter_rotacao_skills_ml(self):
        """Obtém rotação de skills otimizada por ML"""
        if not self.ml_avancado or not self.config.usar_skills_otimizadas:
            return None
        
        rotacao = self.ml_avancado.recomendar_rotacao_skills(max_skills=4)
        
        if rotacao:
            return rotacao
        
        return None
    
    def detectar_vida_atual(self):
        """Detecta % de vida atual do player"""
        try:
            # Captura tela
            screenshot = self.adb.screenshot()
            if screenshot is None:
                return 100  # Assume vida cheia se não conseguir detectar
            
            # Converte PIL Image para NumPy array
            import cv2
            screenshot_np = np.array(screenshot)
            
            # Região da barra de vida (configurável)
            cfg = self.config.regiao_vida_bar
            vida_regiao = screenshot_np[cfg['y']:cfg['y']+cfg['height'], cfg['x']:cfg['x']+cfg['width']]
            
            # Detecta cor vermelha (barra de vida)
            hsv = cv2.cvtColor(vida_regiao, cv2.COLOR_RGB2HSV)
            
            # Máscara para vermelho
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = mask1 + mask2
            
            # Calcula % de pixels vermelhos (proporcional à vida)
            pixels_vermelhos = np.sum(mask > 0)
            pixels_totais = mask.shape[0] * mask.shape[1]
            
            if pixels_totais > 0:
                percentual_vida = int((pixels_vermelhos / pixels_totais) * 100)
                return max(0, min(100, percentual_vida))
            
            return 100
        except Exception as e:
            print(f"  ⚠️ Erro ao detectar vida: {e}")
            return 100
    
    def analisar_dificuldade_area(self, x, y, vida_perdida, morreu=False):
        """Analisa a dificuldade de uma área baseado em perda de vida"""
        if not self.config.monitorar_dificuldade:
            return
        
        # Arredonda coordenada para grid de 100x100
        grid_x = (x // 100) * 100
        grid_y = (y // 100) * 100
        coord = (grid_x, grid_y)
        
        # Inicializa dados da área
        if coord not in self.historico_dificuldade:
            self.historico_dificuldade[coord] = {
                'perdas_vida': [],
                'mortes': 0,
                'combates': 0,
                'nivel_estimado': None
            }
        
        area = self.historico_dificuldade[coord]
        area['perdas_vida'].append(vida_perdida)
        area['combates'] += 1
        
        if morreu:
            area['mortes'] += 1
            print(f"  ☠️ MORTE detectada em ({grid_x}, {grid_y})! Total: {area['mortes']}")
        
        # Analisa se área é muito forte
        if area['combates'] >= self.config.min_combates_analise:
            media_perda = sum(area['perdas_vida']) / len(area['perdas_vida'])
            
            # Critérios para área perigosa
            muito_forte = (
                media_perda > self.config.limite_perda_vida or
                area['mortes'] >= self.config.max_mortes_area
            )
            
            if muito_forte and coord not in self.areas_perigosas:
                self.areas_perigosas.add(coord)
                print(f"  🚨 ÁREA PERIGOSA detectada: ({grid_x}, {grid_y})")
                print(f"     Perda média de vida: {media_perda:.1f}% | Mortes: {area['mortes']}")
                print(f"     ⬇️ Recomendado: Voltar {self.config.recuar_niveis} níveis")
            elif not muito_forte and coord in self.areas_perigosas:
                # Remove da lista se ficou mais fácil (player evoluiu)
                self.areas_perigosas.discard(coord)
                print(f"  ✅ Área ({grid_x}, {grid_y}) agora é segura!")
    
    def obter_area_segura(self, x_atual, y_atual):
        """Retorna uma área segura próxima para farming"""
        if not self.config.monitorar_dificuldade:
            return None
        
        # Procura áreas conhecidas e seguras
        areas_seguras = []
        
        for coord, dados in self.historico_dificuldade.items():
            # Pula áreas perigosas
            if coord in self.areas_perigosas:
                continue
            
            # Precisa de dados suficientes
            if dados['combates'] < self.config.min_combates_analise:
                continue
            
            # Calcula média de perda de vida
            media_perda = sum(dados['perdas_vida']) / len(dados['perdas_vida'])
            
            # Área segura: baixa perda de vida, sem mortes
            if media_perda < 30 and dados['mortes'] == 0:
                distancia = ((coord[0] - x_atual)**2 + (coord[1] - y_atual)**2)**0.5
                areas_seguras.append({
                    'coord': coord,
                    'distancia': distancia,
                    'perda_media': media_perda,
                    'combates': dados['combates']
                })
        
        if not areas_seguras:
            return None
        
        # Ordena por: menor perda de vida, depois menor distância
        areas_seguras.sort(key=lambda a: (a['perda_media'], a['distancia']))
        
        melhor = areas_seguras[0]
        print(f"  🛡️ Área SEGURA encontrada: {melhor['coord']}")
        print(f"     Perda média: {melhor['perda_media']:.1f}% | Combates: {melhor['combates']}")
        
        return melhor['coord']
    
    def deve_evitar_area(self, x, y):
        """Verifica se deve evitar uma área"""
        if not self.config.monitorar_dificuldade:
            return False
        
        # Arredonda coordenada para grid
        grid_x = (x // 100) * 100
        grid_y = (y // 100) * 100
        coord = (grid_x, grid_y)
        
        return coord in self.areas_perigosas
    
    def treinar_modelos_ml(self):
        """Treina modelos ML periodicamente"""
        if not self.ml_avancado:
            return
        
        tempo_desde_ultimo = time.time() - self.ultimo_treino_ml
        
        if tempo_desde_ultimo >= self.config.treinar_modelos_intervalo:
            print("\n🤖 Treinando modelos ML...")
            self.ml_avancado.treinar_modelos()
            self.ml_avancado.salvar_dados()
            self.ultimo_treino_ml = time.time()
            
            # Mostra estatísticas
            stats_ml = self.ml_avancado.obter_estatisticas()
            print(f"  📊 Dados coletados:")
            print(f"    • {stats_ml['total_rotas']} rotas")
            print(f"    • {stats_ml['total_areas']} áreas mapeadas")
            print(f"    • {stats_ml['total_skills_treinadas']} skills analisadas")
            
            if stats_ml.get('top_3_areas'):
                print(f"  🏆 Top 3 áreas:")
                for i, area in enumerate(stats_ml['top_3_areas'], 1):
                    print(f"    {i}. ({area['x']}, {area['y']}) - {area['densidade']:.1f} exp/min")
            
            if stats_ml.get('melhor_horario'):
                hora = stats_ml['melhor_horario']['hora']
                exp_min = stats_ml['melhor_horario']['exp_min']
                print(f"  ⏰ Melhor horário: {hora}:00 ({exp_min:.1f} exp/min)")
    
    def exportar_metricas(self):
        """Exporta métricas atuais para arquivo JSON"""
        try:
            tempo_decorrido = time.time() - self.stats['tempo_inicio']
            horas, resto = divmod(tempo_decorrido, 3600)
            minutos, segundos = divmod(resto, 60)
            
            # Calcula XP/min e tempo estimado (método antigo OCR)
            previsao = self.calcular_previsao_100()
            xp_por_minuto = previsao['xp_por_min'] if previsao else 0.0
            
            if previsao and previsao['minutos_restantes'] > 0:
                horas_rest = int(previsao['minutos_restantes'] // 60)
                mins_rest = int(previsao['minutos_restantes'] % 60)
                tempo_estimado = f"{horas_rest}h {mins_rest}min"
            else:
                tempo_estimado = "N/A"
            
            # Calcula tempo para próximo level (método novo com EXP real)
            previsao_level = self.calcular_tempo_proximo_level()
            if previsao_level and not previsao_level.get('completo'):
                tempo_proximo_level = previsao_level['tempo_restante_formatado']
                data_proximo_level = previsao_level['data_estimada']
                porcentagem_level = previsao_level['porcentagem_level']
                media_exp = previsao_level['media_exp_combate']
            else:
                tempo_proximo_level = "N/A"
                data_proximo_level = "N/A"
                porcentagem_level = 0.0
                media_exp = 0
            
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'tempo_decorrido': f"{int(horas):02d}:{int(minutos):02d}:{int(segundos):02d}",
                'tempo_decorrido_segundos': int(tempo_decorrido),
                'xp_porcentagem': self.stats.get('xp_atual', 0.0),
                'xp_por_minuto': xp_por_minuto,
                'tempo_estimado_lvl_100': tempo_estimado,
                'combates_vencidos': self.stats['combates'],
                'mortes': self.stats['mortes'],
                'skills_usadas': self.stats['skills_usadas'],
                'potions_usadas': self.stats['potions_usadas'],
                'loots_coletados': self.stats['loots_coletados'],
                'imagens_salvas': self.stats['imagens_salvas'],
                'observacoes_ml': [
                    {'x': self.X_train[i][0], 'y': self.X_train[i][1], 'densidade': self.y_train[i]}
                    for i in range(max(0, len(self.X_train) - 50), len(self.X_train))  # Últimas 50 observações
                ],
                'modelo_ml_treinado': self.modelo_treinado,
                'modo_turbo': self.config.modo_turbo if hasattr(self.config, 'modo_turbo') else False,
                
                # Métricas de EXP real
                'exp_total_ganho': self.stats['exp_total_ganho'],
                'exp_atual_level': self.stats['exp_atual_level'],
                'exp_necessario_level': self.config.exp_necessario_level,
                'media_exp_por_combate': media_exp,
                'porcentagem_level_atual': porcentagem_level,
                'tempo_proximo_level': tempo_proximo_level,
                'data_proximo_level': data_proximo_level,
            }
            
            with open(self.config.arquivo_metricas, 'w') as f:
                json.dump(metricas, f, indent=2)
        
        except Exception as e:
            print(f"  ⚠️  Erro ao exportar métricas: {e}")
    
    def atualizar_xp(self):
        """Atualiza tracking de XP e adiciona ao histórico"""
        if not self.config.usar_ocr_xp:
            return
        
        xp = self.ler_xp_atual()
        if xp is not None:
            self.stats['xp_atual'] = xp
            self.stats['historico_xp'].append((time.time(), xp))
            
            # Mantém apenas últimas 100 leituras
            if len(self.stats['historico_xp']) > 100:
                self.stats['historico_xp'] = self.stats['historico_xp'][-100:]
    
    def calcular_previsao_100(self):
        """Calcula previsão de tempo para atingir 100% de XP"""
        hist = self.stats['historico_xp']
        
        if len(hist) < 2:
            return None
        
        # Pega primeira e última leitura
        tempo_inicial, xp_inicial = hist[0]
        tempo_atual, xp_atual = hist[-1]
        
        tempo_decorrido = (tempo_atual - tempo_inicial) / 60.0  # minutos
        xp_ganho = xp_atual - xp_inicial
        
        if tempo_decorrido <= 0 or xp_ganho <= 0:
            return None
        
        # Taxa de XP por minuto
        xp_por_min = xp_ganho / tempo_decorrido
        
        # XP restante
        xp_restante = 100.0 - xp_atual
        
        if xp_por_min <= 0:
            return None
        
        # Tempo estimado em minutos
        minutos_restantes = xp_restante / xp_por_min
        
        return {
            'xp_por_min': xp_por_min,
            'minutos_restantes': minutos_restantes,
            'xp_restante': xp_restante
        }
    
    def verificar_morte(self):
        """Verifica se morreu"""
        if not self.config.verificar_morte:
            return False
        
        screenshot = self.adb.screenshot()
        if not screenshot:
            return False
        
        try:
            img_array = np.array(screenshot)
            vermelho_baixo = np.array([170, 0, 0])
            vermelho_alto = np.array([255, 60, 60])
            
            mask = np.all((img_array >= vermelho_baixo) & (img_array <= vermelho_alto), axis=2)
            proporcao = np.sum(mask) / (img_array.shape[0] * img_array.shape[1])
            
            if proporcao > 0.3:
                print("  💀 MORTE!")
                self.stats['mortes'] += 1
                # Tap no centro para respawn
                time.sleep(2)
                self.adb.tap(self.config.screen_width // 2, self.config.screen_height // 2)
                time.sleep(3)
                return True
        except:
            pass
        
        return False
    
    def resetar_camera(self):
        """Reseta a câmera para trás do personagem"""
        if not self.config.auto_reset_camera:
            return
        
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_reset_camera >= self.config.intervalo_reset_camera:
            pos = self.config.posicao_botao_camera
            self.adb.tap(pos['x'], pos['y'])
            print("  📷 Reset câmera")
            self.ultimo_reset_camera = tempo_atual
    
    def anti_afk(self):
        """Anti-AFK com movimento variável"""
        if not self.config.anti_afk:
            return
        
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_anti_afk >= self.config.intervalo_anti_afk:
            # Movimento aleatório pequeno com intensidade reduzida
            angulo = np.random.uniform(0, 2 * np.pi)
            intensidade = np.random.uniform(0.3, 0.6)  # Movimento curto
            self.mover_joystick(angulo, duracao_ms=300, intensidade=intensidade)
            self.ultimo_anti_afk = tempo_atual
    
    def rotacionar_area(self):
        """Rotação de áreas"""
        if not self.config.rotacao_areas:
            return
        
        tempo_atual = time.time()
        if tempo_atual - self.tempo_entrada_area >= self.config.tempo_max_area:
            self.area_atual = (self.area_atual + 1) % len(self.config.areas_conhecidas)
            area = self.config.areas_conhecidas[self.area_atual]
            
            print(f"\n🔄 Indo para {area['nome']}")
            
            self.pos_x = area['x']
            self.pos_y = area['y']
            self.tempo_entrada_area = tempo_atual
            self.stats['areas_visitadas'] += 1
    
    def prever_melhor_direcao(self):
        """Prevê melhor direção com ML"""
        melhor_densidade = -1
        melhor_angulo = 0
        
        for angulo in np.linspace(0, 2*np.pi, 16, endpoint=False):
            futuro_x = np.clip(self.pos_x + 5 * np.cos(angulo), 0, 100)
            futuro_y = np.clip(self.pos_y + 5 * np.sin(angulo), 0, 100)
            
            hora = datetime.now().hour
            features = np.array([[futuro_x, futuro_y, hora, self.area_atual]])
            features_scaled = self.scaler.transform(features)
            densidade = self.modelo.predict(features_scaled)[0]
            
            if densidade > melhor_densidade:
                melhor_densidade = densidade
                melhor_angulo = angulo
        
        return melhor_angulo, melhor_densidade
    
    def explorar_inteligente(self):
        """Exploração inteligente"""
        if len(self.y_train) >= 5:
            ultimas = self.y_train[-5:]
            if sum(ultimas) == 0:
                return np.random.uniform(0, 2 * np.pi)
            else:
                boas = []
                for i in range(max(0, len(self.X_train) - 10), len(self.X_train)):
                    if self.y_train[i] > 0:
                        boas.append(self.X_train[i])
                
                if boas:
                    media_x = np.mean([p[0] for p in boas])
                    media_y = np.mean([p[1] for p in boas])
                    dx = media_x - self.pos_x
                    dy = media_y - self.pos_y
                    angulo_base = np.arctan2(dy, dx)
                    variacao = np.random.uniform(-np.pi/4, np.pi/4)
                    return angulo_base + variacao
        
        return np.random.uniform(0, 2 * np.pi)
    
    def adicionar_observacao(self, x, y, densidade):
        """Adiciona observação ao ML"""
        hora = datetime.now().hour
        features = [x, y, hora, self.area_atual]
        self.X_train.append(features)
        self.y_train.append(densidade)
    
    def treinar_modelo(self):
        """Treina modelo ML"""
        if len(self.X_train) < 10:
            return False
        
        try:
            X = np.array(self.X_train)
            y = np.array(self.y_train)
            
            X_scaled = self.scaler.fit_transform(X)
            self.modelo.fit(X_scaled, y)
            self.modelo_treinado = True
            
            y_pred = self.modelo.predict(X_scaled)
            acertos = np.sum((y > 0.5) == (y_pred > 0.5))
            taxa = acertos / len(y) * 100
            
            print(f"  🧠 Modelo: {taxa:.1f}% acerto | {np.sum(y > 0.5)} áreas boas")
            return True
        except:
            return False
    
    def salvar_modelo(self):
        """Salva modelo"""
        dados = {
            'X_train': self.X_train,
            'y_train': self.y_train,
            'modelo': self.modelo if self.modelo_treinado else None,
            'scaler': self.scaler,
            'modelo_treinado': self.modelo_treinado
        }
        with open(ARQUIVO_MODELO, 'wb') as f:
            pickle.dump(dados, f)
    
    def carregar_modelo(self):
        """Carrega modelo"""
        if os.path.exists(ARQUIVO_MODELO):
            try:
                with open(ARQUIVO_MODELO, 'rb') as f:
                    dados = pickle.load(f)
                self.X_train = dados['X_train']
                self.y_train = dados['y_train']
                self.modelo = dados['modelo']
                self.scaler = dados['scaler']
                self.modelo_treinado = dados['modelo_treinado']
                print(f"✓ Modelo carregado ({len(self.X_train)} amostras)")
            except:
                pass
    
    def ciclo_farming(self):
        """Ciclo completo de farming"""
        
        # Salva métricas periodicamente
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_salvamento_metricas >= self.config.intervalo_salvar_metricas:
            self.exportar_metricas()
            self.ultimo_salvamento_metricas = tempo_atual
        
        # Treina modelos ML periodicamente
        self.treinar_modelos_ml()
        
        # Verifica morte
        if self.verificar_morte():
            return
        
        # Potion
        self.usar_potion()
        
        # Anti-AFK
        self.anti_afk()
        
        # Rotação
        self.rotacionar_area()
        
        # Decide direção: PRIORIDADE 0 - Área Segura, 1 - ML Avançado, 2 - Minimapa, 3 - ML Básico
        intensidade_movimento = 1.0  # Padrão: movimento completo
        movimento_continuo = False  # Se deve mover até chegar ao destino
        
        # PRIORIDADE 0: Verificar se precisa voltar para área segura
        area_recomendada = None
        if self.config.monitorar_dificuldade:
            # Usa posição atual já rastreada
            if self.deve_evitar_area(self.pos_x, self.pos_y):
                # Está em área perigosa! Busca área segura
                area_segura = self.obter_area_segura(self.pos_x, self.pos_y)
                if area_segura:
                    x_dest, y_dest = area_segura
                    dx = x_dest - self.pos_x
                    dy = y_dest - self.pos_y
                    melhor_angulo = np.arctan2(dy, dx)
                    movimento_continuo = True
                    intensidade_movimento = 1.0
                    area_recomendada = (x_dest, y_dest, 0)  # Marca como recomendada
                    print(f"\n🛡️ RECUANDO para área segura: ({x_dest}, {y_dest})")
        
        # PRIORIDADE 1: ML Avançado (se disponível e treinado)
        if not area_recomendada and self.ml_avancado and self.ml_avancado.modelos_treinados:
            area_recomendada = self.obter_proxima_area_ml()
            if area_recomendada:
                x_dest, y_dest, densidade = area_recomendada
                
                # Verifica se área recomendada não é perigosa
                if self.config.monitorar_dificuldade and self.deve_evitar_area(x_dest, y_dest):
                    print(f"  🚫 ML recomendou área perigosa ({x_dest}, {y_dest}), buscando alternativa...")
                    area_recomendada = None  # Cancela recomendação
                else:
                    # Calcula ângulo para a área recomendada
                    dx = x_dest - self.pos_x
                    dy = y_dest - self.pos_y
                    melhor_angulo = np.arctan2(dy, dx)
                    movimento_continuo = True
                    intensidade_movimento = 1.0
                    print(f"\n🤖 ML Avançado: Indo para ({x_dest}, {y_dest}) - {densidade:.1f} exp/min")
        
        # VERIFICAÇÃO DE INIMIGO PERIGOSO (prioridade máxima!)
        if self.verificar_inimigo_perigoso():
            # Se detectou e fugiu, pula resto do ciclo
            return
        
        # PRIORIDADE 2: Minimapa (se ML não deu recomendação)
        if not area_recomendada and self.config.usar_minimapa:
            info_minimapa = self.analisar_minimapa()
            if info_minimapa:
                melhor_angulo = info_minimapa['angulo']
                # Se detectou inimigos, movimento contínuo até chegar lá
                movimento_continuo = True
                intensidade_movimento = 1.0  # Força total
                print(f"\n🗺️  Minimapa: {info_minimapa['direcao']} ({info_minimapa['inimigos']} inimigos)")
                print(f"  🎯 Indo DIRETO para área com inimigos!")
            else:
                # Fallback para ML ou exploração
                if self.modelo_treinado and len(self.X_train) >= 15:
                    melhor_angulo, densidade = self.prever_melhor_direcao()
                    # Intensidade baseada na densidade prevista
                    intensidade_movimento = np.clip(densidade, 0.4, 1.0)
                    print(f"\n➡️  ML: {np.degrees(melhor_angulo):.0f}° (densidade: {densidade:.2%})")
                else:
                    melhor_angulo = self.explorar_inteligente()
                    # Exploração com intensidade reduzida (mais cauteloso)
                    intensidade_movimento = 0.6
                    print(f"\n🔍 Explorando: {np.degrees(melhor_angulo):.0f}°")
        else:
            # Usa ML/exploração se minimapa desabilitado
            if self.modelo_treinado and len(self.X_train) >= 15:
                melhor_angulo, densidade = self.prever_melhor_direcao()
                intensidade_movimento = np.clip(densidade, 0.4, 1.0)
                print(f"\n➡️  ML: {np.degrees(melhor_angulo):.0f}° (densidade: {densidade:.2%})")
            else:
                melhor_angulo = self.explorar_inteligente()
                intensidade_movimento = 0.6
                print(f"\n🔍 Explorando: {np.degrees(melhor_angulo):.0f}°")
        
        # IMPORTANTE: Reset câmera ANTES de mover
        print("  📷 Resetando câmera antes do movimento...")
        self.resetar_camera()
        time.sleep(0.3)  # Aguarda câmera ajustar
        
        # Move com intensidade variável (contínuo se minimapa detectou inimigos)
        self.mover_joystick(melhor_angulo, intensidade=intensidade_movimento, continuo=movimento_continuo)
        
        # Reduz delay em modo turbo
        delay_acao = self.config.intervalo_entre_acoes / 1000.0
        if self.config.modo_turbo:
            delay_acao *= 0.5  # 50% mais rápido
        time.sleep(delay_acao)
        
        # Skills
        self.usar_skills_rotacao()
        
        # Verifica combate (delay reduzido em modo turbo)
        delay_deteccao = 0.5 if self.config.modo_turbo else 1.0
        time.sleep(delay_deteccao)
        
        # Threshold mais sensível em modo de priorização de combate
        threshold_combate = 0.08 if self.config.priorizar_combate else 0.12
        em_combate = self.detectar_combate(threshold=threshold_combate)
        
        if em_combate:
            print("  ⚔️  COMBATE!")
            self.stats['combates'] += 1
            self.stats['xp_estimado'] += 100
            
            # Detecta vida ANTES do combate
            if self.config.monitorar_dificuldade:
                self.vida_antes_combate = self.detectar_vida_atual()
                print(f"  ❤️ Vida antes: {self.vida_antes_combate}%")
            
            # Marca início do combate para calcular tempo
            tempo_inicio_combate = time.time()
            
            # Salva screenshot de combate para treinamento
            if self.config.salvar_imagens_treino and self.ultima_screenshot:
                self.salvar_imagem_treino(self.ultima_screenshot, 'combate', 1.5)
            
            # VERIFICA SE ESTÁ ATACANDO POUCOS INIMIGOS
            # Se sim, procura área melhor no minimapa
            if self.config.usar_minimapa:
                info_minimapa_combate = self.analisar_minimapa()
                if info_minimapa_combate and info_minimapa_combate['total_inimigos'] > 20:
                    # Calcula concentração de inimigos
                    concentracao = info_minimapa_combate['inimigos'] / info_minimapa_combate['total_inimigos']
                    
                    # Se menos de 30% dos inimigos estão no setor atual = distribuídos
                    if concentracao < 0.3:
                        print(f"  ⚠️  Poucos inimigos aqui! ({info_minimapa_combate['inimigos']}/{info_minimapa_combate['total_inimigos']})")
                        print(f"  🎯 Indo para área com MAIS inimigos...")
                        
                        # Reseta câmera e vai para área melhor
                        self.resetar_camera()
                        time.sleep(0.3)
                        
                        # Move para área com mais densidade
                        self.mover_joystick(
                            info_minimapa_combate['angulo'], 
                            intensidade=1.0, 
                            continuo=True
                        )
                        time.sleep(2)
            
            # Combate otimizado
            delay_combate = 0.5 if self.config.modo_turbo else 1.0
            
            # Registra skills usadas no combo para ML
            skills_combo = []
            
            for _ in range(3):
                self.usar_skills_rotacao()
                if self.skills_ultima_rotacao:
                    skills_combo.extend(self.skills_ultima_rotacao)
                time.sleep(delay_combate)
                self.usar_potion()
            
            # Detecta EXP ganho
            exp_ganho = self.detectar_exp_ganho(debug=False)
            
            # Análise de dificuldade APÓS combate
            if self.config.monitorar_dificuldade:
                vida_depois = self.detectar_vida_atual()
                vida_perdida = self.vida_antes_combate - vida_depois
                
                print(f"  ❤️ Vida após: {vida_depois}%")
                print(f"  💔 Vida perdida: {vida_perdida}%")
                
                # Verifica se morreu (vida muito baixa)
                morreu = vida_depois < 10
                
                # Analisa dificuldade da área usando posição atual
                self.analisar_dificuldade_area(self.pos_x, self.pos_y, vida_perdida, morreu)
                
                # Se perdeu muita vida, alerta
                if vida_perdida > self.config.limite_perda_vida:
                    print(f"  ⚠️ COMBATE DIFÍCIL! Perdeu {vida_perdida}% de vida")
                    print(f"  💡 Considere voltar para áreas mais fracas")
            
            # Registra dados no ML Avançado
            if exp_ganho and self.ml_avancado:
                tempo_combate = time.time() - tempo_inicio_combate
                self.registrar_dados_ml(exp_ganho, tempo_combate)
                
                # Registra combo se usou skills otimizadas
                if skills_combo:
                    self.ml_avancado.registrar_combo(skills_combo, tempo_combate, exp_ganho)
            
            self.coletar_loot()
            self.adicionar_observacao(self.pos_x, self.pos_y, 1.5)
            
            # Delay reduzido após combate
            delay_pos_combate = 1.0 if self.config.modo_turbo else 2.0
            time.sleep(delay_pos_combate)
        else:
            print("  👁️  Vazio")
            
            # Skip rápido de áreas vazias
            if self.config.skip_areas_vazias:
                print("  ⏩ Pulando área vazia...")
                # Não adiciona observação negativa em modo skip
            else:
                # Salva screenshot de área vazia para treinamento
                if self.config.salvar_imagens_treino and self.ultima_screenshot:
                    if np.random.random() < 0.1:  # Salva 10% das áreas vazias
                        self.salvar_imagem_treino(self.ultima_screenshot, 'vazio', 0.0)
                
                self.adicionar_observacao(self.pos_x, self.pos_y, 0.0)
        
        time.sleep(self.config.intervalo_entre_acoes / 1000.0)
    
    def executar(self, ciclos=None):
        """Executa o bot"""
        print("\n" + "="*60)
        print("🚀 BOT ULTRA ADB - SILKROAD ORIGIN")
        print("="*60)
        print(f"\n📱 Dispositivo: {self.config.adb_device}")
        print(f"📐 Resolução: {self.config.screen_width}x{self.config.screen_height}")
        print(f"\n⚡ Funcionalidades:")
        print(f"  ✅ Auto-Skills")
        print(f"  ✅ Auto-Loot")
        print(f"  ✅ Auto-Potion")
        print(f"  ✅ Reset Câmera")
        print(f"  ✅ Rotação de Áreas")
        print(f"  ✅ Anti-AFK")
        print(f"  ✅ ML Guidance (Scikit-learn)")
        print(f"  ✅ Análise de Minimapa (OpenCV)")
        
        if self.config.salvar_imagens_treino:
            print(f"\n💾 Treinamento:")
            print(f"  📁 Salvando imagens em: {self.config.pasta_imagens_treino}/")
            print(f"  🎯 Limite: {self.config.max_imagens_treino} imagens")
        
        print("\nIniciando em 3 segundos...")
        time.sleep(3)
        
        contador = 0
        
        try:
            while True:
                contador += 1
                print(f"\n{'='*60}")
                print(f"📍 Ciclo #{contador} - Pos: ({self.pos_x:.0f},{self.pos_y:.0f})")
                print(f"{'='*60}")
                
                self.ciclo_farming()
                
                # Atualiza XP a cada 3 ciclos
                if contador % 3 == 0:
                    self.atualizar_xp()
                
                # Treina e mostra stats a cada 10 ciclos
                if contador % 10 == 0:
                    self.treinar_modelo()
                    self.salvar_modelo()
                    self.mostrar_stats()
                
                if ciclos and contador >= ciclos:
                    break
                
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n\n⏹ Interrompido")
        
        finally:
            self.treinar_modelo()
            self.salvar_modelo()
            self.mostrar_stats()
    
    def mostrar_stats(self):
        """Mostra estatísticas"""
        tempo = (time.time() - self.stats['tempo_inicio']) / 60
        
        print(f"\n📊 ESTATÍSTICAS ({tempo:.1f} min):")
        print(f"  ⚔️  Combates: {self.stats['combates']}")
        print(f"  💀 Mortes: {self.stats['mortes']}")
        print(f"  🧪 Potions: {self.stats['potions_usadas']}")
        print(f"  💥 Skills: {self.stats['skills_usadas']}")
        print(f"  💰 Loots: {self.stats['loots_coletados']}")
        print(f"  🗺️  Áreas: {self.stats['areas_visitadas']}")
        
        # Mostra XP atual e previsão
        if self.config.usar_ocr_xp and self.stats['xp_atual'] > 0:
            xp_atual = self.stats['xp_atual']
            xp_inicial = self.stats['xp_inicial']
            ganho = xp_atual - xp_inicial
            
            print(f"\n  📊 XP ATUAL: {xp_atual:.2f}%")
            print(f"  📈 Ganho: +{ganho:.2f}% (desde início)")
            
            previsao = self.calcular_previsao_100()
            if previsao:
                xp_min = previsao['xp_por_min']
                min_rest = previsao['minutos_restantes']
                
                horas = int(min_rest // 60)
                mins = int(min_rest % 60)
                
                print(f"  ⚡ Taxa: {xp_min:.3f}% XP/min")
                print(f"  🎯 Para 100%: {horas}h {mins}min")
                
                # Estima horário de chegada
                import datetime
                agora = datetime.datetime.now()
                chegada = agora + datetime.timedelta(minutes=min_rest)
                print(f"  🕒 Previsão: {chegada.strftime('%H:%M')}")
        else:
            print(f"  📈 XP estimado: {self.stats['xp_estimado']:,}")
            if tempo > 0:
                xp_hora = self.stats['xp_estimado'] / tempo * 60
                print(f"  ⚡ XP/hora: {xp_hora:,.0f}")
        
        # Mostra estatísticas de treinamento
        if self.config.salvar_imagens_treino:
            print(f"\n  💾 Imagens de Treino: {self.stats['imagens_salvas']}/{self.config.max_imagens_treino}")
        
        # Mostra estatísticas de EXP real
        if self.config.usar_detector_exp and self.stats['exp_total_ganho'] > 0:
            print(f"\n  💰 EXP REAL GANHO:")
            print(f"    Total: {self.stats['exp_total_ganho']:,} EXP")
            print(f"    Level Atual: {self.stats['exp_atual_level']:,} / {self.config.exp_necessario_level:,}")
            
            previsao_level = self.calcular_tempo_proximo_level()
            if previsao_level and not previsao_level.get('completo'):
                print(f"    Progresso: {previsao_level['porcentagem_level']:.1f}%")
                print(f"    Média/Combate: {previsao_level['media_exp_combate']:,} EXP")
                print(f"    Faltam: {previsao_level['combates_necessarios']:,} combates")
                print(f"    ⏱️  Tempo Estimado: {previsao_level['tempo_restante_formatado']}")
                print(f"    📅 Data Prevista: {previsao_level['data_estimada']}")

def menu():
    """Menu principal"""
    print("\n" + "="*60)
    print("   🚀 BOT ULTRA ADB - SILKROAD ORIGIN")
    print("="*60)
    print("\nOpções:")
    print("  1. Iniciar farming (infinito)")
    print("  2. Treinar por N ciclos")
    print("  3. Calibrar joystick/skills (manual)")
    print("  4. Ver estatísticas")
    print("  5. Sair")
    print()
    
    escolha = input("Escolha: ").strip()
    
    if escolha == '1':
        bot = BotUltraADB()
        bot.executar()
        menu()
    
    elif escolha == '2':
        ciclos = int(input("\nCiclos: ") or "50")
        bot = BotUltraADB()
        bot.executar(ciclos=ciclos)
        menu()
    
    elif escolha == '3':
        print("\n📝 Para calibrar:")
        print("   1. Use o bot de teste de toque ADB")
        print("   2. Toque nas posições desejadas no dispositivo")
        print("   3. Edite config_farming_adb.json com as coordenadas")
        print("\nComando para testar toque:")
        print("   adb -s 192.168.240.112:5555 shell input tap X Y")
        input("\nPressione ENTER...")
        menu()
    
    elif escolha == '4':
        if os.path.exists(ARQUIVO_MODELO):
            bot = BotUltraADB()
            bot.mostrar_stats()
        else:
            print("\n❌ Nenhuma estatística ainda!")
        input("\nPressione ENTER...")
        menu()
    
    elif escolha == '5':
        print("\nAté logo!")
        return
    
    else:
        print("\n❌ Opção inválida!")
        menu()

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\nEncerrado.")
