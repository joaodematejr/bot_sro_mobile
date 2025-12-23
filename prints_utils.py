import os
from datetime import datetime

def tirar_print(adb, config=None, pasta="prints"):
    """Tira screenshot do dispositivo, salva em pasta e mantém só N fotos (configurável)"""
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    nome_arquivo = datetime.now().strftime("print_%Y%m%d_%H%M%S.png")
    caminho_arquivo = os.path.join(pasta, nome_arquivo)
    sucesso = adb.screenshot(caminho_arquivo)
    if not sucesso:
        print(f"✗ Falha ao tirar screenshot!")
    max_prints = 10
    if config is not None:
        max_prints = config.get("max_prints", config.get("max_imagens_treino", 10))
    arquivos = sorted([f for f in os.listdir(pasta) if f.endswith('.png')], key=lambda x: os.path.getctime(os.path.join(pasta, x)))
    while len(arquivos) > max_prints:
        arquivo_remover = arquivos.pop(0)
        try:
            os.remove(os.path.join(pasta, arquivo_remover))
        except Exception as e:
            print(f"✗ Erro ao remover {arquivo_remover}: {e}")

    # --- NOVO: Salvar print também na estrutura de dataset YOLO ---
    import shutil
    dataset_dir = 'dataset_yolo/images/train'
    os.makedirs(dataset_dir, exist_ok=True)
    destino = os.path.join(dataset_dir, nome_arquivo)
    shutil.copy2(caminho_arquivo, destino)
    # Cria arquivo de anotação vazio (para anotar depois)
    labels_dir = 'dataset_yolo/labels/train'
    os.makedirs(labels_dir, exist_ok=True)
    label_path = os.path.join(labels_dir, nome_arquivo.replace('.png', '.txt'))
    if not os.path.exists(label_path):
        with open(label_path, 'w') as f:
            pass  # arquivo vazio, pronto para anotar
    print(f"Print também salvo para dataset YOLO em {destino}")

def rotacionar_prints_yolo(max_prints=50, pasta='print_yolo'):
    """Mantém apenas os max_prints arquivos mais recentes em print_yolo."""
    if not os.path.exists(pasta):
        return
    arquivos = sorted([f for f in os.listdir(pasta) if f.endswith('.png')], key=lambda x: os.path.getctime(os.path.join(pasta, x)))
    while len(arquivos) > max_prints:
        arquivo_remover = arquivos.pop(0)
        try:
            os.remove(os.path.join(pasta, arquivo_remover))
            print(f"Removido {arquivo_remover} de {pasta}")
        except Exception as e:
            print(f"✗ Erro ao remover {arquivo_remover} de {pasta}: {e}")
