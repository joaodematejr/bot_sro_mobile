
# ===================== IMPORTS =====================
import os
import sys
import glob
import re
import time
import threading
import argparse
import subprocess
import builtins
from datetime import datetime
import cv2
import pytesseract
# Imports de módulos do projeto
import Config
import ADBConnection
from session_utils import gerar_session_id, auto_save_sessao, exportar_json_ultima_sessao, carregar_historico_sessoes
from ml_utils import carregar_modelos, MonitoramentoTreinamento, auto_treinar_modelos, scaler, identificar_hotspots
from adb_utils import ativar_pointer_location, desativar_pointer_location, clicar_repetidamente
# from prints_utils import tirar_print  # DESATIVADO: causava travamento no Waydroid
from utils_imagem import crop_image, detect_location_string
from minimap_analysis import detectar_setor_com_mais_vermelhos

# ===================== FUNÇÕES UTILITÁRIAS =====================


def print_log(*args, **kwargs):
    """
    Imprime mensagem no terminal e salva no arquivo de log.
    """
    msg = " ".join(str(a) for a in args)
    builtins.print(*args, **kwargs)
    with open("log_bot.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def contar_mobs_proximos_yolo():
    """
    Detecta inimigos próximos usando YOLO (Ultralytics) no print mais recente.
    Retorna o número de detecções.
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print_log("Ultralytics YOLO não está instalado. Instale com: pip install ultralytics")
        return 0

    lista_prints = glob.glob(os.path.join('prints', '*.png'))
    if not lista_prints:
        return 0
    img_path = max(lista_prints, key=os.path.getctime)

    model_path = 'runs/detect/train/weights/best.pt'  # modelo customizado treinado
    try:
        model = YOLO(model_path)
    except Exception as e:
        print_log(f"Erro ao carregar modelo YOLO: {e}")
        return 0

    results = model(img_path)
    save_dir = 'prints_yolo'
    os.makedirs(save_dir, exist_ok=True)
    for r in results:
        im_bgr = r.plot()
        base = os.path.basename(img_path)
        save_path = os.path.join(save_dir, base.replace('.png', f'_yolo.png'))
        cv2.imwrite(save_path, im_bgr)
    
    # Limpar prints_yolo para manter apenas 15 arquivos
    _limpar_prints_yolo(15)
    
    return len(results[0].boxes) if results and hasattr(results[0], 'boxes') else 0

def _limpar_prints_yolo(max_prints=15):
    """Mantém apenas os max_prints arquivos mais recentes em prints_yolo."""
    save_dir = 'prints_yolo'
    if not os.path.exists(save_dir):
        return
    arquivos = sorted([f for f in os.listdir(save_dir) if f.endswith('.png')], 
                     key=lambda x: os.path.getctime(os.path.join(save_dir, x)))
    while len(arquivos) > max_prints:
        arquivo_remover = arquivos.pop(0)
        try:
            os.remove(os.path.join(save_dir, arquivo_remover))
        except Exception:
            pass

def coletar_coordenadas_personagem():
    """
    Coleta as coordenadas do personagem a partir do print da tela.
    """
    lista_prints = glob.glob(os.path.join('prints', '*.png'))
    if not lista_prints:
        return None, None
    caminho_print = max(lista_prints, key=os.path.getctime)
    crop_path = 'localizacao_tmp.png'
    crop_image(caminho_print, crop_path, x=180, y=180, w=100, h=25)
    localizacao = detect_location_string(crop_path)
    match = re.search(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?", localizacao)
    if match:
        x, y = int(match.group(1)), int(match.group(2))
        return x, y
    return None, None

def coletar_xp_percentual():
    """
    Coleta o percentual de XP a partir do print da tela.
    """
    lista_prints = glob.glob(os.path.join('prints', '*.png'))
    if not lista_prints:
        return None
    caminho_print = max(lista_prints, key=os.path.getctime)
    crop_image(caminho_print, 'xp.png', x=30, y=900, w=140, h=125)
    img = cv2.imread('xp.png')
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(gray, config=custom_config)
    print_log("Texto detectado XP:", text)
    match = re.search(r"([0-9]+\.[0-9]+)%", text)
    if match:
        return float(match.group(1))
    return None

def exibir_estatisticas():
    """Exibe estatísticas do bot."""
    print("\n=== ESTATÍSTICAS DO BOT ===")
    try:
        historico = carregar_historico_sessoes()
        if not historico:
            print("Nenhuma sessão encontrada.")
            return
        
        total_sessoes = len(historico)
        print(f"Total de sessões: {total_sessoes}")
        
        total_mobs = sum(len(s.get('amostras', [])) for s in historico)
        total_eventos = sum(len(s.get('eventos', [])) for s in historico)
        print(f"Total de mobs detectados: {total_mobs}")
        print(f"Total de eventos: {total_eventos}")
    except Exception as e:
        print(f"Erro ao exibir estatísticas: {e}")

def exibir_relatorio_otimizacao_ml():
    """Exibe relatório de otimização de ML."""
    print("\n=== RELATÓRIO DE OTIMIZAÇÃO ML ===")
    print("[INFO] Relatório de otimização ML ainda não implementado.")

def coletar_coordenadas_personagem():
    # Tira print e faz crop da área de localização
    lista_prints = glob.glob(os.path.join('prints', '*.png'))
    if not lista_prints:
        return None, None
    caminho_print = max(lista_prints, key=os.path.getctime)
    crop_path = 'localizacao_tmp.png'
    crop_image(caminho_print, crop_path, x=180, y=180, w=100, h=25)
    localizacao = detect_location_string(crop_path)
    match = re.search(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?", localizacao)
    if match:
        x, y = int(match.group(1)), int(match.group(2))
        return x, y
    return None, None

def coletar_xp_percentual():
    lista_prints = glob.glob(os.path.join('prints', '*.png'))
    if not lista_prints:
        return None
    caminho_print = max(lista_prints, key=os.path.getctime)
    crop_image(caminho_print, 'xp.png', x=30, y=900, w=140, h=125)
    img = cv2.imread('xp.png')
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(gray, config=custom_config)
    print_log("Texto detectado XP:", text)
    match = re.search(r"([0-9]+\.[0-9]+)%", text)
    if match:
        return float(match.group(1))
    return None

def start_infinite_farming(adb: ADBConnection, config: Config):
    # ====== Sessão ======
    session_id = gerar_session_id()
    dados_sessao = {
        'session_id': session_id,
        'inicio': datetime.now(),
        'amostras': [],
        'eventos': [],
    }
    # Executa o loop principal de farming infinito, coleta dados, executa ações e treina modelos ML.
    modelos = carregar_modelos()
    contador_amostras = 0
    X, y = [], []
    monitoramento_ml = MonitoramentoTreinamento()
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

    stop_event = threading.Event()

    def clique_fixo_thread():
        while not stop_event.is_set():
            print("🖱️ Clique automático em (1726, 797)")
            adb.tap(1726, 797)
            stop_event.wait(3)

    thread_fixo = threading.Thread(target=clique_fixo_thread, daemon=True)
    thread_fixo.start()

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
            # tirar_print(adb, config)  # DESATIVADO: causava travamento no Waydroid
            # --- NOVO: Detecta setor mais denso e move personagem ---
            lista_prints = glob.glob(os.path.join('prints', '*.png'))
            if lista_prints:
                caminho_print = max(lista_prints, key=os.path.getctime)
                mini_map_path = 'mini_map.png'
                crop_image(caminho_print, mini_map_path, x=130, y=150, w=200, h=200)
                grid_size = 3
                hotspot, grid = detectar_setor_com_mais_vermelhos(mini_map_path, grid_size=grid_size, debug=True)
                if hotspot is not None:
                    pass
                else:
                    print("[BOT] Não foi possível detectar o setor mais denso do minimapa.")
            else:
                print("[BOT] Nenhuma imagem encontrada para análise do minimapa.")
            # Fim da movimentação automática
            # ====== ML: Coleta de features e auto-treinamento ======
            x, y_coord = coletar_coordenadas_personagem()
            mobs_nearby = contar_mobs_proximos_yolo()
            xp_percent = coletar_xp_percentual()
            features = [x, y_coord, mobs_nearby, xp_percent]
            target = mobs_nearby     # Exemplo: pode ser densidade de inimigos, XP ganho, etc.
            if None not in features and all(isinstance(f, (int, float)) for f in features):
                X.append(features)
                y.append(target)
                contador_amostras += 1
                dados_sessao['amostras'].append({
                    'timestamp': datetime.now(),
                    'features': features,
                    'target': target
                })
                monitoramento_ml.registrar_amostra(features, target)
            else:
                print(f"[ML] Amostra ignorada por dados inválidos: {features}")
            if contador_amostras % 10 == 0:
                auto_save_sessao(session_id, dados_sessao)
            if len(X) > 0:
                X_scaled = scaler.fit_transform(X)
                auto_treinar_modelos(modelos, X_scaled, y, contador_amostras)
                for nome, modelo in modelos.items():
                    if contador_amostras >= 5:
                        modelo.fit(X_scaled, y)
                if contador_amostras >= 5:
                    pred = modelos['sklearn'].predict([X_scaled[-1]])
                    print(f"[ML] Predição de densidade de inimigos: {pred[0]:.2f}")
                    clusters, kmeans = identificar_hotspots(X_scaled, n_clusters=2)
                    print(f"[ML] Cluster do local atual: {clusters[-1]}")
                    monitoramento_ml.registrar_amostra(features=X_scaled[-1], target=y[-1], pred=pred[0])
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
        stop_event.set()
        auto_save_sessao(session_id, dados_sessao)
        exportar_json_ultima_sessao(session_id)
        monitoramento_ml.resumo()
        monitoramento_ml.plotar_curva_aprendizado()
    contador_amostras = 0
    X, y = [], []
    monitoramento_ml = MonitoramentoTreinamento()
    # Exemplo: mobs_nearby e xp_percent podem ser extraídos via visão computacional ou lógica do bot
    # Aqui, valores fictícios para demonstração
    # import time removido (já importado globalmente)
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
        tempo_ultimo_click_fixo = time.time()

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

            # Clique fixo a cada 3 segundos em (1726, 797)
            if agora - tempo_ultimo_click_fixo >= 1:
                print("🖱️ Clique automático em (1726, 797)")
                adb.tap(1726, 797)
                tempo_ultimo_click_fixo = agora

            sucesso = adb.tap(camera_x, camera_y)
            # tirar_print(adb, config)  # DESATIVADO: causava travamento no Waydroid
            # --- NOVO: Detecta setor mais denso e move personagem ---
            lista_prints = glob.glob(os.path.join('prints', '*.png'))
            if lista_prints:
                caminho_print = max(lista_prints, key=os.path.getctime)
                mini_map_path = 'mini_map.png'
                crop_image(caminho_print, mini_map_path, x=130, y=150, w=200, h=200)
                grid_size = 3
                hotspot, grid = detectar_setor_com_mais_vermelhos(mini_map_path, grid_size=grid_size, debug=True)
                if hotspot is not None:
                    # linha, coluna = hotspot
                    # Calcula o centro do setor alvo no minimapa
                    # setor_w = 200 // grid_size
                    # setor_h = 200 // grid_size
                    # centro_x = 130 + coluna * setor_w + setor_w // 2
                    # centro_y = 150 + linha * setor_h + setor_h // 2
                    # print(f"\n🗺️ Movendo para setor mais denso: linha={linha}, coluna={coluna} (x={centro_x}, y={centro_y})")
                    # Realiza swipe do joystick até o setor alvo (exemplo: swipe curto)
                    # Ajuste os valores conforme necessário para o seu jogo
                    # joystick_x, joystick_y = config.get('joystick_centro_x', 288), config.get('joystick_centro_y', 868)
                    # Calcula direção aproximada (pode ser melhorado para pathfinding)
                    # delta_x = centro_x - 230  # 230: centro do minimapa na tela (ajuste se necessário)
                    # delta_y = centro_y - 250  # 250: centro do minimapa na tela (ajuste se necessário)
                    # Normaliza o vetor para um swipe curto
                    # fator = 40  # quanto maior, mais longo o swipe
                    # destino_x = int(joystick_x + (delta_x / 100) * fator)
                    # destino_y = int(joystick_y + (delta_y / 100) * fator)
                    # print(f"[BOT] Swipe do joystick: ({joystick_x},{joystick_y}) -> ({destino_x},{destino_y})")
                    # adb.swipe(joystick_x, joystick_y, destino_x, destino_y, duration=500)
                    pass
                else:
                    print("[BOT] Não foi possível detectar o setor mais denso do minimapa.")
            else:
                print("[BOT] Nenhuma imagem encontrada para análise do minimapa.")
            # Fim da movimentação automática
            # ====== ML: Coleta de features e auto-treinamento ======
            # Exemplo de coleta de features (substitua pelos valores reais do seu bot)
            # Coleta real dos dados do bot
            x, y_coord = coletar_coordenadas_personagem()
            mobs_nearby = contar_mobs_proximos_yolo()
            xp_percent = coletar_xp_percentual()
            features = [x, y_coord, mobs_nearby, xp_percent]
            target = mobs_nearby     # Exemplo: pode ser densidade de inimigos, XP ganho, etc.
            # Verifica se todos os valores são válidos
            if None not in features and all(isinstance(f, (int, float)) for f in features):
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
            else:
                print(f"[ML] Amostra ignorada por dados inválidos: {features}")
            # Auto-save a cada 10 amostras
            if contador_amostras % 10 == 0:
                auto_save_sessao(session_id, dados_sessao)
            # Só executa pipeline ML se houver amostras válidas
            if len(X) > 0:
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
    print("  8. Treinar modelo YOLO (dataset_yolo)")
    print("  9. Avaliar modelo YOLO (dataset_yolo)")
    print(" 10. Visualizar detecções YOLO (prints_yolo)")
    print(" 11. Visualização ao vivo (prints_yolo + logs)")
    print(" 12. Treinar modelo Scikit-learn (ML)")
    print(" 13. Atualizar curva de aprendizado (ML)")
    print(" 14. Clicar repetidamente em (1726, 797) a cada 3s")
    print()
    escolha = input("Escolha uma opção: ")
    # Exibe o menu principal e retorna a escolha do usuário.
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
    # Gerencia a interação do usuário com o bot, permitindo a execução de várias funções.
    
    import subprocess
    while True:
        escolha = menu()

        if escolha == "1":
            start_infinite_farming(adb, config)

        elif escolha == "2":
            #show_config_menu(config)
            pass

        elif escolha == "3":
            exibir_estatisticas()
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "4":
            exibir_relatorio_otimizacao_ml()
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

        elif escolha == "8":
            print("\n🚀 Treinando modelo YOLO com dataset_yolo...")
            subprocess.run(["python3", "train_yolo.py"])
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "9":
            print("\n📊 Avaliando modelo YOLO com dataset_yolo...")
            subprocess.run(["python3", "eval_yolo.py"])
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "10":
            print("\n🖼️ Gerando visualizações das detecções YOLO em prints_yolo...")
            subprocess.run(["python3", "visualize_yolo.py"])
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "11":
            print("\n🖼️ Modo janela: última print_yolo + logs ao vivo...")
            subprocess.run(["python3", "bot_visual.py"])
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "12":
            print("\n🔬 Treinando modelo Scikit-learn (ML)...")
            try:
                # Treinamento básico do modelo Scikit-learn
                from ml_utils import auto_treinar_modelos, carregar_modelos, scaler
                historico = carregar_historico_sessoes()
                X, y = [], []
                total_sessoes = len(historico)
                total_amostras = 0
                total_eventos = 0
                for sessao in historico:
                    total_amostras += len(sessao.get('amostras', []))
                    total_eventos += len(sessao.get('eventos', []))
                    for amostra in sessao.get('amostras', []):
                        features = amostra.get('features')
                        target = amostra.get('target')
                        if features is not None and target is not None:
                            X.append(features)
                            y.append(target)
                if len(X) > 0:
                    X_scaled = scaler.fit_transform(X)
                    modelos = carregar_modelos()
                    auto_treinar_modelos(modelos, X_scaled, y, len(X))
                    print("\n✅ Treinamento do modelo Scikit-learn concluído!")
                    print(f"Sessões usadas: {total_sessoes}")
                    print(f"Amostras usadas: {len(X)} (total registradas: {total_amostras})")
                    print(f"Eventos registrados: {total_eventos}")
                else:
                    print("\n⚠️ Não há amostras suficientes para treinar o modelo.")
            except Exception as e:
                print(f"\n❌ Erro ao treinar modelo Scikit-learn: {e}")
            input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "13":
            print("\n📈 Atualizando curva de aprendizado (ML)...")
            try:
                monitoramento = MonitoramentoTreinamento()
                monitoramento.plotar_curva_aprendizado()
                print("\n✅ curva_aprendizado.png atualizada!")
            except Exception as e:
                print(f"\n❌ Erro ao atualizar curva de aprendizado: {e}")
            input("\nPressione ENTER para voltar ao menu...")
        elif escolha == "14":
            print("\n🖱️ Iniciando cliques automáticos em (1726, 797) a cada 3 segundos...")
            clicar_repetidamente(adb, x=1726, y=797, intervalo=3)
            input("\nPressione ENTER para voltar ao menu...")
        else:
            print("\n❌ Opção inválida!")
            input("\nPressione ENTER para continuar...")


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
        # Interpreta argumentos de linha de comando e executa o fluxo adequado.
    
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