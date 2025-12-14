#!/usr/bin/env python3
"""
Bot Ultra ADB - Silkroad Origin Mobile
Sistema automatizado de farming com IA e controle via ADB
"""

import subprocess
import sys
import time
import argparse
import signal
import json
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path

# Módulos de IA
try:
    from ai_modules import (
        MinimapVision,
        MLPredictor,
        OCRReader,
        CombatDetector,
        IntelligentMovement,
        AdvancedVision
    )
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Módulos de IA não disponíveis: {e}")
    print("   Instale: pip install opencv-python scikit-learn pytesseract imagehash")
    AI_AVAILABLE = False

# Sistema de Analytics
try:
    from analytics import FarmingAnalytics
    from xp_detector import XPGainDetector
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Analytics não disponível: {e}")
    ANALYTICS_AVAILABLE = False

# Detector Visual Corrigido (minimapa)
try:
    from detector_corrigido import DetectorVisualCorrigido
    DETECTOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Detector visual não disponível: {e}")
    DETECTOR_AVAILABLE = False

ADB_DEVICE = "192.168.240.112:5555"

# Arquivo de configuração
CONFIG_FILE = "config_farming_adb.json"


def cleanup_folder_images(folder: str, max_keep: int = 10, pattern: str = "*.png"):
    """
    Limpa pasta mantendo apenas as N imagens mais recentes
    
    Args:
        folder: Caminho da pasta
        max_keep: Quantidade máxima de imagens a manter
        pattern: Padrão de arquivos (*.png, *.jpg, etc.)
    """
    try:
        folder_path = Path(folder)
        if not folder_path.exists():
            return
        
        # Lista todos os arquivos do padrão
        images = sorted(folder_path.glob(pattern), key=os.path.getmtime)
        
        # Remove imagens excedentes
        if len(images) > max_keep:
            to_remove = len(images) - max_keep
            for img in images[:to_remove]:
                img.unlink()
    except Exception as e:
        pass  # Silencioso para não poluir logs


