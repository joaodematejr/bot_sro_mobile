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
        self.ultima_screenshot = None
        
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
        }
        
        self.carregar_modelo()
        
        # Captura XP inicial
        if self.config.usar_ocr_xp:
            xp = self.ler_xp_atual()
            if xp is not None:
                self.stats['xp_inicial'] = xp
                self.stats['xp_atual'] = xp
                self.stats['historico_xp'].append((time.time(), xp))
                print(f"✓ XP inicial: {xp:.2f}%")
    
    def mover_joystick(self, angulo, duracao_ms=None):
        """Move usando o joystick via press-and-drag (como no celular)"""
        if duracao_ms is None:
            duracao_ms = self.config.velocidade_movimento
        
        centro_x = self.config.joystick_centro_x
        centro_y = self.config.joystick_centro_y
        raio = self.config.joystick_raio
        
        # Ponto de destino
        dest_x = int(centro_x + raio * np.cos(angulo))
        dest_y = int(centro_y + raio * np.sin(angulo))
        
        print(f"  🕹️  Joystick: centro({centro_x},{centro_y}) raio={raio}")
        print(f"  📐 Ângulo: {np.degrees(angulo):.0f}° → destino({dest_x},{dest_y})")
        
        # Pressiona no centro, arrasta para direção e segura
        sucesso = self.adb.press_and_drag(centro_x, centro_y, dest_x, dest_y, duracao_ms)
        
        if sucesso:
            print(f"  ✅ Movimento executado!")
        else:
            print(f"  ❌ Movimento falhou!")
        
        # Atualiza posição virtual
        self.pos_x = np.clip(self.pos_x + 3 * np.cos(angulo), 0, 100)
        self.pos_y = np.clip(self.pos_y + 3 * np.sin(angulo), 0, 100)
    
    def usar_skill(self, index):
        """Usa skill via tap ADB"""
        if index < len(self.config.posicoes_skills):
            pos = self.config.posicoes_skills[index]
            self.adb.tap(pos['x'], pos['y'])
            self.stats['skills_usadas'] += 1
            print(f"  💥 Skill {index + 1}")
            time.sleep(0.3)
    
    def usar_skills_rotacao(self):
        """Usa skills em rotação"""
        if not self.config.usar_skills_automaticas:
            return
        
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_skill >= self.config.intervalo_skills / 1000.0:
            for i in range(len(self.config.posicoes_skills)):
                self.usar_skill(i)
            self.ultimo_skill = tempo_atual
    
    def coletar_loot(self):
        """Coleta loot"""
        if self.config.auto_loot:
            pos = self.config.posicao_botao_loot
            self.adb.tap(pos['x'], pos['y'])
            self.stats['loots_coletados'] += 1
            print("  💰 Loot")
    
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
            
            if melhor_setor[1]['count'] > 10:  # Threshold mínimo
                return {
                    'direcao': melhor_setor[0],
                    'angulo': melhor_setor[1]['angulo'],
                    'inimigos': melhor_setor[1]['count']
                }
            
            return None
            
        except Exception as e:
            return None
    
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
        """Anti-AFK"""
        if not self.config.anti_afk:
            return
        
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_anti_afk >= self.config.intervalo_anti_afk:
            # Movimento aleatório pequeno
            angulo = np.random.uniform(0, 2 * np.pi)
            self.mover_joystick(angulo, duracao_ms=300)
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
        # Verifica morte
        if self.verificar_morte():
            return
        
        # Potion
        self.usar_potion()
        
        # Reset câmera
        self.resetar_camera()
        
        # Anti-AFK
        self.anti_afk()
        
        # Rotação
        self.rotacionar_area()
        
        # Decide direção: PRIORIDADE 1 - Minimapa
        if self.config.usar_minimapa:
            info_minimapa = self.analisar_minimapa()
            if info_minimapa:
                melhor_angulo = info_minimapa['angulo']
                print(f"\n🗺️  Minimapa: {info_minimapa['direcao']} ({info_minimapa['inimigos']} inimigos)")
            else:
                # Fallback para ML ou exploração
                if self.modelo_treinado and len(self.X_train) >= 15:
                    melhor_angulo, densidade = self.prever_melhor_direcao()
                    print(f"\n➡️  ML: {np.degrees(melhor_angulo):.0f}° (densidade: {densidade:.2%})")
                else:
                    melhor_angulo = self.explorar_inteligente()
                    print(f"\n🔍 Explorando: {np.degrees(melhor_angulo):.0f}°")
        else:
            # Usa ML/exploração se minimapa desabilitado
            if self.modelo_treinado and len(self.X_train) >= 15:
                melhor_angulo, densidade = self.prever_melhor_direcao()
                print(f"\n➡️  ML: {np.degrees(melhor_angulo):.0f}° (densidade: {densidade:.2%})")
            else:
                melhor_angulo = self.explorar_inteligente()
                print(f"\n🔍 Explorando: {np.degrees(melhor_angulo):.0f}°")
        
        # Move
        self.mover_joystick(melhor_angulo)
        time.sleep(self.config.intervalo_entre_acoes / 1000.0)
        
        # Skills
        self.usar_skills_rotacao()
        
        # Verifica combate
        time.sleep(1)
        em_combate = self.detectar_combate(threshold=0.12)
        
        if em_combate:
            print("  ⚔️  COMBATE!")
            self.stats['combates'] += 1
            self.stats['xp_estimado'] += 100
            
            for _ in range(3):
                self.usar_skills_rotacao()
                time.sleep(1)
                self.usar_potion()
            
            self.coletar_loot()
            self.adicionar_observacao(self.pos_x, self.pos_y, 1.5)
            time.sleep(2)
        else:
            print("  👁️  Vazio")
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
        print(f"  ✅ ML Guidance")
        
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
