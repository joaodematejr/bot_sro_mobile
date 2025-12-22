import subprocess
import time
from datetime import datetime
import os

from constants import ADB_DEVICE

class ADBConnection:
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
            """
            Executa um swipe (arrasto) na tela do dispositivo
            Args:
                x1, y1: Ponto inicial
                x2, y2: Ponto final
                duration: Duração em ms
            Returns:
                True se o comando foi executado com sucesso
            """
            try:
                # Timeout dinâmico: duração do swipe + 2s de margem (mínimo 5s)
                timeout = max(5, int(duration / 1000) + 2)
                subprocess.run(
                    ["adb", "-s", self.device_address, "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)],
                    capture_output=True,
                    timeout=timeout
                )
                return True
            except Exception as e:
                print(f"✗ Erro ao executar swipe: {e}")
                return False
    """
    Gerenciador de conexão ADB
    """
    
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