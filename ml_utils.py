import os
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import time as _time

class MonitoramentoTreinamento:
    def __init__(self, milestones=None, historico_path='ml_training_history.json'):
        self.timeline = []
        self.tempo_treinos = []
        self.acuracias = []
        self.milestones = milestones or [10, 50, 100, 200, 500, 1000]
        self.historico_path = historico_path
        self.milestones_atingidos = set()
        self._carregar_historico()

    def registrar_amostra(self, features, target, pred=None):
        if hasattr(features, 'tolist'):
            features = features.tolist()
        if hasattr(pred, 'tolist'):
            pred = pred.tolist()
        amostra = {
            'timestamp': _time.time(),
            'features': features,
            'target': target,
            'pred': pred
        }
        self.timeline.append(amostra)
        self._checar_milestones()
        self._salvar_historico()

    def registrar_treino(self, tempo_treino, acuracia):
        self.tempo_treinos.append(tempo_treino)
        self.acuracias.append(acuracia)
        self._salvar_historico()

    def _checar_milestones(self):
        n = len(self.timeline)
        for m in self.milestones:
            if n == m and m not in self.milestones_atingidos:
                print(f"\n🏆 Milestone atingido: {m} amostras coletadas!")
                self.milestones_atingidos.add(m)

    def plotar_curva_aprendizado(self, path='curva_aprendizado.png'):
        import matplotlib.pyplot as plt
        if not self.acuracias:
            print("Nenhum treino registrado para plotar curva de aprendizado.")
            return
        plt.figure(figsize=(8,4))
        plt.plot(self.acuracias, marker='o')
        plt.title('Curva de Aprendizado (R² Score)')
        plt.xlabel('Treino #')
        plt.ylabel('Acurácia (R²)')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(path)
        print(f"Curva de aprendizado salva em {path}")

    def _salvar_historico(self):
        import json
        dados = {
            'timeline': self.timeline,
            'tempo_treinos': self.tempo_treinos,
            'acuracias': self.acuracias,
            'milestones_atingidos': list(self.milestones_atingidos)
        }
        try:
            with open(self.historico_path, 'w') as f:
                json.dump(dados, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico de treinamento: {e}")

    def _carregar_historico(self):
        import json
        try:
            with open(self.historico_path, 'r') as f:
                dados = json.load(f)
                self.timeline = dados.get('timeline', [])
                self.tempo_treinos = dados.get('tempo_treinos', [])
                self.acuracias = dados.get('acuracias', [])
                self.milestones_atingidos = set(dados.get('milestones_atingidos', []))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Erro ao carregar histórico de treinamento: {e}")

    def resumo(self):
        print("\n===== Monitoramento de Treinamento ML =====")
        print(f"Amostras coletadas: {len(self.timeline)}")
        print(f"Treinos realizados: {len(self.acuracias)}")
        if self.acuracias:
            print(f"Última acurácia (R²): {self.acuracias[-1]:.4f}")
        if self.tempo_treinos:
            print(f"Último tempo de treino: {self.tempo_treinos[-1]:.2f}s")
        print(f"Milestones atingidos: {sorted(self.milestones_atingidos)}")
        print("==========================================\n")

MODELOS_PATHS = {
    'sklearn': 'model_sklearn.pkl',
    'ultra': 'model_ultra.pkl',
    'ultra_adb': 'model_ultra_adb.pkl',
    'avancado': 'model_avancado.pkl',
}

def carregar_modelos():
    modelos = {}
    for nome, path in MODELOS_PATHS.items():
        if os.path.exists(path):
            modelos[nome] = joblib.load(path)
        else:
            modelos[nome] = RandomForestRegressor(n_estimators=100)
    return modelos

scaler = StandardScaler()

def auto_treinar_modelos(modelos, X, y, contador_amostras, batch=100):
    if contador_amostras % batch == 0 and contador_amostras > 0:
        print(f"[ML] Treinando todos os modelos com {contador_amostras} amostras...")
        for nome, modelo in modelos.items():
            t0 = _time.time()
            modelo.fit(X, y)
            tempo_treino = _time.time() - t0
            try:
                score = modelo.score(X, y)
            except Exception:
                score = None
            # monitoramento_ml.registrar_treino(tempo_treino, score)  # Passe o monitoramento como argumento se necessário
            joblib.dump(modelo, MODELOS_PATHS[nome])
            print(f"[ML] Modelo '{nome}' salvo em {MODELOS_PATHS[nome]}")
            if score is not None:
                print(f"[ML] Tempo de treino: {tempo_treino:.2f}s | Acurácia (R²): {score:.4f}")
            else:
                print(f"[ML] Tempo de treino: {tempo_treino:.2f}s")

def identificar_hotspots(X, n_clusters=2):
    with warnings.catch_warnings(record=True) as wlist:
        warnings.simplefilter("always")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)
        for w in wlist:
            if issubclass(w.category, Warning) and 'Number of distinct clusters' in str(w.message):
                print("[ML] Aviso: poucos dados distintos para clustering. Colete mais amostras variadas para melhor análise de hotspots.")
    return clusters, kmeans
