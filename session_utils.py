import os
import json
from datetime import datetime

SESSOES_PATH = 'sessoes/'
os.makedirs(SESSOES_PATH, exist_ok=True)

def gerar_session_id():
    import uuid
    return str(uuid.uuid4())

def auto_save_sessao(session_id, dados):
    path = os.path.join(SESSOES_PATH, f'sessao_{session_id}.json')
    with open(path, 'w') as f:
        json.dump(dados, f, indent=2, default=str)

def carregar_historico_sessoes():
    historico = []
    for arquivo in os.listdir(SESSOES_PATH):
        if arquivo.endswith('.json'):
            with open(os.path.join(SESSOES_PATH, arquivo)) as f:
                historico.append(json.load(f))
    return historico

def exportar_json_ultima_sessao(session_id):
    path = os.path.join(SESSOES_PATH, f'sessao_{session_id}.json')
    export_dir = 'sessoes_exports'
    os.makedirs(export_dir, exist_ok=True)
    if os.path.exists(path):
        with open(path) as f:
            dados = json.load(f)
        export_path = os.path.join(export_dir, f'export_sessao_{session_id}.json')
        with open(export_path, 'w') as f:
            json.dump(dados, f, indent=2, default=str)
        print(f"Sessão exportada para {export_path}")
    else:
        print("Nenhuma sessão encontrada para exportar.")
