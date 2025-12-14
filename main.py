#!/usr/bin/env python3
"""
Bot Ultra ADB - Silkroad Origin Mobile
Sistema automatizado de farming com IA e controle via ADB
"""

import subprocess
import sys
import time
import argparse
from typing import Optional

ADB_DEVICE = "192.168.240.112:5555"

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


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Bot Ultra ADB - Silkroad Origin Mobile",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
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
        choices=["connect", "disconnect", "list", "info"],
        help="Comando a executar"
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


if __name__ == "__main__":
    main()

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