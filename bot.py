from prints_utils import tirar_print
import argparse
import sys

import subprocess

import ADBConnection
import Config


def start_infinite_farming(adb: ADBConnection, config: Config):
    import time
    camera_x, camera_y = config.get_camera_position()
    camera_interval = config.get_camera_interval()
    intervalo_troca_arma = config.get("intervalo_troca_arma", 720)  # padrão 12 min
    intervalo_berserk = config.get("intervalo_berserk", 240)        # padrão 4 min
    delay_troca_arma_1 = config.get("delay_troca_arma_1", 2)
    delay_troca_arma_2 = config.get("delay_troca_arma_2", 0.5)

    print("\n" + "="*60)
    print("   🚀 FARMING INFINITO INICIADO")
    print("="*60)
    print(f"\n🎥 Reset de câmera: ({camera_x}, {camera_y}) - a cada {camera_interval}s")

    contador_camera = 0
    try:
        # Clicar nos botões ao iniciar
        print("🔄 Trocando de arma para Debuff...")
        adb.tap(1735, 600)
        time.sleep(delay_troca_arma_1)
        adb.tap(1636, 568)
        time.sleep(delay_troca_arma_2)

        tempo_ultimo_click = time.time()
        tempo_ultimo_click_4min = time.time()

        # Clique inicial em (1831, 534) ao iniciar o farming
        print("🦾 Verificando se possui Berserk (1831, 534)...")
        adb.tap(1831, 534)

        while True:
            agora = time.time()
            # A cada X minutos, clicar novamente nos botões de troca de arma
            if agora - tempo_ultimo_click >= intervalo_troca_arma:
                print("🔄 Trocando de arma para Debuff...")
                adb.tap(1735, 600)
                time.sleep(delay_troca_arma_1)
                adb.tap(1636, 568)
                time.sleep(delay_troca_arma_2)
                tempo_ultimo_click = agora

            # A cada Y minutos, clicar no botão (1831, 534)
            if agora - tempo_ultimo_click_4min >= intervalo_berserk:
                print("🦾 Verificando se possui Berserk (1831, 534)...")
                adb.tap(1831, 534)
                tempo_ultimo_click_4min = agora

            sucesso = adb.tap(camera_x, camera_y)
            tirar_print(adb, config)
            contador_camera += 1
            if sucesso:
                print(f"🎥 Reset de câmera realizado com sucesso.")
            else:
                print(f"🎥 Falha ao resetar câmera!")
            time.sleep(camera_interval)
    except KeyboardInterrupt:
        print("\n⏹️  Farming infinito interrompido pelo usuário.")

def menu():
    """Menu principal"""
    print("\n" + "="*60)
    print("   🚀 BOT ULTRA ADB - SILKROAD ORIGIN")
    print("="*60)
    print("\nOpções:")
    print("  1. Iniciar farming (infinito)")
    print("  2. Configurações")
    print("  3. Ver estatísticas")
    print("  4. Relatório de Otimização ML")
    print("  5. Ativar pointer_location (mostrar coordenadas)")
    print("  6. Desativar pointer_location")
    print("  7. Sair")
    print()
    escolha = input("Escolha uma opção: ")
    return escolha


def run_interactive_menu():
    """Executa o menu interativo"""
    # Carrega configurações
    config = Config.Config()
    
    adb = ADBConnection.ADBConnection()
    
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
            #show_config_menu(config)
            pass

        elif escolha == "3":
            print("\n📊 Estatísticas")
            print("⚠️  Funcionalidade em desenvolvimento")
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "4":
            print("\n🤖 Relatório de Otimização ML")
            print("⚠️  Funcionalidade em desenvolvimento")
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "5":
            print("\n🖱️ Ativando pointer_location (mostrar coordenadas na tela)...")
            ativar_pointer_location(adb)
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "6":
            print("\n🖱️ Desativando pointer_location...")
            desativar_pointer_location(adb)
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "7":
            print("\n👋 Encerrando bot...")
            sys.exit(0)

        else:
            print("\n❌ Opção inválida!")
            input("\nPressione ENTER para continuar...")
def ativar_pointer_location(adb):
    try:
        result = subprocess.run([
            "adb", "-s", adb.device_address, "shell", "settings", "put", "system", "pointer_location", "1"
        ], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ pointer_location ativado com sucesso!")
        else:
            print(f"✗ Falha ao ativar pointer_location: {result.stderr}")
    except Exception as e:
        print(f"✗ Erro ao ativar pointer_location: {e}")

def desativar_pointer_location(adb):
    try:
        result = subprocess.run([
            "adb", "-s", adb.device_address, "shell", "settings", "put", "system", "pointer_location", "0"
        ], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ pointer_location desativado com sucesso!")
        else:
            print(f"✗ Falha ao desativar pointer_location: {result.stderr}")
    except Exception as e:
        print(f"✗ Erro ao desativar pointer_location: {e}")


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
    
    if args.command is None or args.command == "menu":
        run_interactive_menu()
        return
    
    device_address = f"{args.ip}:{args.port}"
    
    adb = ADBConnection.ADBConnection(device_address=device_address)
    
    if not adb.check_adb_installed():
        sys.exit(1)
    
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