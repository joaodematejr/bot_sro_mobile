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