class Config:
    """Gerenciador de configurações do bot"""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✓ Configurações carregadas de {self.config_file}")
                return config
            except Exception as e:
                print(f"⚠️ Erro ao carregar config: {e}. Usando padrões.")
                return self.get_default_config()
        else:
            print(f"⚠️ Arquivo {self.config_file} não encontrado. Criando padrão...")
            config = self.get_default_config()
            self.save_config(config)
            return config
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Salva configurações no arquivo JSON"""
        try:
            if config is None:
                config = self.config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✓ Configurações salvas em {self.config_file}")
            return True
        except Exception as e:
            print(f"✗ Erro ao salvar config: {e}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Retorna configurações padrão"""
        return {
            "adb_device": ADB_DEVICE,
            "screen_width": 1920,
            "screen_height": 993,
            "posicao_botao_camera": {
                "x": 67,
                "y": 144,
                "descricao": "Botão para resetar câmera (voltar para trás do personagem)"
            },
            "intervalo_reset_camera": 2,
            "posicao_botao_target": {
                "x": 1726,
                "y": 797,
                "descricao": "Botão para mirar/targetar inimigos próximos"
            },
            "intervalo_target": 5,
            "target_clicks_por_ciclo": 5,
            "target_pausa_entre_ciclos": 30,
            "posicao_botao_demon": {
                "x": 1830,
                "y": 552,
                "descricao": "Botão para ativar habilidade Demon"
            },
            "intervalo_demon": 900,
            "regiao_exp": {
                "x": 119,
                "y": 964,
                "width": 200,
                "height": 30,
                "descricao": "Região da barra de EXP para OCR"
            },
            "intervalo_captura_exp": 60,
            "pasta_imagens_treino": "treino_ml",
            "inimigos_para_fugir": ["Giant", "Boss", "Elite", "Champion"],
            "salvar_imagens_treino": True,
            "max_imagens_treino": 100
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Define valor de configuração"""
        self.config[key] = value
    
    def get_camera_position(self) -> tuple:
        """Retorna posição do botão de câmera"""
        pos = self.config.get("posicao_botao_camera", {"x": 67, "y": 144})
        return (pos["x"], pos["y"])
    
    def get_camera_interval(self) -> int:
        """Retorna intervalo de reset de câmera em segundos"""
        return self.config.get("intervalo_reset_camera", 2)
    
    def get_target_position(self) -> tuple:
        """Retorna posição do botão de target"""
        pos = self.config.get("posicao_botao_target", {"x": 1726, "y": 797})
        return (pos["x"], pos["y"])
    
    def get_target_interval(self) -> int:
        """Retorna intervalo de target em segundos"""
        return self.config.get("intervalo_target", 5)
    
    def get_target_clicks_per_cycle(self) -> int:
        """Retorna quantos cliques de target fazer por ciclo"""
        return self.config.get("target_clicks_por_ciclo", 5)
    
    def get_target_pause_between_cycles(self) -> int:
        """Retorna pausa entre ciclos de target em segundos"""
        return self.config.get("target_pausa_entre_ciclos", 30)
    
    def get_demon_position(self) -> tuple:
        """Retorna posição do botão de Demon"""
        pos = self.config.get("posicao_botao_demon", {"x": 1830, "y": 552})
        return (pos["x"], pos["y"])
    
    def get_demon_interval(self) -> int:
        """Retorna intervalo de ativação do Demon em segundos (15 min = 900s)"""
        return self.config.get("intervalo_demon", 900)
    
    def get_exp_region(self) -> Dict[str, int]:
        """Retorna região da barra de EXP"""
        return self.config.get("regiao_exp", {"x": 119, "y": 964, "width": 200, "height": 30})
    
    def get_exp_capture_interval(self) -> int:
        """Retorna intervalo de captura de EXP em segundos"""
        return self.config.get("intervalo_captura_exp", 60)
    
    def get_training_folder(self) -> str:
        """Retorna pasta para salvar imagens de treino"""
        return self.config.get("pasta_imagens_treino", "treino_ml")
    
    def should_save_training_images(self) -> bool:
        """Verifica se deve salvar imagens de treino"""
        return self.config.get("salvar_imagens_treino", True)
    
    def get_max_training_images(self) -> int:
        """Retorna número máximo de imagens de treino"""
        return self.config.get("max_imagens_treino", 100)
    
    def get_minimap_region(self) -> Dict[str, int]:
        """Retorna região do mini mapa"""
        return self.config.get("regiao_minimap", {"x": 231, "y": 255, "width": 200, "height": 200})
    
    def get_minimap_capture_interval(self) -> int:
        """Retorna intervalo de captura do minimap em segundos"""
        return self.config.get("intervalo_captura_minimap", 5)
    
    def should_detect_enemies(self) -> bool:
        """Verifica se deve detectar inimigos no minimap"""
        return self.config.get("detectar_inimigos_minimap", True)
    
    def should_detect_players(self) -> bool:
        """Verifica se deve detectar jogadores no minimap"""
        return self.config.get("detectar_jogadores_minimap", True)
    
    def should_detect_coordinates(self) -> bool:
        """Verifica se deve detectar coordenadas no minimap"""
        return self.config.get("detectar_coordenadas_minimap", True)
    
    def get_minimap_colors(self) -> Dict[str, Any]:
        """Retorna configurações de cores do minimap"""
        return self.config.get("cores_minimap", {})
    
    def get_exp_gain_region(self) -> Dict[str, int]:
        """Retorna região onde aparece EXP ganho ao matar inimigos"""
        return self.config.get("regiao_exp_ganho", {"x": 764, "y": 498, "width": 150, "height": 50})
    
    def get_exp_gain_capture_interval(self) -> int:
        """Retorna intervalo de captura de EXP ganho em segundos"""
        return self.config.get("intervalo_captura_exp_ganho", 3)
    
    def get_exp_gain_folder(self) -> str:
        """Retorna pasta para salvar imagens de EXP ganho"""
        return self.config.get("pasta_exp_ganho", "exp_ganho_treino")
    
    def get_max_exp_gain_images(self) -> int:
        """Retorna número máximo de imagens de EXP ganho"""
        return self.config.get("max_imagens_exp_ganho", 200)
    
    def is_ai_enabled(self) -> bool:
        """Verifica se IA está habilitada"""
        return self.config.get("ia_habilitada", True) and AI_AVAILABLE
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Retorna configurações de IA"""
        return self.config.get("ia_config", {})
    
    def should_use_minimap_vision(self) -> bool:
        """Verifica se deve usar análise de minimap com CV"""
        return self.get_ai_config().get("usar_minimap_vision", True)
    
    def should_use_ml_predictor(self) -> bool:
        """Verifica se deve usar ML para previsões"""
        return self.get_ai_config().get("usar_ml_predictor", True)
    
    def should_use_ocr(self) -> bool:
        """Verifica se deve usar OCR"""
        return self.get_ai_config().get("usar_ocr", True)
    
    def should_use_combat_detector(self) -> bool:
        """Verifica se deve detectar combate"""
        return self.get_ai_config().get("usar_combat_detector", True)
    
    def should_use_intelligent_movement(self) -> bool:
        """Verifica se deve usar movimento inteligente"""
        return self.get_ai_config().get("usar_movimento_inteligente", False)
    
    def should_use_advanced_vision(self) -> bool:
        """Verifica se deve usar detecção avançada"""
        return self.get_ai_config().get("usar_advanced_vision", True)
    
    def get_advanced_vision_config(self) -> Dict[str, Any]:
        """Retorna configurações do AdvancedVision"""
        return self.config.get("advanced_vision", {})
    
    def get_joystick_config(self) -> Dict[str, int]:
        """Retorna configurações do joystick"""
        return {
            'centro_x': self.config.get('joystick_centro_x', 150),
            'centro_y': self.config.get('joystick_centro_y', 850),
            'raio': self.config.get('joystick_raio', 80)
        }

class ADBConnection:
    """Gerenciador de conexão ADB"""
    
    def __init__(self, device_address: str = None):
        if device_address is None:
            device_address = ADB_DEVICE
        self.device_address = device_address
        # Extrai IP e porta do endereço
        if ":" in device_address:
            self.device_ip, port_str = device_address.split(":")
            self.port = int(port_str)
        else:
            self.device_ip = device_address
            self.port = 5555
    
    def check_adb_installed(self) -> bool:
        """Verifica se o ADB está instalado no sistema"""
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ ADB encontrado: {result.stdout.split()[4]}")
                return True
            return False
        except FileNotFoundError:
            print("✗ ADB não encontrado no sistema!")
            print("  Instale com: sudo apt install adb")
            return False
        except Exception as e:
            print(f"✗ Erro ao verificar ADB: {e}")
            return False
    
    def connect(self, timeout: int = 10) -> bool:
        """
        Conecta ao dispositivo via ADB TCP/IP
        
        Args:
            timeout: Tempo máximo de espera em segundos
            
        Returns:
            True se conectou com sucesso, False caso contrário
        """
        print(f"\n🔌 Conectando ao dispositivo {self.device_address}...")
        
        try:
            # Tenta conectar
            result = subprocess.run(
                ["adb", "connect", self.device_address],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout + result.stderr
            
            if "connected" in output.lower() or "already connected" in output.lower():
                print(f"✓ Conexão estabelecida com {self.device_address}")
                
                # Verifica se o dispositivo está realmente conectado
                time.sleep(1)
                if self.verify_connection():
                    return True
                else:
                    print("✗ Falha na verificação da conexão")
                    return False
            else:
                print(f"✗ Falha na conexão: {output.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout ao tentar conectar (>{timeout}s)")
            return False
        except Exception as e:
            print(f"✗ Erro ao conectar: {e}")
            return False
    
    def verify_connection(self) -> bool:
        """Verifica se o dispositivo está conectado e respondendo"""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Pula o cabeçalho "List of devices attached"
                if self.device_address in line and "device" in line:
                    # Testa um comando simples
                    test = subprocess.run(
                        ["adb", "-s", self.device_address, "shell", "echo", "test"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if test.returncode == 0:
                        print(f"✓ Dispositivo {self.device_address} respondendo")
                        return True
            
            print(f"✗ Dispositivo {self.device_address} não encontrado ou não respondendo")
            return False
            
        except Exception as e:
            print(f"✗ Erro ao verificar conexão: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Desconecta do dispositivo"""
        try:
            print(f"\n🔌 Desconectando de {self.device_address}...")
            result = subprocess.run(
                ["adb", "disconnect", self.device_address],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"✓ Desconectado: {result.stdout.strip()}")
            return True
        except Exception as e:
            print(f"✗ Erro ao desconectar: {e}")
            return False
    
    def list_devices(self) -> None:
        """Lista todos os dispositivos conectados"""
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            print("\n📱 Dispositivos conectados:")
            print(result.stdout)
        except Exception as e:
            print(f"✗ Erro ao listar dispositivos: {e}")
    
    def get_device_info(self) -> None:
        """Obtém informações do dispositivo conectado"""
        if not self.verify_connection():
            print("✗ Dispositivo não conectado")
            return
        
        try:
            print(f"\n📱 Informações do dispositivo {self.device_address}:")
            
            # Modelo do dispositivo
            model = subprocess.run(
                ["adb", "-s", self.device_address, "shell", "getprop", "ro.product.model"],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"  Modelo: {model.stdout.strip()}")
            
            # Versão do Android
            version = subprocess.run(
                ["adb", "-s", self.device_address, "shell", "getprop", "ro.build.version.release"],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"  Android: {version.stdout.strip()}")
            
            # Resolução da tela
            size = subprocess.run(
                ["adb", "-s", self.device_address, "shell", "wm", "size"],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"  Tela: {size.stdout.strip()}")
            
        except Exception as e:
            print(f"✗ Erro ao obter informações: {e}")
    
    def screenshot(self, output_path: str) -> bool:
        """
        Captura screenshot do dispositivo
        Usa método shell + pull (mais compatível)
        
        Args:
            output_path: Caminho onde salvar a imagem
            
        Returns:
            True se capturou com sucesso
        """
        try:
            # Usa timestamp para arquivo temporário único
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:20]
            temp_path = f"/sdcard/screencap_{timestamp}.png"
            
            # Captura screenshot no dispositivo
            result = subprocess.run(
                ["adb", "-s", self.device_address, "shell", "screencap", "-p", temp_path],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return False
            
            # Puxa arquivo para PC
            result = subprocess.run(
                ["adb", "-s", self.device_address, "pull", temp_path, output_path],
                capture_output=True,
                timeout=10
            )
            
            # Remove arquivo temporário do dispositivo
            subprocess.run(
                ["adb", "-s", self.device_address, "shell", "rm", temp_path],
                capture_output=True,
                timeout=3
            )
            
            # Verifica se arquivo foi criado e é PNG válido
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                with open(output_path, 'rb') as f:
                    header = f.read(8)
                    if header == b'\x89PNG\r\n\x1a\n':
                        return True
                    else:
                        # Remove arquivo inválido
                        os.remove(output_path)
                        return False
            
            return False
            
        except Exception as e:
            print(f"✗ Erro ao capturar screenshot: {e}")
            return False
    
    def tap(self, x: int, y: int) -> bool:
        """
        Executa um toque na tela do dispositivo
        
        Args:
            x: Coordenada X do toque
            y: Coordenada Y do toque
            
        Returns:
            True se o comando foi executado com sucesso
        """
        try:
            subprocess.run(
                ["adb", "-s", self.device_address, "shell", "input", "tap", str(x), str(y)],
                capture_output=True,
                timeout=2
            )
            return True
        except Exception as e:
            print(f"✗ Erro ao executar tap: {e}")
            return False


class MinimapAnalyzer:
    """Analisador de mini mapa usando OpenCV"""
    
    def __init__(self, adb: ADBConnection, config: Config, detector_visual=None):
        self.adb = adb
        self.config = config
        self.detector_visual = detector_visual  # Detector corrigido
        self.minimap_folder = "minimap_captures"
        self.enemies_detected = []
        self.players_detected = []
        self.current_position = None
        self.current_coordinates = None
        
        # Cria pasta para capturas do minimap
        Path(self.minimap_folder).mkdir(exist_ok=True)
    
    def capture_and_analyze(self) -> Dict[str, Any]:
        """Captura e analisa o mini mapa"""
        try:
            # Captura screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.minimap_folder, f"minimap_{timestamp}.png")
            
            if not self.adb.screenshot(filepath):
                return None
            
            result = {
                "timestamp": timestamp,
                "filepath": filepath,
                "enemies_count": 0,
                "players_count": 0,
                "coordinates": None,
                "status": "captured"
            }
            
            # Analisa com detector visual se disponível
            if self.detector_visual:
                try:
                    detection = self.detector_visual.detectar_objetos_reais(
                        filepath, 
                        crop_minimap=True
                    )
                    
                    if detection:
                        resultados, debug_path = detection
                        
                        # Atualiza contagens
                        result["enemies_count"] = resultados.get('vermelho_mob', 0)
                        result["players_count"] = resultados.get('azul', 0)
                        result["player_marker"] = resultados.get('amarelo', 0)
                        result["party_members"] = resultados.get('verde', 0)
                        result["debug_path"] = str(debug_path)
                        result["status"] = "analyzed"
                        
                        # Armazena histórico
                        self.enemies_detected.append({
                            "timestamp": timestamp,
                            "count": result["enemies_count"]
                        })
                        
                        # Mantém apenas últimos 100 registros
                        if len(self.enemies_detected) > 100:
                            self.enemies_detected = self.enemies_detected[-100:]
                        
                except Exception as e:
                    print(f"⚠️ Erro ao analisar minimap: {e}")
                    result["status"] = "error"
            
            return result
            
        except Exception as e:
            print(f"✗ Erro ao analisar minimap: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do minimap"""
        return {
            "enemies_detected": len(self.enemies_detected),
            "players_detected": len(self.players_detected),
            "current_position": self.current_position,
            "current_coordinates": self.current_coordinates
        }


class ExpTracker:
    """Rastreador de EXP com captura de screenshots para treino ML"""
    
    def __init__(self, adb: ADBConnection, config: Config):
        self.adb = adb
        self.config = config
        self.training_folder = config.get_training_folder()
        self.max_images = config.get_max_training_images()
        self.exp_history = []
        
        # Cria pasta de treino se não existir
        if config.should_save_training_images():
            Path(self.training_folder).mkdir(exist_ok=True)
            print(f"📁 Pasta de treino: {self.training_folder}/")
    
    def capture_exp_screenshot(self) -> Optional[str]:
        """Captura screenshot da região de EXP"""
        if not self.config.should_save_training_images():
            return None
        
        try:
            # Limpa imagens antigas se necessário
            self._cleanup_old_images()
            
            # Gera nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exp_{timestamp}.png"
            filepath = os.path.join(self.training_folder, filename)
            
            # Captura screenshot completo
            if self.adb.screenshot(filepath):
                self.exp_history.append({
                    "timestamp": timestamp,
                    "filepath": filepath
                })
                return filepath
            return None
        except Exception as e:
            print(f"✗ Erro ao capturar EXP: {e}")
            return None
    
    def _cleanup_old_images(self):
        """Remove imagens antigas mantendo apenas as max_images mais recentes"""
        try:
            folder_path = Path(self.training_folder)
            images = sorted(folder_path.glob("exp_*.png"), key=os.path.getmtime)
            
            # Remove imagens excedentes
            if len(images) >= self.max_images:
                to_remove = len(images) - self.max_images + 1
                for img in images[:to_remove]:
                    img.unlink()
        except Exception as e:
            print(f"⚠️ Erro ao limpar imagens antigas: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do rastreamento"""
        return {
            "total_capturas": len(self.exp_history),
            "pasta": self.training_folder,
            "max_images": self.max_images
        }


class ExpGainTracker:
    """Rastreador de EXP ganho ao matar inimigos"""
    
    def __init__(self, adb: ADBConnection, config: Config):
        self.adb = adb
        self.config = config
        self.exp_gain_folder = config.get_exp_gain_folder()
        self.max_images = config.get_max_exp_gain_images()
        self.exp_gains = []
        
        # Cria pasta para EXP ganho
        Path(self.exp_gain_folder).mkdir(exist_ok=True)
        print(f"📁 Pasta EXP ganho: {self.exp_gain_folder}/")
    
    def capture_exp_gain(self) -> Optional[str]:
        """Captura screenshot da região de EXP ganho"""
        try:
            # Limpa imagens antigas se necessário
            self._cleanup_old_images()
            
            # Gera nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # milissegundos
            filename = f"exp_gain_{timestamp}.png"
            filepath = os.path.join(self.exp_gain_folder, filename)
            
            # Captura screenshot completo
            if self.adb.screenshot(filepath):
                self.exp_gains.append({
                    "timestamp": timestamp,
                    "filepath": filepath
                })
                return filepath
            return None
        except Exception as e:
            print(f"✗ Erro ao capturar EXP ganho: {e}")
            return None
    
    def _cleanup_old_images(self):
        """Remove imagens antigas mantendo apenas as max_images mais recentes"""
        try:
            folder_path = Path(self.exp_gain_folder)
            images = sorted(folder_path.glob("exp_gain_*.png"), key=os.path.getmtime)
            
            # Remove imagens excedentes
            if len(images) >= self.max_images:
                to_remove = len(images) - self.max_images + 1
                for img in images[:to_remove]:
                    img.unlink()
        except Exception as e:
            print(f"⚠️ Erro ao limpar imagens de EXP ganho: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do rastreamento de EXP ganho"""
        return {
            "total_capturas": len(self.exp_gains),
            "pasta": self.exp_gain_folder,
            "max_images": self.max_images
        }


def menu():
    """Menu principal"""
    print("\n" + "="*60)
    print("   🚀 BOT ULTRA ADB - SILKROAD ORIGIN")
    print("="*60)
    print("\nOpções:")
    print("  1. Iniciar farming (infinito)")
    print("  2. Treinar por N ciclos")
    print("  3. Configurações")
    print("  4. Ver estatísticas")
    print("  5. Relatório de Otimização ML")
    print("  6. Sair")
    print()
    escolha = input("Escolha uma opção: ")
    return escolha


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Bot Ultra ADB - Silkroad Origin Mobile",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py                            # Inicia o menu interativo
  python main.py connect                    # Conecta ao IP padrão (192.168.240.112:5555)
  python main.py connect -i 192.168.1.100   # Conecta a um IP específico
  python main.py connect -i 192.168.1.100 -p 5556  # IP e porta customizados
  python main.py disconnect                 # Desconecta do dispositivo
  python main.py list                       # Lista dispositivos conectados
  python main.py info                       # Mostra informações do dispositivo
        """
    )
    
    parser.add_argument(
        "command",
        nargs='?',
        choices=["connect", "disconnect", "list", "info", "menu"],
        help="Comando a executar (opcional, padrão: menu)"
    )
    
    parser.add_argument(
        "-i", "--ip",
        default="192.168.240.112",
        help="IP do dispositivo (padrão: 192.168.240.112)"
    )
    
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=5555,
        help="Porta ADB (padrão: 5555)"
    )
    
    args = parser.parse_args()
    
    # Se nenhum comando foi fornecido, inicia o menu
    if args.command is None or args.command == "menu":
        run_interactive_menu()
        return
    
    # Monta o endereço do dispositivo
    device_address = f"{args.ip}:{args.port}"
    
    # Inicializa conexão ADB
    adb = ADBConnection(device_address=device_address)
    
    # Verifica se ADB está instalado
    if not adb.check_adb_installed():
        sys.exit(1)
    
    # Executa comando
    if args.command == "connect":
        success = adb.connect()
        if success:
            adb.get_device_info()
            sys.exit(0)
        else:
            print("\n💡 Dicas:")
            print("  1. Verifique se o dispositivo está na mesma rede")
            print("  2. Ative 'Depuração USB' nas Opções do Desenvolvedor")
            print("  3. Ative 'Depuração via Wi-Fi' (se disponível)")
            print("  4. No dispositivo, execute: adb tcpip 5555")
            sys.exit(1)
    
    elif args.command == "disconnect":
        adb.disconnect()
        sys.exit(0)
    
    elif args.command == "list":
        adb.list_devices()
        sys.exit(0)
    
    elif args.command == "info":
        adb.get_device_info()
        sys.exit(0)


def run_interactive_menu():
    """Executa o menu interativo"""
    # Carrega configurações
    config = Config()
    
    adb = ADBConnection()
    
    # Verifica se ADB está instalado
    if not adb.check_adb_installed():
        sys.exit(1)
    
    # Verifica se está conectado
    if not adb.verify_connection():
        print("\n⚠️  Dispositivo não conectado!")
        resposta = input("Deseja conectar agora? (s/n): ").lower()
        if resposta == 's':
            if not adb.connect():
                print("\n❌ Falha ao conectar. Encerrando...")
                sys.exit(1)
        else:
            print("\n❌ É necessário conectar ao dispositivo para usar o bot.")
            sys.exit(1)
    
    while True:
        escolha = menu()
        
        if escolha == "1":
            start_infinite_farming(adb, config)
        
        elif escolha == "2":
            print("\n🎯 Treinar por N ciclos")
            try:
                ciclos = int(input("Quantos ciclos? "))
                start_farming_cycles(adb, config, ciclos)
            except ValueError:
                print("❌ Número inválido!")
                input("\nPressione ENTER para voltar ao menu...")
        
        elif escolha == "3":
            show_config_menu(config)
        
        elif escolha == "4":
            print("\n📊 Estatísticas")
            print("⚠️  Funcionalidade em desenvolvimento")
            input("\nPressione ENTER para voltar ao menu...")
        
        elif escolha == "5":
            print("\n🤖 Relatório de Otimização ML")
            print("⚠️  Funcionalidade em desenvolvimento")
            input("\nPressione ENTER para voltar ao menu...")
        
        elif escolha == "6":
            print("\n👋 Encerrando bot...")
            sys.exit(0)
        
        else:
            print("\n❌ Opção inválida!")
            input("\nPressione ENTER para continuar...")


def start_infinite_farming(adb: ADBConnection, config: Config):
    """Inicia o farming infinito - resetando câmera, targetando inimigos e ativando demon"""
    camera_x, camera_y = config.get_camera_position()
    camera_interval = config.get_camera_interval()
    target_x, target_y = config.get_target_position()
    target_interval = config.get_target_interval()
    target_clicks = config.get_target_clicks_per_cycle()
    target_pause = config.get_target_pause_between_cycles()
    demon_x, demon_y = config.get_demon_position()
    demon_interval = config.get_demon_interval()
    exp_capture_interval = config.get_exp_capture_interval()
    exp_region = config.get_exp_region()
    exp_gain_interval = config.get_exp_gain_capture_interval()
    exp_gain_region = config.get_exp_gain_region()
    
    # Inicializa rastreadores
    exp_tracker = ExpTracker(adb, config)
    exp_gain_tracker = ExpGainTracker(adb, config)
    
    # Inicializa Analytics
    analytics = None
    xp_detector = None
    if ANALYTICS_AVAILABLE:
        analytics = FarmingAnalytics()
        xp_detector = XPGainDetector()
        print("📊 Analytics habilitado")
    
    # Inicializa Detector Visual
    detector_visual = None
    if DETECTOR_AVAILABLE:
        detector_visual = DetectorVisualCorrigido()
        print("🔍 Detector Visual habilitado (minimapa)")
    
    # Inicializa módulos de IA
    ai_enabled = config.is_ai_enabled()
    minimap_vision = None
    ml_predictor = None
    ocr_reader = None
    combat_detector = None
    intelligent_movement = None
    advanced_vision = None
    
    if ai_enabled:
        print("\n🧠 Inicializando módulos de IA...")
        
        if config.should_use_minimap_vision():
            minimap_vision = MinimapVision(config.config)
            print("  ✓ MinimapVision (OpenCV)")
        
        if config.should_use_ml_predictor():
            ml_predictor = MLPredictor()
            print("  ✓ MLPredictor (RandomForest + KMeans)")
        
        if config.should_use_ocr():
            ocr_reader = OCRReader()
            print("  ✓ OCRReader (Tesseract)")
        
        if config.should_use_combat_detector():
            combat_detector = CombatDetector()
            print("  ✓ CombatDetector (ImageHash)")
        
        if config.should_use_intelligent_movement():
            intelligent_movement = IntelligentMovement(adb, config.config)
            print("  ✓ IntelligentMovement")
        
        if config.should_use_advanced_vision():
            advanced_vision = AdvancedVision(config.get_advanced_vision_config())
            print("  ✓ AdvancedVision (cv2.inRange + HoughCircles + OCR)")
    
    print("\n" + "="*60)
    print("   🚀 FARMING INFINITO INICIADO")
    print("="*60)
    print(f"\n🎥 Reset de câmera: ({camera_x}, {camera_y}) - a cada {camera_interval}s")
    print(f"🎯 Target em ciclos:")
    print(f"   • {target_clicks} cliques de {target_interval}s cada")
    print(f"   • Pausa de {target_pause}s entre ciclos")
    print(f"😈 Demon: ({demon_x}, {demon_y}) - a cada {demon_interval//60} minutos")
    print(f"📊 EXP Barra: Região ({exp_region['x']}, {exp_region['y']}) - captura a cada {exp_capture_interval}s")
    print(f"💰 EXP Ganho: Região ({exp_gain_region['x']}, {exp_gain_region['y']}) - captura a cada {exp_gain_interval}s")
    if config.should_save_training_images():
        print(f"📁 Screenshots EXP barra: {exp_tracker.training_folder}/")
        print(f"📁 Screenshots EXP ganho: {exp_gain_tracker.exp_gain_folder}/")
    print("⚠️  Pressione Ctrl+C para parar\n")
    
    contador_camera = 0
    contador_target = 0
    contador_demon = 0
    contador_exp_captures = 0
    contador_exp_gain_captures = 0
    contador_ia_analises = 0
    contador_movimentos_ia = 0
    ciclos_target = 0
    tempo_inicio = time.time()
    ultimo_camera = 0
    ultimo_demon = 0
    ultimo_exp_capture = 0
    ultimo_exp_gain_capture = 0
    ultimo_ia_analise = 0
    ultimo_movimento_ia = 0
    
    # Controle de ciclos de target
    em_ciclo_target = False
    clicks_no_ciclo = 0
    ultimo_target = 0
    fim_ultimo_ciclo = 0
    
    # Dados de IA
    best_farming_direction = None
    current_exp_percentage = None
    in_combat = False
    
    # Handler para Ctrl+C
    def signal_handler(sig, frame):
        tempo_total = time.time() - tempo_inicio
        minutos = int(tempo_total // 60)
        segundos = int(tempo_total % 60)
        
        # Salva analytics antes de exibir relatório
        if analytics:
            analytics.auto_save()
            metrics_file = analytics.export_metrics()
        
        print("\n\n" + "="*60)
        print("   ⏹️  FARMING INTERROMPIDO")
        print("="*60)
        print(f"\n📊 Estatísticas:")
        print(f"  🎥 Resets de câmera: {contador_camera}")
        print(f"  🎯 Targets totais: {contador_target}")
        print(f"  🔄 Ciclos de target: {ciclos_target}")
        print(f"  😈 Demon ativado: {contador_demon} vezes")
        print(f"  📸 Screenshots EXP barra: {contador_exp_captures}")
        print(f"  💰 Screenshots EXP ganho: {contador_exp_gain_captures}")
        
        # Estatísticas de Analytics
        if analytics:
            print(f"\n📈 Analytics:")
            stats = analytics.get_current_statistics()
            xp_stats = stats['xp']
            combat_stats = stats['combat']
            
            if xp_stats['initial'] is not None:
                print(f"  XP ganho: {xp_stats['gained']:.2f}%")
                print(f"  XP/min: {xp_stats['xp_per_minute']:.4f}%")
                print(f"  Tempo para level: {xp_stats['time_to_level']}")
            
            if combat_stats['kills'] > 0:
                print(f"  Kills: {combat_stats['kills']}")
                print(f"  Kills/min: {combat_stats['kills_per_minute']:.2f}")
                print(f"  XP médio/kill: {xp_stats['avg_xp_per_kill']:.4f}%")
            
            print(f"\n💾 Métricas exportadas: {metrics_file}")
        
        # Estatísticas de IA
        if ai_enabled:
            print(f"\n🧠 Estatísticas de IA:")
            print(f"  🔍 Análises de minimap: {contador_ia_analises}")
            print(f"  🚶 Movimentos inteligentes: {contador_movimentos_ia}")
            
            if minimap_vision:
                density_stats = minimap_vision.get_density_stats()
                if density_stats:
                    print(f"  👹 Inimigos detectados: {density_stats.get('total_enemies_seen', 0)}")
                    print(f"  📊 Média por scan: {density_stats.get('avg_enemies_per_scan', 0):.1f}")
            
            if combat_detector:
                combat_stats = combat_detector.get_combat_stats()
                if combat_stats:
                    print(f"  ⚔️  Combate detectado: {combat_stats.get('combat_percentage', 0):.1f}% do tempo")
            
            if ml_predictor and len(ml_predictor.training_data) > 0:
                print(f"  🎓 Amostras ML coletadas: {len(ml_predictor.training_data)}")
        
        if config.should_save_training_images():
            exp_stats = exp_tracker.get_stats()
            exp_gain_stats = exp_gain_tracker.get_stats()
            print(f"\n📁 Imagens de Treino:")
            print(f"  📁 EXP barra: {exp_stats['pasta']}/ ({exp_stats['total_capturas']} imagens)")

            print(f"  📁 EXP ganho: {exp_gain_stats['pasta']}/ ({exp_gain_stats['total_capturas']} imagens)")
        print(f"  ⏱️  Tempo total: {minutos}min {segundos}s")
        print()
        input("Pressione ENTER para voltar ao menu...")
        return
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while True:
            tempo_atual = time.time() - tempo_inicio
            
            # Reseta câmera a cada X segundos
            if tempo_atual - ultimo_camera >= camera_interval:
                if adb.tap(camera_x, camera_y):
                    contador_camera += 1
                    ultimo_camera = tempo_atual
            
            # Ativa Demon a cada Y minutos
            if tempo_atual - ultimo_demon >= demon_interval:
                if adb.tap(demon_x, demon_y):
                    contador_demon += 1
                    ultimo_demon = tempo_atual
            
            # Captura screenshot de EXP periodicamente
            if tempo_atual - ultimo_exp_capture >= exp_capture_interval:
                filepath = exp_tracker.capture_exp_screenshot()
                if filepath:
                    contador_exp_captures += 1
                ultimo_exp_capture = tempo_atual
            
            # Captura screenshot de EXP ganho periodicamente
            if tempo_atual - ultimo_exp_gain_capture >= exp_gain_interval:
                filepath = exp_gain_tracker.capture_exp_gain()
                if filepath:
                    contador_exp_gain_captures += 1
                    
                    # Tenta detectar XP ganho na screenshot (análise assíncrona leve)
                    if analytics and xp_detector and contador_exp_gain_captures % 5 == 0:
                        try:
                            xp_value = xp_detector.detect_xp_from_image(filepath)
                            if xp_value:
                                analytics.add_xp_gain(xp_value, source='combat')
                                analytics.register_combat(duration=2.0, killed=True)  # Assume kill se detectou XP
                        except:
                            pass
                
                ultimo_exp_gain_capture = tempo_atual
            
            # Análise de IA periódica (minimap, cores, círculos, OCR, combate)
            ia_interval = config.get_ai_config().get("minimap_analise_intervalo", 5)
            if ai_enabled and tempo_atual - ultimo_ia_analise >= ia_interval:
                # Captura screenshot temporário para análises de IA
                temp_screenshot = f"temp_ai_{datetime.now().strftime('%H%M%S')}.png"
                
                if adb.screenshot(temp_screenshot):
                    # Aguarda arquivo ser escrito
                    time.sleep(0.1)
                    
                    # Verifica se arquivo existe antes de processar
                    if os.path.exists(temp_screenshot):
                        try:
                            # 1. Detector Visual Corrigido - Análise precisa do minimapa
                            if detector_visual:
                                try:
                                    detection = detector_visual.detectar_objetos_reais(
                                        temp_screenshot,
                                        crop_minimap=True
                                    )
                                    
                                    if detection:
                                        resultados, debug_path = detection
                                        
                                        mobs_count = resultados.get('vermelho_mob', 0)
                                        
                                        # Mostra info no console
                                        if mobs_count > 0:
                                            print(f"  🔴 {mobs_count} mobs detectados no minimapa")
                                        
                                        contador_ia_analises += 1
                                        
                                        # Limpa pastas antigas (mantém apenas 10 mais recentes)
                                        cleanup_folder_images("minimap_captures", max_keep=10)
                                        cleanup_folder_images("debug_deteccao", max_keep=10)
                                        
                                        # Adiciona dados para ML
                                        if ml_predictor:
                                            now = datetime.now()
                                            ml_predictor.add_training_data({
                                                'hour': now.hour,
                                                'minute': now.minute,
                                                'pos_x': 0,
                                                'pos_y': 0,
                                                'sector_N': 0,
                                                'sector_E': 0,
                                                'sector_S': 0,
                                                'sector_W': 0,
                                                'enemy_count': mobs_count
                                            })
                                    
                                except Exception as e:
                                    print(f"⚠️ Erro detector visual: {e}")
                            
                            # 2. MinimapVision - Análise do minimap (fallback/complementar)
                            elif minimap_vision:
                                try:
                                    analise = minimap_vision.analyze_screenshot(temp_screenshot)
                                    
                                    if analise:
                                        contador_ia_analises += 1
                                        best_farming_direction = analise['best_direction']
                                        
                                        # Adiciona dados para ML
                                        if ml_predictor:
                                            now = datetime.now()
                                            ml_predictor.add_training_data({
                                                'hour': now.hour,
                                                'minute': now.minute,
                                                'pos_x': 0,
                                                'pos_y': 0,
                                                'sector_N': analise['sector_density'].get('N', 0),
                                                'sector_E': analise['sector_density'].get('E', 0),
                                                'sector_S': analise['sector_density'].get('S', 0),
                                                'sector_W': analise['sector_density'].get('W', 0),
                                                'enemy_count': analise['enemies_count']
                                            })
                                        
                                        # Movimento inteligente
                                        movimento_interval = config.get_ai_config().get("movimento_intervalo", 30)
                                        if (intelligent_movement and 
                                            config.get_ai_config().get("movimento_auto", False) and
                                            tempo_atual - ultimo_movimento_ia >= movimento_interval and
                                            analise['enemies_count'] > 0):
                                            
                                            moved_dir = intelligent_movement.move_to_best_farming_spot(analise['sector_density'])
                                            if moved_dir:
                                                contador_movimentos_ia += 1
                                                ultimo_movimento_ia = tempo_atual
                                except Exception as e:
                                    pass
                            
                            # 2. AdvancedVision - Detecção de cores, círculos e coordenadas
                            if advanced_vision:
                                av_config = config.get_advanced_vision_config()
                                
                                # Detecta cores configuradas
                                if av_config.get('detect_colors_enabled', True):
                                    try:
                                        target_colors = av_config.get('target_colors', ['vermelho', 'azul', 'amarelo'])
                                        color_results = advanced_vision.detect_colors(temp_screenshot, target_colors)
                                        if color_results and contador_ia_analises % 10 == 0:  # Log a cada 10 análises
                                            for color, data in color_results['colors_detected'].items():
                                                if data['count'] > 0:
                                                    print(f"  🎨 {color.capitalize()}: {data['count']} objetos")
                                    except Exception as e:
                                        pass
                                
                                # Detecta círculos
                                if av_config.get('detect_circles_enabled', True) and contador_ia_analises % 10 == 0:
                                    try:
                                        circle_results = advanced_vision.detect_circles(temp_screenshot)
                                        if circle_results and circle_results['circles_count'] > 0:
                                            print(f"  ⭕ Círculos: {circle_results['circles_count']} detectados")
                                    except Exception as e:
                                        pass
                                
                                # Lê coordenadas via OCR
                                if av_config.get('read_coords_enabled', True) and contador_ia_analises % 5 == 0:
                                    try:
                                        coord_results = advanced_vision.read_coordinates_ocr(temp_screenshot)
                                        if coord_results and coord_results['success']:
                                            coords = coord_results['coordinates']
                                            print(f"  📍 Posição: X:{coords['x']} Y:{coords['y']}")
                                    except Exception as e:
                                        pass
                            
                            # 3. CombatDetector - Detecção de combate
                            if combat_detector:
                                try:
                                    in_combat = combat_detector.is_in_combat(temp_screenshot)
                                except:
                                    pass
                            
                            # 4. OCRReader - Lê EXP e detecta perigos (reduzido para evitar sobrecarga)
                            if ocr_reader and contador_ia_analises % 5 == 0:
                                try:
                                    exp_pct = ocr_reader.read_exp_percentage(temp_screenshot, exp_region)
                                    if exp_pct:
                                        current_exp_percentage = exp_pct
                                        # Atualiza analytics
                                        if analytics:
                                            analytics.update_xp(exp_pct)
                                except:
                                    pass
                                
                                try:
                                    # Detecta nomes perigosos
                                    dangerous = ocr_reader.detect_dangerous_enemy(temp_screenshot)
                                    if dangerous:
                                        print(f"\n⚠️  INIMIGO PERIGOSO: {dangerous}!")
                                except:
                                    pass
                        
                        except Exception as e:
                            pass  # Ignora erros de IA para não travar farming
                        
                        # Remove temp
                        try:
                            os.remove(temp_screenshot)
                        except:
                            pass
                
                ultimo_ia_analise = tempo_atual
            
            # Gerencia ciclos de target
            if not em_ciclo_target:
                # Verifica se é hora de iniciar novo ciclo
                if tempo_atual - fim_ultimo_ciclo >= target_pause or fim_ultimo_ciclo == 0:
                    em_ciclo_target = True
                    clicks_no_ciclo = 0
                    ultimo_target = tempo_atual - target_interval  # Permite clicar imediatamente
            else:
                # Está em ciclo de target
                if clicks_no_ciclo < target_clicks:
                    if tempo_atual - ultimo_target >= target_interval:
                        if adb.tap(target_x, target_y):
                            contador_target += 1
                            clicks_no_ciclo += 1
                            ultimo_target = tempo_atual
                            
                            if clicks_no_ciclo >= target_clicks:
                                # Ciclo completo
                                em_ciclo_target = False
                                ciclos_target += 1
                                fim_ultimo_ciclo = tempo_atual
            
            # Atualiza display
            minutos = int(tempo_atual // 60)
            segundos = int(tempo_atual % 60)
            
            # Status do target
            if em_ciclo_target:
                status_target = f"🎯 Targetando ({clicks_no_ciclo}/{target_clicks})"
            else:
                tempo_ate_proximo = int(target_pause - (tempo_atual - fim_ultimo_ciclo))
                if tempo_ate_proximo > 0:
                    status_target = f"⏸️  Pausa ({tempo_ate_proximo}s)"
                else:
                    status_target = "🎯 Iniciando ciclo..."
            
            # Tempo até próximo Demon
            tempo_ate_demon = int(demon_interval - (tempo_atual - ultimo_demon))
            min_demon = tempo_ate_demon // 60
            seg_demon = tempo_ate_demon % 60
            
            # Monta display
            display = f"\r{status_target} | 🎥:{contador_camera} | 😈:{contador_demon}({min_demon}:{seg_demon:02d}) | 📸:{contador_exp_captures} | 💰:{contador_exp_gain_captures}"
            
            # Adiciona info de IA se habilitada
            if ai_enabled:
                display += f" | 🧠:{contador_ia_analises}"
                if best_farming_direction:
                    display += f"→{best_farming_direction}"
                if current_exp_percentage:
                    display += f" | EXP:{current_exp_percentage:.1f}%"
                if in_combat:
                    display += " | ⚔️"
            
            # Adiciona info de Analytics se habilitado
            if analytics:
                analytics_compact = analytics.print_live_stats(compact=True)
                # Só mostra parte da estatística para não poluir
                if current_exp_percentage:
                    xp_per_min = analytics.get_xp_per_minute()
                    if xp_per_min > 0:
                        display += f" | 📈{xp_per_min:.3f}/min"
            
            display += f" | ⏱️{minutos:02d}:{segundos:02d}"
            
            print(display, end="", flush=True)
            
            # Pequeno sleep para não sobrecarregar CPU
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        signal_handler(None, None)


def start_farming_cycles(adb: ADBConnection, config: Config, ciclos: int):
    """Inicia farming por número específico de ciclos - resetando câmera e targetando"""
    camera_x, camera_y = config.get_camera_position()
    camera_interval = config.get_camera_interval()
    target_x, target_y = config.get_target_position()
    target_interval = config.get_target_interval()
    
    print("\n" + "="*60)
    print(f"   🎯 FARMING: {ciclos} CICLOS DE TARGET")
    print("="*60)
    print(f"\n🎥 Reset de câmera: ({camera_x}, {camera_y}) - a cada {camera_interval}s")
    print(f"🎯 Target inimigos: ({target_x}, {target_y}) - a cada {target_interval}s")
    print("⚠️  Pressione Ctrl+C para parar\n")
    
    tempo_inicio = time.time()
    contador_camera = 0
    ultimo_camera = 0
    
    # Handler para Ctrl+C
    def signal_handler(sig, frame):
        tempo_total = time.time() - tempo_inicio
        minutos = int(tempo_total // 60)
        segundos = int(tempo_total % 60)
        print("\n\n" + "="*60)
        print("   ⏹️  FARMING INTERROMPIDO")
        print("="*60)
        print(f"\n📊 Estatísticas:")
        print(f"  🎯 Targets realizados: {i}/{ciclos}")
        print(f"  🎥 Resets de câmera: {contador_camera}")
        print(f"  ⏱️  Tempo total: {minutos}min {segundos}s")
        print()
        input("Pressione ENTER para voltar ao menu...")
        return
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        for i in range(1, ciclos + 1):
            tempo_atual = time.time() - tempo_inicio
            
            # Targeta inimigo
            if adb.tap(target_x, target_y):
                minutos = int(tempo_atual // 60)
                segundos = int(tempo_atual % 60)
                
                # Mostra progresso
                porcentagem = (i / ciclos) * 100
                print(f"\r🎯 Targets: {i}/{ciclos} ({porcentagem:.1f}%) | 🎥 Camera: {contador_camera} | ⏱️  {minutos:02d}:{segundos:02d}", end="", flush=True)
            
            # Durante o intervalo, verifica se precisa resetar câmera
            inicio_espera = time.time() - tempo_inicio
            while (time.time() - tempo_inicio) - inicio_espera < target_interval and i < ciclos:
                tempo_atual = time.time() - tempo_inicio
                
                # Reseta câmera se necessário
                if tempo_atual - ultimo_camera >= camera_interval:
                    if adb.tap(camera_x, camera_y):
                        contador_camera += 1
                        ultimo_camera = tempo_atual
                        minutos = int(tempo_atual // 60)
                        segundos = int(tempo_atual % 60)
                        porcentagem = (i / ciclos) * 100
                        print(f"\r🎯 Targets: {i}/{ciclos} ({porcentagem:.1f}%) | 🎥 Camera: {contador_camera} | ⏱️  {minutos:02d}:{segundos:02d}", end="", flush=True)
                
                time.sleep(0.1)
        
        # Farming completo
        tempo_total = time.time() - tempo_inicio
        minutos = int(tempo_total // 60)
        segundos = int(tempo_total % 60)
        
        print("\n\n" + "="*60)
        print("   ✅ FARMING COMPLETO!")
        print("="*60)
        print(f"\n📊 Estatísticas:")
        print(f"  🎯 Targets em inimigos: {ciclos}")
        print(f"  🎥 Resets de câmera: {contador_camera}")
        print(f"  ⏱️  Tempo total: {minutos}min {segundos}s")
        print()
        input("Pressione ENTER para voltar ao menu...")
        
    except KeyboardInterrupt:
        signal_handler(None, None)


def show_config_menu(config: Config):
    """Mostra menu de configurações"""
    print("\n" + "="*60)
    print("   ⚙️  CONFIGURAÇÕES")
    print("="*60)
    
    camera_x, camera_y = config.get_camera_position()
    camera_interval = config.get_camera_interval()
    target_x, target_y = config.get_target_position()
    target_interval = config.get_target_interval()
    target_clicks = config.get_target_clicks_per_cycle()
    target_pause = config.get_target_pause_between_cycles()
    demon_x, demon_y = config.get_demon_position()
    demon_interval = config.get_demon_interval()
    exp_region = config.get_exp_region()
    minimap_region = config.get_minimap_region()
    
    print(f"\n🎥 Botão de Reset de Câmera:")
    print(f"   📍 Posição: ({camera_x}, {camera_y})")
    print(f"   ⏱️  Intervalo: {camera_interval} segundos")
    
    print(f"\n🎯 Botão de Target (Mirar Inimigos):")
    print(f"   📍 Posição: ({target_x}, {target_y})")
    print(f"   🔄 Ciclo: {target_clicks} cliques de {target_interval}s")
    print(f"   ⏸️  Pausa entre ciclos: {target_pause} segundos")
    print(f"   📊 Total por ciclo: {target_clicks * target_interval}s de action + {target_pause}s pausa")
    
    print(f"\n😈 Botão Demon:")
    print(f"   📍 Posição: ({demon_x}, {demon_y})")
    print(f"   ⏱️  Intervalo: {demon_interval} segundos ({demon_interval//60} minutos)")
    
    print(f"\n📊 EXP Tracker:")
    print(f"   📍 Região: ({exp_region['x']}, {exp_region['y']}) {exp_region['width']}x{exp_region['height']}")
    print(f"   ⏱️  Intervalo: {config.get_exp_capture_interval()}s")
    print(f"   📁 Pasta: {config.get_training_folder()}/")
    
    exp_gain_region = config.get_exp_gain_region()
    print(f"\n💰 EXP Ganho (ao matar inimigos):")
    print(f"   📍 Região: ({exp_gain_region['x']}, {exp_gain_region['y']}) {exp_gain_region['width']}x{exp_gain_region['height']}")
    print(f"   ⏱️  Intervalo: {config.get_exp_gain_capture_interval()}s")
    print(f"   📁 Pasta: {config.get_exp_gain_folder()}/")
    print(f"   🖼️  Máx imagens: {config.get_max_exp_gain_images()}")
    
    print(f"\n🗺️  Mini Mapa Analyzer:")
    print(f"   📍 Região: ({minimap_region['x']}, {minimap_region['y']}) {minimap_region['width']}x{minimap_region['height']}")
    print(f"   ⏱️  Intervalo: {config.get_minimap_capture_interval()}s")
    print(f"   🔴 Detectar inimigos: {'✓' if config.should_detect_enemies() else '✗'}")
    print(f"   🔵 Detectar jogadores: {'✓' if config.should_detect_players() else '✗'}")
    print(f"   📝 Detectar coordenadas: {'✓' if config.should_detect_coordinates() else '✗'}")
    
    # Configurações de IA
    if config.is_ai_enabled():
        ai_config = config.get_ai_config()
        print(f"\n🧠 Inteligência Artificial:")
        print(f"   ✓ IA Habilitada")
        print(f"   🔍 MinimapVision (OpenCV): {'✓' if ai_config.get('usar_minimap_vision') else '✗'}")
        print(f"   🎓 ML Predictor (RandomForest): {'✓' if ai_config.get('usar_ml_predictor') else '✗'}")
        print(f"   📖 OCR Reader (Tesseract): {'✓' if ai_config.get('usar_ocr') else '✗'}")
        print(f"   ⚔️  Combat Detector (ImageHash): {'✓' if ai_config.get('usar_combat_detector') else '✗'}")
        print(f"   🚶 Movimento Inteligente: {'✓' if ai_config.get('usar_movimento_inteligente') else '✗'}")
        if ai_config.get('movimento_auto'):
            print(f"   🤖 Movimento Automático: ✓ (a cada {ai_config.get('movimento_intervalo', 30)}s)")
    else:
        print(f"\n🧠 Inteligência Artificial: ✗ Desabilitada")
        if not AI_AVAILABLE:
            print("   ⚠️  Instale: pip install opencv-python scikit-learn pytesseract imagehash")
    
    print(f"\n📱 Dispositivo ADB:")
    print(f"   🔌 Endereço: {config.get('adb_device')}")
    print(f"   📺 Resolução: {config.get('screen_width')}x{config.get('screen_height')}")
    print(f"   📄 Config: {config.config_file}")
    
    print("\n💡 Dicas:")
    print(f"   • Edite {config.config_file} para alterar configurações")
    print("   • Use 'adb shell settings put system pointer_location 1'")
    print("     para ver coordenadas ao tocar na tela")
    
    input("\nPressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    main()
