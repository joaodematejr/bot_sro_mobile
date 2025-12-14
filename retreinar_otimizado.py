#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-treina modelos com configuração otimizada
Baseado na análise de diversidade
"""

import json
import pickle
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime

def retreinar_com_config_otimizada():
    """Re-treina modelos com número ideal de clusters"""
    
    print("\n" + "="*70)
    print("🔄 RE-TREINAMENTO OTIMIZADO")
    print("="*70)
    
    # Carrega dados
    data_path = Path("ml_models/training_data.json")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    # Prepara features
    X = []
    y = []
    
    for sample in samples:
        features = [
            sample.get('hour', 0),
            sample.get('minute', 0),
            sample.get('pos_x', 0),
            sample.get('pos_y', 0),
            sample.get('sector_N', 0),
            sample.get('sector_E', 0),
            sample.get('sector_S', 0),
            sample.get('sector_W', 0),
            sample.get('enemy_count', 0),
        ]
        X.append(features)
        
        enemy_count = sample.get('enemy_count', 0)
        if enemy_count == 0:
            label = 0
        elif enemy_count <= 2:
            label = 1
        else:
            label = 2
        
        y.append(label)
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"\n📊 Dados carregados: {len(X)} amostras")
    
    # Normalização
    print("\n🔧 Normalizando dados...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Número otimizado de clusters baseado na análise
    # 2228 padrões únicos → 5-7 clusters é ideal
    n_clusters_otimo = 7
    
    print(f"\n🎯 Configuração otimizada:")
    print(f"   Clusters: {n_clusters_otimo} (era 3)")
    print(f"   RandomForest: 200 estimadores")
    print(f"   Max depth: 15")
    
    # Treina KMeans otimizado
    print("\n🧠 Treinando KMeans...")
    start_time = datetime.now()
    
    kmeans = KMeans(
        n_clusters=n_clusters_otimo,
        random_state=42,
        n_init=10,
        max_iter=300
    )
    kmeans.fit(X_scaled)
    
    kmeans_time = (datetime.now() - start_time).total_seconds()
    print(f"   ✅ Concluído em {kmeans_time:.2f}s")
    print(f"   Inércia: {kmeans.inertia_:.2f}")
    
    # Treina RandomForest otimizado
    print("\n🌲 Treinando RandomForest...")
    start_time = datetime.now()
    
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X, y)
    
    rf_time = (datetime.now() - start_time).total_seconds()
    accuracy = rf.score(X, y)
    
    print(f"   ✅ Concluído em {rf_time:.2f}s")
    print(f"   Acurácia: {accuracy*100:.1f}%")
    
    # Importância das features
    print("\n📊 Importância das Features:")
    feature_names = ['hour', 'minute', 'pos_x', 'pos_y', 'sector_N', 
                     'sector_E', 'sector_S', 'sector_W', 'enemy_count']
    
    importances = sorted(
        zip(feature_names, rf.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    
    for name, importance in importances[:5]:
        bar = "█" * int(importance * 50)
        print(f"   {name:12s}: {importance:.3f} {bar}")
    
    # Salva modelos otimizados
    print("\n💾 Salvando modelos...")
    
    models_dir = Path("ml_models")
    
    # KMeans otimizado
    with open(models_dir / "modelo_ultra.pkl", 'wb') as f:
        pickle.dump(kmeans, f)
    
    # RandomForest otimizado
    with open(models_dir / "modelo_sklearn.pkl", 'wb') as f:
        pickle.dump(rf, f)
    
    # Scaler
    with open(models_dir / "scaler.pkl", 'wb') as f:
        pickle.dump(scaler, f)
    
    # Modelo completo (para backup)
    modelo_completo = {
        'kmeans': kmeans,
        'random_forest': rf,
        'scaler': scaler,
        'feature_names': feature_names,
        'n_clusters': n_clusters_otimo,
        'trained_at': datetime.now().isoformat(),
        'accuracy': accuracy,
        'n_samples': len(X)
    }
    
    with open(models_dir / "modelo_ultra_adb.pkl", 'wb') as f:
        pickle.dump(modelo_completo, f)
    
    print("   ✅ Modelos salvos!")
    
    # Análise de clusters
    print("\n🎯 DISTRIBUIÇÃO POR CLUSTER:")
    
    clusters = kmeans.predict(X_scaled)
    from collections import Counter
    
    cluster_counts = Counter(clusters)
    
    for cluster_id in sorted(cluster_counts.keys()):
        count = cluster_counts[cluster_id]
        pct = (count / len(X)) * 100
        bar = "█" * int(pct / 2)
        print(f"   Cluster {cluster_id}: {count:4d} ({pct:5.1f}%) {bar}")
    
    print("\n" + "="*70)
    print("✅ RE-TREINAMENTO CONCLUÍDO!")
    print("="*70)
    print(f"\n📊 Resumo:")
    print(f"   Amostras: {len(X)}")
    print(f"   Clusters: {n_clusters_otimo} (otimizado)")
    print(f"   Acurácia RF: {accuracy*100:.1f}%")
    print(f"   Tempo total: {kmeans_time + rf_time:.2f}s")
    print(f"\n✅ Modelos prontos para uso!")
    print("   Execute o bot normalmente: python3 main.py")
    print("\n" + "="*70)


if __name__ == "__main__":
    retreinar_com_config_otimizada()
