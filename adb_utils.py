import subprocess

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

def clicar_repetidamente(adb, x, y, intervalo):
    import time
    try:
        print(f"Iniciando cliques a cada {intervalo}s em x={x}, y={y}. Pressione Ctrl+C para parar.")
        while True:
            result = subprocess.run([
                "adb", "-s", adb.device_address, "shell", f"input tap {x} {y}"
            ], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"✗ Falha ao clicar: {result.stderr}")
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print("\nParado pelo usuário.")
    except Exception as e:
        print(f"✗ Erro ao clicar repetidamente: {e}")
