
# ===============================
# Imports organizados
# ===============================
import os
import sys
import time
import glob
import re
import argparse
from datetime import datetime
import ADBConnection
import Config
from session_utils import gerar_session_id, auto_save_sessao, carregar_historico_sessoes, exportar_json_ultima_sessao
from ml_utils import MonitoramentoTreinamento, carregar_modelos, scaler, auto_treinar_modelos, identificar_hotspots
from utils_imagem import crop_image, detect_location_string
from minimap_analysis import detectar_setor_com_mais_vermelhos
from menu_utils import menu
from adb_utils import ativar_pointer_location, desativar_pointer_location
from prints_utils import tirar_print

# ===============================
# Integração Machine Learning (Scikit-learn)
# ===============================
# 🎓 RandomForest Regressor - Predição de densidade de inimigos
# 🗺️ KMeans Clustering - Identificação de hotspots de farming
# 📊 StandardScaler - Normalização de features para melhor acurácia
# 💾 Auto-Treinamento - Treina automaticamente a cada 100 amostras
# 📈 Múltiplos Modelos - 4 formatos salvos (sklearn, ultra, ultra_adb, avancado)
# 🔄 Treinamento Contínuo - Melhora ao longo do tempo

from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
import matplotlib.pyplot as plt


def mostrar_localizacao_personagem(adb, config, mostrar_mapa_calor=False, grid_size=3):

    import re
    # Busca a imagem mais recente na pasta prints
    lista_prints = glob.glob(os.path.join('prints', '*.png'))
    if lista_prints:
        caminho_print = max(lista_prints, key=os.path.getctime)
        crop_path = 'localizacao.png'
        crop_image(caminho_print, crop_path, x=180, y=180, w=100, h=25)
        localizacao = detect_location_string(crop_path)
        match = re.search(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?", localizacao)
        if match:
            x, y = match.group(1), match.group(2)
            print(f"📍 Localização do personagem:")
            print(f"   X: {x}")
            print(f"   Y: {y}")
        else:
            print(f"Localização detectada (OCR): {localizacao}")
        # --- NOVO: Análise de mapa de calor do mini mapa ---
        if mostrar_mapa_calor:
            mini_map_path = 'mini_map.png'
            crop_image(caminho_print, mini_map_path, x=130, y=150, w=200, h=200)
            hotspot, grid = detectar_setor_com_mais_vermelhos(mini_map_path, grid_size=grid_size, debug=True)
            if hotspot is not None:
                linha, coluna = hotspot
                print(f"\n🗺️ Setor mais denso do minimapa:")
                print(f"   Linha: {linha}")
                print(f"   Coluna: {coluna}")
            else:
                print("\n[MiniMap] Não foi possível detectar o setor mais denso.")
    else:
        print("Erro: nenhuma imagem encontrada na pasta prints.")

def start_infinite_farming(adb: ADBConnection, config: Config):
        # ====== Sessão ======
    session_id = gerar_session_id()
    dados_sessao = {
        'session_id': session_id,
        'inicio': datetime.now(),
        'amostras': [],
        'eventos': [],
    }
    modelos = carregar_modelos()
    contador_amostras = 0
    X, y = [], []
    monitoramento_ml = MonitoramentoTreinamento()
    # Exemplo: mobs_nearby e xp_percent podem ser extraídos via visão computacional ou lógica do bot
    # Aqui, valores fictícios para demonstração
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
            mostrar_localizacao_personagem(adb, config, mostrar_mapa_calor=True, grid_size=3)
            # ====== ML: Coleta de features e auto-treinamento ======
            # Exemplo de coleta de features (substitua pelos valores reais do seu bot)
            # x, y: coordenadas do personagem (exemplo: 2036, 1321)
            # mobs_nearby: número de inimigos próximos (exemplo: 5)
            # xp_percent: porcentagem de XP atual (exemplo: 44.64)
            x, y_coord = 2036, 1321  # Substitua pela leitura real
            mobs_nearby = 5          # Substitua pela detecção real
            xp_percent = 44.64       # Substitua pela leitura real
            features = [x, y_coord, mobs_nearby, xp_percent]
            target = mobs_nearby     # Exemplo: pode ser densidade de inimigos, XP ganho, etc.
            X.append(features)
            y.append(target)
            contador_amostras += 1
            # Salva amostra na sessão
            dados_sessao['amostras'].append({
                'timestamp': datetime.now(),
                'features': features,
                'target': target
            })
            # Monitoramento ML: registrar amostra
            monitoramento_ml.registrar_amostra(features, target)
            # Auto-save a cada 10 amostras
            if contador_amostras % 10 == 0:
                auto_save_sessao(session_id, dados_sessao)
            # Normalização
            X_scaled = scaler.fit_transform(X)
            # Auto-treinamento de todos os modelos
            auto_treinar_modelos(modelos, X_scaled, y, contador_amostras)
            # Treinamento contínuo: todos os modelos são atualizados a cada ciclo
            for nome, modelo in modelos.items():
                if contador_amostras >= 5:
                    modelo.fit(X_scaled, y)
            # Predição e clustering usando o modelo principal
            if contador_amostras >= 5:
                pred = modelos['sklearn'].predict([X_scaled[-1]])
                print(f"[ML] Predição de densidade de inimigos: {pred[0]:.2f}")
                # Identificação de hotspot (cluster)
                clusters, kmeans = identificar_hotspots(X_scaled, n_clusters=2)
                print(f"[ML] Cluster do local atual: {clusters[-1]}")
                # Monitoramento de treinamento ML
                monitoramento_ml.registrar_amostra(features=X_scaled[-1], target=y[-1], pred=pred[0])
                # Exibir resumo do monitoramento a cada milestone
                if len(monitoramento_ml.timeline) in monitoramento_ml.milestones:
                    monitoramento_ml.resumo()
                    monitoramento_ml.plotar_curva_aprendizado()
            else:
                print("[ML] Aguardando mais amostras para treinar o modelo...")
            contador_camera += 1
            if sucesso:
                print(f"🎥 Reset de câmera realizado com sucesso.")
            else:
                print(f"🎥 Falha ao resetar câmera!")
            time.sleep(camera_interval)
    except KeyboardInterrupt:
        print("\n⏹️  Farming infinito interrompido pelo usuário.")
        # Salva sessão ao finalizar
        auto_save_sessao(session_id, dados_sessao)
        exportar_json_ultima_sessao(session_id)
        # Exibir resumo e curva de aprendizado ao finalizar
        monitoramento_ml.resumo()
        monitoramento_ml.plotar_curva_aprendizado()

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
    # Função agora importada de adb_utils.py
    pass

def desativar_pointer_location(adb):
    # Função agora importada de adb_utils.py
    pass


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