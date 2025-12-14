#!/usr/bin/env python3
"""
AI Modules - Machine Learning & Computer Vision
Sistema de inteligência artificial para bot farming
"""

import cv2
import numpy as np
import pytesseract
import imagehash
from PIL import Image
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json
import os
import re
import time

# Machine Learning
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

# Métricas de aprendizado
try:
    from metricas_aprendizado import MetricasAprendizadoML
    METRICAS_AVAILABLE = True
except ImportError:
    METRICAS_AVAILABLE = False


class MinimapVision:
    """Análise de minimap usando Computer Vision (OpenCV)"""
    
    # Direções dos 8 setores do minimap
    DIRECTIONS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.minimap_region = config.get('regiao_minimap', {})
        self.colors = config.get('cores_minimap', {})
        
        # Histórico de detecções
        self.enemy_history = []
        self.player_history = []
        
    def analyze_screenshot(self, screenshot_path: str) -> Dict[str, Any]:
        """Analisa screenshot completo e extrai info do minimap"""
        try:
            # Carrega imagem
            img = cv2.imread(screenshot_path)
            if img is None:
                return None
            
            # Extrai região do minimap
            x, y = self.minimap_region['x'], self.minimap_region['y']
            w, h = self.minimap_region['width'], self.minimap_region['height']
            minimap = img[y:y+h, x:x+w]
            
            # Detecta elementos
            enemies = self._detect_enemies(minimap)
            players = self._detect_players(minimap)
            player_pos = self._detect_player_position(minimap)
            
            # Divide em setores e conta densidade
            sector_density = self._calculate_sector_density(minimap, enemies)
            
            # Encontra melhor direção
            best_direction = self._find_best_direction(sector_density)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'enemies_count': len(enemies),
                'players_count': len(players),
                'enemies_positions': enemies,
                'players_positions': players,
                'player_position': player_pos,
                'sector_density': sector_density,
                'best_direction': best_direction
            }
            
            # Atualiza histórico
            self.enemy_history.append({
                'timestamp': datetime.now(),
                'count': len(enemies),
                'positions': enemies
            })
            
            return result
            
        except Exception as e:
            print(f"✗ Erro ao analisar minimap: {e}")
            return None
    
    def _detect_enemies(self, minimap: np.ndarray) -> List[Tuple[int, int]]:
        """Detecta inimigos (círculos vermelhos) no minimap"""
        # Converte para HSV
        hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
        
        # Range de vermelho (configurável)
        enemy_config = self.colors.get('inimigos', {})
        lower_red = np.array(enemy_config.get('hsv_min', [0, 100, 100]))
        upper_red = np.array(enemy_config.get('hsv_max', [10, 255, 255]))
        
        # Cria máscara
        mask = cv2.inRange(hsv, lower_red, upper_red)
        
        # Encontra contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Extrai posições
        positions = []
        for contour in contours:
            if cv2.contourArea(contour) > 5:  # Filtro de tamanho mínimo
                M = cv2.moments(contour)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    positions.append((cx, cy))
        
        return positions
    
    def _detect_players(self, minimap: np.ndarray) -> List[Tuple[int, int]]:
        """Detecta jogadores (círculos azuis) no minimap"""
        hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
        
        player_config = self.colors.get('jogadores', {})
        lower_blue = np.array(player_config.get('hsv_min', [100, 100, 100]))
        upper_blue = np.array(player_config.get('hsv_max', [130, 255, 255]))
        
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        positions = []
        for contour in contours:
            if cv2.contourArea(contour) > 5:
                M = cv2.moments(contour)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    positions.append((cx, cy))
        
        return positions
    
    def _detect_player_position(self, minimap: np.ndarray) -> Optional[Tuple[int, int]]:
        """Detecta posição do jogador (seta amarela) no minimap"""
        hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
        
        player_pos_config = self.colors.get('player', {})
        lower_yellow = np.array(player_pos_config.get('hsv_min', [20, 100, 100]))
        upper_yellow = np.array(player_pos_config.get('hsv_max', [30, 255, 255]))
        
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Pega o maior contorno (seta do jogador)
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                return (cx, cy)
        
        return None
    
    def _calculate_sector_density(self, minimap: np.ndarray, enemies: List[Tuple[int, int]]) -> Dict[str, int]:
        """Divide minimap em 8 setores e conta inimigos em cada um"""
        h, w = minimap.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        density = {direction: 0 for direction in self.DIRECTIONS}
        
        for ex, ey in enemies:
            # Calcula ângulo em relação ao centro
            dx, dy = ex - center_x, center_y - ey  # Inverte Y (tela)
            angle = np.degrees(np.arctan2(dy, dx))
            
            # Normaliza para 0-360
            if angle < 0:
                angle += 360
            
            # Determina setor (45 graus cada)
            # N=0°, NE=45°, E=90°, SE=135°, S=180°, SW=225°, W=270°, NW=315°
            sector_idx = int((angle + 22.5) // 45) % 8
            density[self.DIRECTIONS[sector_idx]] += 1
        
        return density
    
    def _find_best_direction(self, sector_density: Dict[str, int]) -> str:
        """Encontra direção com mais inimigos"""
        if not sector_density:
            return 'N'  # Default
        
        return max(sector_density, key=sector_density.get)
    
    def get_density_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de densidade ao longo do tempo"""
        if not self.enemy_history:
            return {}
        
        total_enemies = sum(h['count'] for h in self.enemy_history)
        avg_enemies = total_enemies / len(self.enemy_history) if self.enemy_history else 0
        
        return {
            'total_detections': len(self.enemy_history),
            'total_enemies_seen': total_enemies,
            'avg_enemies_per_scan': avg_enemies,
            'max_enemies': max(h['count'] for h in self.enemy_history) if self.enemy_history else 0
        }


class MLPredictor:
    """Machine Learning - Previsão de densidade e clustering"""
    
    def __init__(self, model_folder: str = "ml_models"):
        self.model_folder = Path(model_folder)
        self.model_folder.mkdir(exist_ok=True)
        
        # Modelos - Ajustado para 2 clusters (baseado na análise de diversidade)
        # Com 51.8% de dados únicos, usar menos clusters evita convergência
        self.density_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.cluster_model = KMeans(n_clusters=2, random_state=42, n_init=10)
        self.scaler = StandardScaler()
        
        # Dados de treino
        self.training_data = []
        
        # Sistema de métricas
        if METRICAS_AVAILABLE:
            self.metricas = MetricasAprendizadoML()
            print("✅ Sistema de métricas ML ativado")
        else:
            self.metricas = None
        
        # Carrega modelos salvos
        self._load_models()
    
    def add_training_data(self, features: Dict[str, Any]):
        """Adiciona dados para treino contínuo"""
        self.training_data.append(features)
        
        # Registra nas métricas
        if self.metricas:
            self.metricas.register_sample_collected(len(self.training_data))
        
        # Mostra progresso a cada 10 amostras
        if len(self.training_data) % 10 == 0:
            print(f"🧠 ML: {len(self.training_data)} amostras coletadas")
        
        # Auto-treina a cada 100 amostras
        if len(self.training_data) % 100 == 0:
            print(f"🤖 Treinando modelos com {len(self.training_data)} amostras...")
            self.train_models()
        
        # Salva backup incremental a cada 50 amostras (sem treinar)
        elif len(self.training_data) % 50 == 0:
            self._save_training_data_only()
    
    def train_models(self):
        """Treina modelos com dados coletados"""
        if len(self.training_data) < 10:
            print(f"⚠️ Dados insuficientes para treino ({len(self.training_data)}/10 mínimo)")
            return False
        
        try:
            start_time = time.time()
            
            # Prepara dados
            X = []
            y = []
            
            for data in self.training_data:
                features = [
                    data.get('hour', 0),
                    data.get('minute', 0),
                    data.get('pos_x', 0),
                    data.get('pos_y', 0),
                    data.get('sector_N', 0),
                    data.get('sector_E', 0),
                    data.get('sector_S', 0),
                    data.get('sector_W', 0)
                ]
                X.append(features)
                y.append(data.get('enemy_count', 0))
            
            X = np.array(X)
            y = np.array(y)
            
            # Normaliza features
            X_scaled = self.scaler.fit_transform(X)
            
            # Treina RandomForest para prever densidade
            self.density_model.fit(X_scaled, y)
            
            # Treina KMeans para clustering de áreas
            self.cluster_model.fit(X_scaled[:, 2:4])  # Apenas coordenadas x,y
            
            # Salva modelos
            self._save_models()
            
            # Registra treinamento nas métricas
            training_duration = time.time() - start_time
            if self.metricas:
                # Calcula acurácia aproximada (R² score)
                from sklearn.metrics import r2_score
                y_pred = self.density_model.predict(X_scaled)
                accuracy = r2_score(y, y_pred)
                
                self.metricas.register_training_completed(
                    sample_count=len(self.training_data),
                    duration=training_duration,
                    accuracy=accuracy
                )
            
            print(f"✅ Modelos ML treinados com {len(self.training_data)} amostras!")
            print(f"   ⏱️ Tempo de treino: {training_duration:.2f}s")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao treinar modelos: {e}")
            return False
    
    def predict_density(self, hour: int, minute: int, pos_x: int, pos_y: int, 
                       sector_counts: Dict[str, int]) -> float:
        """Prevê densidade de inimigos para posição e horário"""
        try:
            features = [[
                hour, minute, pos_x, pos_y,
                sector_counts.get('N', 0),
                sector_counts.get('E', 0),
                sector_counts.get('S', 0),
                sector_counts.get('W', 0)
            ]]
            
            features_scaled = self.scaler.transform(features)
            prediction = self.density_model.predict(features_scaled)[0]
            
            return max(0, prediction)  # Não retorna valores negativos
            
        except Exception as e:
            print(f"✗ Erro na previsão: {e}")
            return 0.0
    
    def find_best_cluster(self, positions: List[Tuple[int, int]]) -> int:
        """Identifica cluster com mais atividade"""
        if not positions:
            return 0
        
        try:
            positions_scaled = self.scaler.transform(positions)
            clusters = self.cluster_model.predict(positions_scaled)
            
            # Conta pontos por cluster
            cluster_counts = {}
            for cluster in clusters:
                cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1
            
            # Retorna cluster mais populado
            return max(cluster_counts, key=cluster_counts.get)
            
        except:
            return 0
    
    def _save_models(self):
        """Salva modelos treinados com nomes descritivos"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Salva modelos principais
            joblib.dump(self.density_model, self.model_folder / "density_model.pkl")
            joblib.dump(self.cluster_model, self.model_folder / "cluster_model.pkl")
            joblib.dump(self.scaler, self.model_folder / "scaler.pkl")
            
            # Salva modelos com nomes descritivos (compatível com projeto anterior)
            joblib.dump(self.density_model, self.model_folder / "modelo_sklearn.pkl")
            joblib.dump(self.cluster_model, self.model_folder / "modelo_ultra.pkl")
            
            # Modelo completo (todos juntos)
            modelo_completo = {
                'density_model': self.density_model,
                'cluster_model': self.cluster_model,
                'scaler': self.scaler,
                'training_samples': len(self.training_data),
                'timestamp': timestamp,
                'version': '1.0'
            }
            joblib.dump(modelo_completo, self.model_folder / "modelo_ultra_adb.pkl")
            joblib.dump(modelo_completo, self.model_folder / "ml_avancado_modelo.pkl")
            
            # Salva dados de treino
            self._save_training_data_only()
            
            print(f"💾 Modelos salvos em {self.model_folder}/")
            print(f"   • modelo_sklearn.pkl (RandomForest)")
            print(f"   • modelo_ultra.pkl (KMeans)")
            print(f"   • modelo_ultra_adb.pkl (Completo)")
            print(f"   • ml_avancado_modelo.pkl (Completo)")
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar modelos: {e}")
    
    def _save_training_data_only(self):
        """Salva apenas dados de treino (backup incremental)"""
        try:
            with open(self.model_folder / "training_data.json", 'w') as f:
                json.dump(self.training_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar dados de treino: {e}")
    
    def _load_models(self):
        """Carrega modelos salvos"""
        try:
            density_path = self.model_folder / "density_model.pkl"
            cluster_path = self.model_folder / "cluster_model.pkl"
            scaler_path = self.model_folder / "scaler.pkl"
            data_path = self.model_folder / "training_data.json"
            
            if density_path.exists():
                self.density_model = joblib.load(density_path)
                print("✓ Modelo de densidade carregado")
            
            if cluster_path.exists():
                self.cluster_model = joblib.load(cluster_path)
                print("✓ Modelo de clustering carregado")
            
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                print("✓ Scaler carregado")
            
            if data_path.exists():
                with open(data_path, 'r') as f:
                    self.training_data = json.load(f)
                print(f"✓ {len(self.training_data)} amostras de treino carregadas")
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar modelos: {e}")
    
    def get_training_status(self) -> Dict[str, Any]:
        """Retorna status do treinamento"""
        total_samples = len(self.training_data)
        next_train = 100 - (total_samples % 100)
        next_backup = 50 - (total_samples % 50)
        
        return {
            'total_samples': total_samples,
            'samples_to_next_train': next_train if next_train < 100 else 0,
            'samples_to_next_backup': next_backup if next_backup < 50 else 0,
            'can_train': total_samples >= 10,
            'model_folder': str(self.model_folder),
            'models_exist': (self.model_folder / "modelo_ultra_adb.pkl").exists()
        }
    
    def force_train(self) -> bool:
        """Força treinamento imediato (mínimo 10 amostras)"""
        if len(self.training_data) >= 10:
            print(f"\n🤖 Treinamento manual iniciado...")
            return self.train_models()
        else:
            print(f"✗ Mínimo 10 amostras necessárias ({len(self.training_data)}/10)")
            return False


class OCRReader:
    """OCR para leitura de textos usando Tesseract"""
    
    def __init__(self):
        # Configuração do Tesseract
        self.tesseract_config = '--psm 7 --oem 3'  # Single line, LSTM
        
        # Nomes perigosos para detectar
        self.dangerous_names = ['Giant', 'Boss', 'Elite', 'Champion', 'Unique']
    
    def read_exp_percentage(self, screenshot_path: str, region: Dict[str, int]) -> Optional[float]:
        """Lê porcentagem de EXP usando OCR"""
        try:
            # Carrega e processa imagem
            img = cv2.imread(screenshot_path)
            x, y = region['x'], region['y']
            w, h = region['width'], region['height']
            
            roi = img[y:y+h, x:x+w]
            
            # Preprocessamento para melhorar OCR
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Threshold adaptativo
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
            
            # Resize para melhor precisão
            resized = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            
            # OCR
            text = pytesseract.image_to_string(resized, config=self.tesseract_config)
            
            # Extrai número
            import re
            numbers = re.findall(r'\d+\.?\d*', text)
            if numbers:
                return float(numbers[0])
            
            return None
            
        except Exception as e:
            print(f"✗ Erro OCR EXP: {e}")
            return None
    
    def detect_dangerous_enemy(self, screenshot_path: str) -> Optional[str]:
        """Detecta nomes de inimigos perigosos na tela"""
        try:
            img = cv2.imread(screenshot_path)
            
            # OCR na imagem inteira (ou região específica)
            text = pytesseract.image_to_string(img)
            
            # Busca nomes perigosos
            for name in self.dangerous_names:
                if name.lower() in text.lower():
                    return name
            
            return None
            
        except Exception as e:
            print(f"✗ Erro OCR detecção: {e}")
            return None
    
    def read_coordinates(self, screenshot_path: str, region: Dict[str, int]) -> Optional[Tuple[int, int]]:
        """Lê coordenadas do minimap (ex: 288, 2635)"""
        try:
            img = cv2.imread(screenshot_path)
            x, y = region['x'], region['y']
            w, h = region['width'], region['height']
            
            roi = img[y:y+h, x:x+w]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            text = pytesseract.image_to_string(thresh, config=self.tesseract_config)
            
            # Extrai números entre parênteses
            import re
            match = re.search(r'\((\d+),\s*(\d+)\)', text)
            if match:
                return (int(match.group(1)), int(match.group(2)))
            
            return None
            
        except Exception as e:
            print(f"✗ Erro OCR coordenadas: {e}")
            return None


class CombatDetector:
    """Detecção de combate usando ImageHash"""
    
    def __init__(self, threshold: int = 10):
        self.threshold = threshold
        self.previous_hash = None
        self.combat_detected = False
        self.combat_history = []
    
    def is_in_combat(self, screenshot_path: str) -> bool:
        """Detecta se está em combate comparando frames"""
        try:
            # Calcula hash da imagem
            img = Image.open(screenshot_path)
            current_hash = imagehash.average_hash(img)
            
            if self.previous_hash is None:
                self.previous_hash = current_hash
                return False
            
            # Calcula diferença
            diff = current_hash - self.previous_hash
            
            # Se diferença > threshold, está em combate (tela mudando)
            in_combat = diff > self.threshold
            
            # Atualiza
            self.previous_hash = current_hash
            self.combat_detected = in_combat
            
            # Histórico
            self.combat_history.append({
                'timestamp': datetime.now(),
                'in_combat': in_combat,
                'diff': diff
            })
            
            return in_combat
            
        except Exception as e:
            print(f"✗ Erro detecção combate: {e}")
            return False
    
    def get_combat_stats(self) -> Dict[str, Any]:
        """Estatísticas de combate"""
        if not self.combat_history:
            return {}
        
        combat_count = sum(1 for h in self.combat_history if h['in_combat'])
        
        return {
            'total_checks': len(self.combat_history),
            'combat_detected': combat_count,
            'combat_percentage': (combat_count / len(self.combat_history)) * 100,
            'currently_in_combat': self.combat_detected
        }


class IntelligentMovement:
    """Sistema de movimento inteligente baseado em IA"""
    
    # Mapeamento de direções para ângulos de joystick
    DIRECTION_ANGLES = {
        'N': 0,
        'NE': 45,
        'E': 90,
        'SE': 135,
        'S': 180,
        'SW': 225,
        'W': 270,
        'NW': 315
    }
    
    def __init__(self, adb, config: Dict[str, Any]):
        self.adb = adb
        self.config = config
        self.joystick_center = (
            config.get('joystick_centro_x', 150),
            config.get('joystick_centro_y', 850)
        )
        self.joystick_radius = config.get('joystick_raio', 80)
    
    def move_to_direction(self, direction: str, duration: float = 1.0) -> bool:
        """Move o personagem para uma direção específica"""
        if direction not in self.DIRECTION_ANGLES:
            return False
        
        try:
            angle = self.DIRECTION_ANGLES[direction]
            
            # Calcula posição do joystick
            angle_rad = np.radians(angle)
            offset_x = int(self.joystick_radius * np.cos(angle_rad))
            offset_y = int(self.joystick_radius * np.sin(angle_rad))
            
            target_x = self.joystick_center[0] + offset_x
            target_y = self.joystick_center[1] - offset_y  # Inverte Y
            
            # Simula swipe (arrasto) no joystick
            import subprocess
            subprocess.run([
                "adb", "-s", self.adb.device_address, "shell", "input", "swipe",
                str(self.joystick_center[0]), str(self.joystick_center[1]),
                str(target_x), str(target_y),
                str(int(duration * 1000))  # Duração em ms
            ], capture_output=True, timeout=5)
            
            return True
            
        except Exception as e:
            print(f"✗ Erro ao mover: {e}")
            return False
    
    def move_to_best_farming_spot(self, sector_density: Dict[str, int]) -> str:
        """Move automaticamente para área com mais inimigos"""
        best_direction = max(sector_density, key=sector_density.get)
        
        if sector_density[best_direction] > 0:
            self.move_to_direction(best_direction, duration=2.0)
            return best_direction
        
        return None


class AdvancedVision:
    """
    Detecção avançada com OpenCV:
    - Detecção de cores com cv2.inRange()
    - Detecção de círculos com cv2.HoughCircles()
    - OCR com Tesseract para ler coordenadas
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.detection_history = []
        self.coordinates_history = []
        
        # Configurações de detecção
        self.color_ranges = config.get('color_ranges', {
            'vermelho': {'hsv_min': [0, 100, 100], 'hsv_max': [10, 255, 255]},
            'azul': {'hsv_min': [100, 100, 100], 'hsv_max': [130, 255, 255]},
            'verde': {'hsv_min': [40, 50, 50], 'hsv_max': [80, 255, 255]},
            'amarelo': {'hsv_min': [20, 100, 100], 'hsv_max': [30, 255, 255]},
            'roxo': {'hsv_min': [130, 50, 50], 'hsv_max': [160, 255, 255]},
            'laranja': {'hsv_min': [10, 100, 100], 'hsv_max': [20, 255, 255]},
        })
        
        # Parâmetros de detecção de círculos
        self.circle_params = config.get('circle_detection', {
            'dp': 1.2,
            'minDist': 20,
            'param1': 50,
            'param2': 30,
            'minRadius': 5,
            'maxRadius': 50
        })
        
        # Região de coordenadas na tela (onde aparece X: Y:)
        self.coord_region = config.get('coord_region', {
            'x': 10,
            'y': 10,
            'width': 200,
            'height': 30
        })
    
    def detect_colors(self, screenshot_path: str, target_colors: List[str] = None) -> Dict[str, Any]:
        """
        Detecta cores específicas na imagem usando cv2.inRange()
        
        Args:
            screenshot_path: Caminho da imagem
            target_colors: Lista de cores a detectar ['vermelho', 'azul', etc]
                          Se None, detecta todas as cores configuradas
        
        Returns:
            Dict com contagens e posições de cada cor detectada
        """
        try:
            # Carrega imagem
            img = cv2.imread(screenshot_path)
            if img is None:
                return None
            
            # Converte para HSV
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Define cores a detectar
            if target_colors is None:
                target_colors = list(self.color_ranges.keys())
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'colors_detected': {}
            }
            
            # Detecta cada cor
            for color_name in target_colors:
                if color_name not in self.color_ranges:
                    continue
                
                color_config = self.color_ranges[color_name]
                lower = np.array(color_config['hsv_min'])
                upper = np.array(color_config['hsv_max'])
                
                # Cria máscara com cv2.inRange()
                mask = cv2.inRange(hsv, lower, upper)
                
                # Encontra contornos
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Extrai informações
                positions = []
                areas = []
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 10:  # Filtro mínimo
                        M = cv2.moments(contour)
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                            positions.append((cx, cy))
                            areas.append(area)
                
                results['colors_detected'][color_name] = {
                    'count': len(positions),
                    'positions': positions,
                    'areas': areas,
                    'total_area': sum(areas),
                    'avg_area': sum(areas) / len(areas) if areas else 0
                }
            
            # Salva histórico
            self.detection_history.append(results)
            
            return results
            
        except Exception as e:
            print(f"✗ Erro detecção de cores: {e}")
            return None
    
    def detect_circles(self, screenshot_path: str, min_radius: int = None, max_radius: int = None) -> Dict[str, Any]:
        """
        Detecta círculos na imagem usando cv2.HoughCircles()
        
        Args:
            screenshot_path: Caminho da imagem
            min_radius: Raio mínimo (sobrescreve config)
            max_radius: Raio máximo (sobrescreve config)
        
        Returns:
            Dict com círculos detectados (centro, raio)
        """
        try:
            # Carrega imagem
            img = cv2.imread(screenshot_path)
            if img is None:
                return None
            
            # Converte para grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Aplica blur para reduzir ruído
            gray = cv2.medianBlur(gray, 5)
            
            # Parâmetros
            params = self.circle_params.copy()
            if min_radius is not None:
                params['minRadius'] = min_radius
            if max_radius is not None:
                params['maxRadius'] = max_radius
            
            # Detecta círculos com HoughCircles
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=params['dp'],
                minDist=params['minDist'],
                param1=params['param1'],
                param2=params['param2'],
                minRadius=params['minRadius'],
                maxRadius=params['maxRadius']
            )
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'circles_count': 0,
                'circles': []
            }
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                
                for circle in circles[0, :]:
                    x, y, r = int(circle[0]), int(circle[1]), int(circle[2])
                    results['circles'].append({
                        'center': (x, y),
                        'radius': r,
                        'diameter': r * 2,
                        'area': np.pi * r * r
                    })
                
                results['circles_count'] = len(results['circles'])
            
            return results
            
        except Exception as e:
            print(f"✗ Erro detecção de círculos: {e}")
            return None
    
    def read_coordinates_ocr(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Lê coordenadas da tela usando OCR (Tesseract)
        Procura por padrões como "X: 1234 Y: 5678" ou "1234, 5678"
        
        Args:
            screenshot_path: Caminho da imagem
        
        Returns:
            Dict com coordenadas X, Y detectadas
        """
        try:
            # Carrega imagem
            img = cv2.imread(screenshot_path)
            if img is None:
                return None
            
            # Extrai região de coordenadas
            x, y = self.coord_region['x'], self.coord_region['y']
            w, h = self.coord_region['width'], self.coord_region['height']
            coord_img = img[y:y+h, x:x+w]
            
            # Pré-processamento para OCR
            # Converte para grayscale
            gray = cv2.cvtColor(coord_img, cv2.COLOR_BGR2GRAY)
            
            # Aumenta contraste
            gray = cv2.equalizeHist(gray)
            
            # Threshold adaptativo
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Inverte se fundo escuro
            if np.mean(thresh) < 127:
                thresh = cv2.bitwise_not(thresh)
            
            # Redimensiona para melhorar OCR
            thresh = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            
            # Aplica OCR
            text = pytesseract.image_to_string(
                thresh,
                config='--psm 7 -c tessedit_char_whitelist=0123456789XY:,. '
            )
            
            # Parse do texto
            coords = self._parse_coordinates(text)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'raw_text': text.strip(),
                'coordinates': coords,
                'success': coords is not None
            }
            
            # Salva histórico
            if coords:
                self.coordinates_history.append({
                    'timestamp': datetime.now(),
                    'x': coords['x'],
                    'y': coords['y']
                })
            
            return result
            
        except Exception as e:
            print(f"✗ Erro OCR coordenadas: {e}")
            return None
    
    def _parse_coordinates(self, text: str) -> Optional[Dict[str, int]]:
        """
        Parseia texto OCR para extrair coordenadas X e Y
        Suporta formatos:
        - "X: 1234 Y: 5678"
        - "X:1234 Y:5678"
        - "1234, 5678"
        - "1234 5678"
        """
        try:
            # Padrão 1: X: 1234 Y: 5678
            pattern1 = r'X\s*[:.]?\s*(\d+)\s*Y\s*[:.]?\s*(\d+)'
            match = re.search(pattern1, text, re.IGNORECASE)
            if match:
                return {'x': int(match.group(1)), 'y': int(match.group(2))}
            
            # Padrão 2: 1234, 5678
            pattern2 = r'(\d+)\s*,\s*(\d+)'
            match = re.search(pattern2, text)
            if match:
                return {'x': int(match.group(1)), 'y': int(match.group(2))}
            
            # Padrão 3: 1234 5678 (dois números separados)
            pattern3 = r'(\d{3,})\s+(\d{3,})'
            match = re.search(pattern3, text)
            if match:
                return {'x': int(match.group(1)), 'y': int(match.group(2))}
            
            return None
            
        except Exception as e:
            print(f"✗ Erro parse coordenadas: {e}")
            return None
    
    def detect_colored_circles(self, screenshot_path: str, color: str = 'vermelho') -> Dict[str, Any]:
        """
        Combina detecção de cores + círculos
        Detecta círculos de uma cor específica
        
        Args:
            screenshot_path: Caminho da imagem
            color: Cor a detectar ('vermelho', 'azul', etc)
        
        Returns:
            Dict com círculos da cor especificada
        """
        try:
            # Carrega imagem
            img = cv2.imread(screenshot_path)
            if img is None:
                return None
            
            # Aplica filtro de cor
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            color_config = self.color_ranges.get(color, self.color_ranges['vermelho'])
            lower = np.array(color_config['hsv_min'])
            upper = np.array(color_config['hsv_max'])
            
            mask = cv2.inRange(hsv, lower, upper)
            
            # Aplica máscara na imagem
            filtered = cv2.bitwise_and(img, img, mask=mask)
            
            # Converte para grayscale
            gray = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            
            # Detecta círculos na imagem filtrada
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=self.circle_params['dp'],
                minDist=self.circle_params['minDist'],
                param1=self.circle_params['param1'],
                param2=self.circle_params['param2'],
                minRadius=self.circle_params['minRadius'],
                maxRadius=self.circle_params['maxRadius']
            )
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'color': color,
                'circles_count': 0,
                'circles': []
            }
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                
                for circle in circles[0, :]:
                    x, y, r = int(circle[0]), int(circle[1]), int(circle[2])
                    results['circles'].append({
                        'center': (x, y),
                        'radius': r,
                        'color': color
                    })
                
                results['circles_count'] = len(results['circles'])
            
            return results
            
        except Exception as e:
            print(f"✗ Erro detecção círculos coloridos: {e}")
            return None
    
    def get_movement_vector(self) -> Optional[Tuple[float, float]]:
        """
        Calcula vetor de movimento baseado no histórico de coordenadas
        Útil para detectar direção do movimento do personagem
        
        Returns:
            (dx, dy) - Vetor de movimento ou None se não houver histórico
        """
        if len(self.coordinates_history) < 2:
            return None
        
        # Pega últimas 2 posições
        pos1 = self.coordinates_history[-2]
        pos2 = self.coordinates_history[-1]
        
        dx = pos2['x'] - pos1['x']
        dy = pos2['y'] - pos1['y']
        
        return (dx, dy)
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de detecção"""
        total_detections = len(self.detection_history)
        total_coords = len(self.coordinates_history)
        
        return {
            'total_color_detections': total_detections,
            'total_coordinates_read': total_coords,
            'last_detection': self.detection_history[-1] if self.detection_history else None,
            'last_coordinates': self.coordinates_history[-1] if self.coordinates_history else None
        }
