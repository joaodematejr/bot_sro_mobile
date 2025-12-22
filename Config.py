from constants import ADB_DEVICE, CONFIG_FILE
import json
import os
from typing import Dict, Any

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
            "intervalo_reset_camera": 1,
            "posicao_botao_target": {
                "x": 1726,
                "y": 797,
                "descricao": "Botão para mirar/targetar inimigos próximos"
            },
            "intervalo_target": 5,
            "target_clicks_por_ciclo": 5,
            "target_pausa_entre_ciclos": 30,
            "pasta_imagens_treino": "treino_ml",
            "inimigos_para_fugir": ["Giant", "Boss", "Elite", "Champion"],
            "salvar_imagens_treino": True,
            "max_imagens_treino": 10
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


    def get_training_folder(self) -> str:
        """Retorna pasta para salvar imagens de treino"""
        return self.config.get("pasta_imagens_treino", "treino_ml")
    
    def should_save_training_images(self) -> bool:
        """Verifica se deve salvar imagens de treino"""
        return self.config.get("salvar_imagens_treino", True)
    
    def get_max_training_images(self) -> int:
        """Retorna número máximo de imagens de treino"""
        return self.config.get("max_imagens_treino", 50)

