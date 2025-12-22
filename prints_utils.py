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
