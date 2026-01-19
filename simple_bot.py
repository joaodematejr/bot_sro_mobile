"""
Bot Simples para ADB - Cliques Automáticos
Estrutura minimalista para conectar com dispositivo via ADB e realizar cliques
"""
import subprocess
import time
import sys
import json
import os
import threading

class SimpleBotADB:
    """Bot simples para interação com dispositivo Android via ADB"""
    
    def __init__(self, device_address: str = "192.168.240.112:5555"):
        """
        Inicializa o bot com endereço do dispositivo
        
        Args:
            device_address: Endereço IP:porta do dispositivo (padrão: 127.0.0.1:5555)
        """
        self.device_address = device_address
        self.connected = False
        
    def check_adb(self) -> bool:
        """Verifica se ADB está instalado"""
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ ADB encontrado")
                return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("✗ ADB não encontrado. Instale com: sudo apt install adb")
            return False
    
    def connect(self) -> bool:
        """Conecta ao dispositivo via ADB"""
        try:
            # Tenta conectar
            result = subprocess.run(
                ["adb", "connect", self.device_address],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "connected" in result.stdout.lower() or "already connected" in result.stdout.lower():
                print(f"✓ Conectado a {self.device_address}")
                self.connected = True
                return True
            else:
                print(f"✗ Falha ao conectar: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"✗ Erro na conexão: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Desconecta do dispositivo"""
        try:
            result = subprocess.run(
                ["adb", "disconnect", self.device_address],
                capture_output=True,
                text=True,
                timeout=5
            )
            print("✓ Desconectado")
            self.connected = False
            return True
        except Exception as e:
            print(f"✗ Erro ao desconectar: {e}")
            return False
    
    def tap(self, x: int, y: int) -> bool:
        """
        Realiza um clique em coordenadas específicas
        
        Args:
            x: Coordenada X
            y: Coordenada Y
            
        Returns:
            True se o clique foi executado com sucesso
        """
        if not self.connected:
            print("✗ Dispositivo não conectado")
            return False
            
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_address, "shell", "input", "tap", str(x), str(y)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"✗ Erro ao clicar: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao executar clique: {e}")
            return False
    
    def click_loop(self, x: int, y: int, interval: float = 1.0, max_clicks: int = None):
        """
        Realiza cliques repetidos em uma posição
        
        Args:
            x: Coordenada X
            y: Coordenada Y
            interval: Intervalo entre cliques em segundos (padrão: 1.0)
            max_clicks: Número máximo de cliques (None = infinito)
        """
        if not self.connected:
            print("✗ Dispositivo não conectado")
            return
        
        print(f"🤖 Iniciando cliques em ({x}, {y}) a cada {interval}s")
        print("   Pressione Ctrl+C para parar\n")
        
        click_count = 0
        
        try:
            while True:
                if max_clicks and click_count >= max_clicks:
                    print(f"\n✓ Completados {click_count} cliques")
                    break
                
                if self.tap(x, y):
                    click_count += 1
                    print(f"  Clique #{click_count} em ({x}, {y})")
                else:
                    print(f"  Falha no clique #{click_count + 1}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹ Parado pelo usuário após {click_count} cliques")
    
    def click_sequence(self, positions: list, interval: float = 1.0, repeat: int = 1):
        """
        Realiza uma sequência de cliques em múltiplas posições
        
        Args:
            positions: Lista de tuplas (x, y) com as coordenadas
            interval: Intervalo entre cliques em segundos
            repeat: Quantas vezes repetir a sequência
        """
        if not self.connected:
            print("✗ Dispositivo não conectado")
            return
        
        print(f"🤖 Iniciando sequência de {len(positions)} posições")
        print(f"   Repetições: {repeat} | Intervalo: {interval}s\n")
        
        try:
            for cycle in range(repeat):
                print(f"--- Ciclo {cycle + 1}/{repeat} ---")
                
                for i, (x, y) in enumerate(positions, 1):
                    if self.tap(x, y):
                        print(f"  ✓ Clique {i}/{len(positions)} em ({x}, {y})")
                    else:
                        print(f"  ✗ Falha no clique {i}/{len(positions)}")
                    
                    if i < len(positions):  # Não espera após o último clique
                        time.sleep(interval)
                
                if cycle < repeat - 1:  # Espera entre ciclos
                    time.sleep(interval)
            
            print(f"\n✓ Sequência completada!")
            
        except KeyboardInterrupt:
            print(f"\n\n⏹ Sequência interrompida pelo usuário")
    
    def enable_pointer_location(self) -> bool:
        """
        Ativa o pointer_location (mostra coordenadas na tela)
        
        Returns:
            True se ativado com sucesso
        """
        if not self.connected:
            print("✗ Dispositivo não conectado")
            return False
        
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_address, "shell", "settings", "put", "system", "pointer_location", "1"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print("✓ Pointer Location ATIVADO - coordenadas visíveis na tela")
                return True
            else:
                print(f"✗ Falha ao ativar: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao ativar pointer_location: {e}")
            return False
    
    def disable_pointer_location(self) -> bool:
        """
        Desativa o pointer_location (remove coordenadas da tela)
        
        Returns:
            True se desativado com sucesso
        """
        if not self.connected:
            print("✗ Dispositivo não conectado")
            return False
        
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_address, "shell", "settings", "put", "system", "pointer_location", "0"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print("✓ Pointer Location DESATIVADO")
                return True
            else:
                print(f"✗ Falha ao desativar: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao desativar pointer_location: {e}")
            return False
    
    def move_joystick(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 4000, direction: str = "") -> bool:
        """
        Move o joystick de uma posição para outra
        
        Args:
            start_x: Coordenada X inicial do joystick (centro)
            start_y: Coordenada Y inicial do joystick (centro)
            end_x: Coordenada X final do joystick
            end_y: Coordenada Y final do joystick
            duration: Duração do movimento em milissegundos (padrão: 4000ms = 4s)
            direction: Nome da direção para exibição (opcional)
            
        Returns:
            True se o movimento foi executado com sucesso
        """
        if not self.connected:
            print("✗ Dispositivo não conectado")
            return False
        
        try:
            direction_text = f" ({direction})" if direction else ""
            print(f"🕹️  Movendo joystick{direction_text} por {duration/1000}s...")
            result = subprocess.run(
                ["adb", "-s", self.device_address, "shell", "input", "swipe", 
                 str(start_x), str(start_y), str(end_x), str(end_y), str(duration)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✓ Joystick movido com sucesso")
                return True
            else:
                print(f"✗ Erro ao mover joystick: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao executar movimento: {e}")
            return False
    
    def move_joystick_forward(self, start_x: int, start_y: int, end_x: int = None, end_y: int = None, duration: int = 4000) -> bool:
        """
        Move o joystick para frente por um período determinado
        
        Args:
            start_x: Coordenada X inicial do joystick (centro)
            start_y: Coordenada Y inicial do joystick (centro)
            end_x: Coordenada X final do joystick (opcional, usa start_x se não fornecido)
            end_y: Coordenada Y final do joystick (opcional, calcula automaticamente se não fornecido)
            duration: Duração do movimento em milissegundos (padrão: 4000ms = 4s)
            
        Returns:
            True se o movimento foi executado com sucesso
        """
        if not self.connected:
            print("✗ Dispositivo não conectado")
            return False
        
        # Usa coordenadas fornecidas ou calcula a posição final
        if end_x is None:
            end_x = start_x
        if end_y is None:
            end_y = start_y - 150  # Move 150 pixels para cima por padrão
        
        return self.move_joystick(start_x, start_y, end_x, end_y, duration, "frente")
    
    def lure_with_joystick(self, joystick_config: dict, duration: int = 4000, interval: float = 0.5) -> bool:
        """
        Executa sequência de movimentos para Lure: frente -> esquerda -> trás -> direita
        
        Args:
            joystick_config: Dicionário com configurações do joystick
            duration: Duração de cada movimento em milissegundos (padrão: 4000ms = 4s)
            interval: Intervalo entre movimentos em segundos (padrão: 0.5s)
            
        Returns:
            True se todos os movimentos foram executados com sucesso
        """
        if not self.connected:
            print("✗ Dispositivo não conectado")
            return False
        
        center_x = joystick_config.get('center_x', 248)
        center_y = joystick_config.get('center_y', 789)
        duration = joystick_config.get('duration', duration)  # Usa do config ou mantém padrão
        
        forward = joystick_config.get('forward', {})
        left = joystick_config.get('left', {})
        backward = joystick_config.get('backward', {})
        right = joystick_config.get('right', {})
        
        print("\n🎯 Iniciando sequência Lure com Joystick...")
        print(f"   Duração de cada movimento: {duration/1000}s\n")
        
        success = True
        
        # 1. Mover para frente
        if not self.move_joystick(center_x, center_y, forward.get('x', 246), forward.get('y', 697), duration, "frente"):
            success = False
        time.sleep(interval)
        
        # 2. Mover para esquerda
        if not self.move_joystick(center_x, center_y, left.get('x', 334), left.get('y', 787), duration, "esquerda"):
            success = False
        time.sleep(interval)
        
        # 3. Mover para trás
        if not self.move_joystick(center_x, center_y, backward.get('x', 243), backward.get('y', 869), duration, "trás"):
            success = False
        time.sleep(interval)
        
        # 4. Mover para direita
        if not self.move_joystick(center_x, center_y, right.get('x', 162), right.get('y', 787), duration, "direita"):
            success = False
        
        if success:
            print("\n✓ Sequência Lure completada!")
        else:
            print("\n⚠ Sequência Lure completada com alguns erros")
        
        return success
    
    def lure_with_joystick_steps(self, joystick_config: dict, step_duration: int = 500, step_interval: float = 0.3, steps_per_direction: int = 8) -> bool:
        """
        Executa sequência de movimentos para Lure com passos intervalados: frente -> esquerda -> trás -> direita
        Cria efeito de caminhada com pausas entre os passos
        
        Args:
            joystick_config: Dicionário com configurações do joystick
            step_duration: Duração de cada passo em milissegundos (padrão: 500ms)
            step_interval: Intervalo entre passos em segundos (padrão: 0.3s)
            steps_per_direction: Quantidade de passos por direção (padrão: 8)
            
        Returns:
            True se todos os movimentos foram executados com sucesso
        """
        if not self.connected:
            print("✗ Dispositivo não conectado")
            return False
        
        center_x = joystick_config.get('center_x', 248)
        center_y = joystick_config.get('center_y', 789)
        
        # Lê configurações do JSON ou usa padrões
        step_duration = joystick_config.get('step_duration', step_duration)
        step_interval = joystick_config.get('step_interval', step_interval)
        steps_per_direction = joystick_config.get('steps_per_direction', steps_per_direction)
        
        forward = joystick_config.get('forward', {})
        left = joystick_config.get('left', {})
        backward = joystick_config.get('backward', {})
        right = joystick_config.get('right', {})
        
        print("\n🎯 Iniciando sequência Lure com passos intervalados...")
        print(f"   Duração do passo: {step_duration}ms | Intervalo: {step_interval}s | Passos/direção: {steps_per_direction}\n")
        
        success = True
        directions = [
            ("frente", forward.get('x', 246), forward.get('y', 697)),
            ("esquerda", left.get('x', 334), left.get('y', 787)),
            ("trás", backward.get('x', 243), backward.get('y', 869)),
            ("direita", right.get('x', 162), right.get('y', 787))
        ]
        
        for direction_name, end_x, end_y in directions:
            print(f"➜ Caminhando para {direction_name}...")
            for step in range(steps_per_direction):
                if not self.move_joystick(center_x, center_y, end_x, end_y, step_duration, f"{direction_name} (passo {step+1}/{steps_per_direction})"):
                    success = False
                if step < steps_per_direction - 1:  # Não espera após o último passo
                    time.sleep(step_interval)
            time.sleep(0.5)  # Pausa entre mudanças de direção
        
        if success:
            print("\n✓ Sequência Lure com passos completada!")
        else:
            print("\n⚠ Sequência Lure com passos completada com alguns erros")
        
        return success


def load_config(config_file: str = "bot_config.json") -> dict:
    """
    Carrega configurações do arquivo JSON
    
    Args:
        config_file: Caminho do arquivo de configuração
        
    Returns:
        Dicionário com as configurações
    """
    if not os.path.exists(config_file):
        print(f"✗ Arquivo {config_file} não encontrado!")
        print(f"  Criando arquivo de exemplo...")
        
        default_config = {
            "device": "192.168.240.112:5555",
            "camera_reset": {
                "enabled": True,
                "x": 67,
                "y": 146,
                "interval": 8.0,
                "description": "Resetar Camera"
            },
            "clicks": [
                {"x": 500, "y": 800, "interval": 2.0, "description": "Botão principal"},
                {"x": 600, "y": 900, "interval": 1.5, "description": "Botão secundário"}
            ]
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Arquivo {config_file} criado com configurações padrão")
        return default_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✓ Configurações carregadas de {config_file}")
        return config
    except Exception as e:
        print(f"✗ Erro ao carregar configurações: {e}")
        sys.exit(1)


def main():
    """Função principal com exemplo de uso"""
    
    # Carrega configurações do JSON
    config = load_config()
    
    DEVICE = config.get("device", "192.168.240.112:5555")
    CLICKS = config.get("clicks", [])
    CAMERA_RESET = config.get("camera_reset", {})
    LURE = config.get("lure", {})
    
    # Inicializa o bot
    bot = SimpleBotADB(device_address=DEVICE)
    
    # Verifica ADB
    if not bot.check_adb():
        sys.exit(1)
    
    # Conecta ao dispositivo
    if not bot.connect():
        sys.exit(1)
    
    print("\n" + "="*50)
    print("BOT SIMPLES ADB - MENU")
    print("="*50)
    print("1 - Iniciar Bot (cliques automáticos)")
    print("2 - Ativar Pointer Location (mostrar coordenadas)")
    print("3 - Desativar Pointer Location")
    print("4 - Habilitar/Desabilitar Lure")
    print("5 - Lure com Joystick (frente -> esquerda -> trás e direita)")
    print("6 - Sair")
    print("="*50)
    print(f"\n⚙️  Configuração atual:")
    print(f"   Dispositivo: {DEVICE}")
    print(f"   Pontos de clique: {len(CLICKS)}")
    
    # Mostra configuração de reset de câmera
    if CAMERA_RESET.get('enabled'):
        cam_x = CAMERA_RESET.get('x')
        cam_y = CAMERA_RESET.get('y')
        cam_interval = CAMERA_RESET.get('interval', 8.0)
        print(f"   📷 Camera Reset: ({cam_x}, {cam_y}) a cada {cam_interval}s [PARALELO]")
    
    # Mostra configuração do Lure
    if LURE.get('enabled'):
        lure_x = LURE.get('x')
        lure_y = LURE.get('y')
        lure_interval = LURE.get('interval', 3.0)
        print(f"   🎯 Lure: ({lure_x}, {lure_y}) a cada {lure_interval}s [PARALELO - ATIVO]")
    else:
        print(f"   🎯 Lure: [DESATIVADO]")
    
    if CLICKS:
        print(f"\n📍 Sequência de cliques:")
        for i, click in enumerate(CLICKS, 1):
            desc = click.get('description', 'Sem descrição')
            interval = click.get('interval', 1.0)
            print(f"   {i}. ({click['x']}, {click['y']}) - {desc} [{interval}s]")
    
    try:
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            if not CLICKS:
                print("✗ Nenhum ponto de clique configurado no bot_config.json!")
                return
            
            print(f"\n🤖 Iniciando bot...")
            print(f"   Clicando em {len(CLICKS)} posições com intervalos individuais")
            
            # Flag de controle para parar as threads
            stop_flag = threading.Event()
            
            # Thread para resetar câmera em paralelo
            camera_thread = None
            if CAMERA_RESET.get('enabled'):
                cam_x = CAMERA_RESET.get('x')
                cam_y = CAMERA_RESET.get('y')
                cam_interval = CAMERA_RESET.get('interval', 8.0)
                
                def camera_reset_loop():
                    cam_count = 0
                    while not stop_flag.is_set():
                        if bot.tap(cam_x, cam_y):
                            cam_count += 1
                            print(f"  📷 Camera Reset #{cam_count}")
                        time.sleep(cam_interval)
                
                camera_thread = threading.Thread(target=camera_reset_loop, daemon=True)
                camera_thread.start()
                print(f"   📷 Camera Reset ativado (paralelo a cada {cam_interval}s)")
            
            # Thread para Lure em paralelo
            lure_thread = None
            if LURE.get('enabled'):
                lure_x = LURE.get('x')
                lure_y = LURE.get('y')
                lure_interval = LURE.get('interval', 3.0)
                
                def lure_loop():
                    lure_count = 0
                    while not stop_flag.is_set():
                        if bot.tap(lure_x, lure_y):
                            lure_count += 1
                            print(f"  🎯 Lure #{lure_count}")
                        time.sleep(lure_interval)
                
                lure_thread = threading.Thread(target=lure_loop, daemon=True)
                lure_thread.start()
                print(f"   🎯 Lure ativado (paralelo a cada {lure_interval}s)")
            
            print(f"   Pressione Ctrl+C para parar\n")
            
            # Executa sequência infinita de cliques principais
            click_count = 0
            try:
                while True:
                    for i, click in enumerate(CLICKS, 1):
                        x = click['x']
                        y = click['y']
                        interval = click.get('interval', 1.0)
                        desc = click.get('description', '')
                        
                        if bot.tap(x, y):
                            click_count += 1
                            print(f"  ✓ Clique #{click_count} em ({x}, {y}) - {desc}")
                        else:
                            print(f"  ✗ Falha no clique em ({x}, {y})")
                        
                        # Aguarda o intervalo específico deste clique
                        time.sleep(interval)
                    
            except KeyboardInterrupt:
                print(f"\n\n⏹ Bot parado após {click_count} cliques")
                stop_flag.set()  # Para as threads
                if camera_thread:
                    camera_thread.join(timeout=1)
                if lure_thread:
                    lure_thread.join(timeout=1)
            
        elif opcao == "2":
            bot.enable_pointer_location()
            
        elif opcao == "3":
            bot.disable_pointer_location()
            
        elif opcao == "4":
            # Alterna estado do Lure
            config = load_config()
            lure_config = config.get("lure", {})
            current_state = lure_config.get('enabled', False)
            lure_config['enabled'] = not current_state
            config['lure'] = lure_config
            
            # Salva no arquivo
            try:
                with open('bot_config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                if lure_config['enabled']:
                    print(f"✓ Lure HABILITADO - será ativado na próxima execução do bot")
                else:
                    print(f"✓ Lure DESABILITADO")
            except Exception as e:
                print(f"✗ Erro ao salvar configuração: {e}")
            
        elif opcao == "5":
            # Executa sequência de Lure com movimentos do joystick em loop COM INTERVALOS
            config = load_config()
            joystick_config = config.get("joystick", {})
            
            if not joystick_config:
                print("\n⚙️  Configuração do joystick não encontrada.")
                print("   Usando coordenadas padrão do bot_config.json")
                # Cria config padrão
                joystick_config = {
                    'center_x': 248,
                    'center_y': 789,
                    'forward': {'x': 246, 'y': 697},
                    'left': {'x': 334, 'y': 787},
                    'backward': {'x': 243, 'y': 869},
                    'right': {'x': 162, 'y': 787}
                }
            
            print("\n🔄 Iniciando Lure com Joystick (PASSOS INTERVALADOS)...")
            print("   Fazendo trajeto quadrado com pausas no caminhar")
            print("   Pressione Ctrl+C para parar\n")
            
            cycle_interval = joystick_config.get('cycle_interval', 10)  # Lê do JSON ou usa padrão
            
            cycle_count = 0
            try:
                while True:
                    cycle_count += 1
                    print(f"--- Ciclo #{cycle_count} ---")
                    bot.lure_with_joystick_steps(joystick_config)
                    print(f"\n⏳ Aguardando {cycle_interval} segundos até próximo ciclo...\n")
                    time.sleep(cycle_interval)
                    
            except KeyboardInterrupt:
                print(f"\n\n⏹ Loop parado após {cycle_count} ciclos")
            
        elif opcao == "6":
            print("Saindo...")
        else:
            print("Opção inválida!")
            
    except ValueError:
        print("✗ Entrada inválida!")
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
    finally:
        bot.disconnect()


if __name__ == "__main__":
    main()
