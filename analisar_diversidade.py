#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisa diversidade das amostras ML
Identifica se dados são muito similares
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter

def analisar_diversidade():
    """Analisa diversidade das amostras coletadas"""
    
    data_path = Path("ml_models/training_data.json")
    
    if not data_path.exists():
        print("❌ Dados de treino não encontrados!")
        print("   Execute o bot primeiro para coletar amostras")
        return
    
    # Carrega dados JSON
    with open(data_path, 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    if not samples or len(samples) == 0:
        print("❌ Nenhuma amostra encontrada!")
        return
    
    # Converte para arrays numpy
    X = []
    y = []
    
    for sample in samples:
        # Features baseadas na estrutura real
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
        
        # Label baseado na contagem de inimigos (proxy para ação)
        enemy_count = sample.get('enemy_count', 0)
        if enemy_count == 0:
            label = 0  # Explorar
        elif enemy_count <= 2:
            label = 1  # Combate único
        else:
            label = 2  # AOE/Multi-target
        
        y.append(label)
    
    X = np.array(X)
    y = np.array(y)
    
    print("\n" + "="*70)
    print("📊 ANÁLISE DE DIVERSIDADE DOS DADOS ML")
    print("="*70)
    
    print(f"\n📈 Total de amostras: {len(X)}")
    print(f"   Features por amostra: {X.shape[1]}")
    
    # Análise de labels
    print("\n🏷️  DISTRIBUIÇÃO DE LABELS:")
    label_counts = Counter(y)
    for label, count in sorted(label_counts.items()):
        pct = (count / len(y)) * 100
        bar = "█" * int(pct / 2)
        print(f"   Classe {label}: {count:4d} ({pct:5.1f}%) {bar}")
    
    # Análise de unicidade
    print("\n🔍 ANÁLISE DE UNICIDADE:")
    
    # Amostras únicas
    X_unique = np.unique(X, axis=0)
    pct_unique = (len(X_unique) / len(X)) * 100
    
    print(f"   Amostras únicas: {len(X_unique)} de {len(X)} ({pct_unique:.1f}%)")
    
    if pct_unique < 50:
        print("   ⚠️  MUITAS DUPLICADAS! Dados repetitivos!")
    elif pct_unique < 80:
        print("   ⚠️  Diversidade moderada. Pode melhorar.")
    else:
        print("   ✅ Boa diversidade!")
    
    # Análise de variância
    print("\n📊 VARIÂNCIA DAS FEATURES:")
    
    variances = np.var(X, axis=0)
    mean_var = np.mean(variances)
    
    print(f"   Variância média: {mean_var:.4f}")
    
    # Features com baixa variância (pouco úteis)
    low_var_features = np.sum(variances < 0.01)
    pct_low_var = (low_var_features / len(variances)) * 100
    
    print(f"   Features com baixa variância: {low_var_features} ({pct_low_var:.1f}%)")
    
    if pct_low_var > 30:
        print("   ⚠️  Muitas features não variam!")
    
    # Análise de correlação entre amostras
    print("\n🔗 ANÁLISE DE SIMILARIDADE:")
    
    # Pega 1000 amostras aleatórias para análise
    sample_size = min(1000, len(X))
    indices = np.random.choice(len(X), sample_size, replace=False)
    X_sample = X[indices]
    
    # Calcula distâncias médias
    distances = []
    for i in range(min(100, len(X_sample))):
        for j in range(i+1, min(i+10, len(X_sample))):
            dist = np.linalg.norm(X_sample[i] - X_sample[j])
            distances.append(dist)
    
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    
    print(f"   Distância média entre amostras: {mean_dist:.4f}")
    print(f"   Desvio padrão: {std_dist:.4f}")
    
    if mean_dist < 1.0:
        print("   ⚠️  Amostras muito SIMILARES!")
        print("   Sugestão: Farmar em áreas/condições diferentes")
    elif mean_dist < 5.0:
        print("   ⚠️  Similaridade moderada")
    else:
        print("   ✅ Boa variação entre amostras!")
    
    # Recomendações
    print("\n" + "="*70)
    print("💡 RECOMENDAÇÕES:")
    print("="*70)
    
    problemas = []
    
    if pct_unique < 50:
        problemas.append("duplicatas")
        print("\n1. 🔄 REDUZIR DUPLICATAS:")
        print("   • Farmar em áreas diferentes")
        print("   • Variar horários (manhã/tarde/noite)")
        print("   • Testar diferentes estratégias de combate")
    
    if pct_low_var > 30:
        problemas.append("features constantes")
        print("\n2. 📊 AUMENTAR VARIAÇÃO:")
        print("   • Usar diferentes skills")
        print("   • Alterar padrões de movimento")
        print("   • Farmar mobs de diferentes níveis")
    
    if mean_dist < 1.0:
        problemas.append("amostras similares")
        print("\n3. 🎯 DIVERSIFICAR FARMING:")
        print("   • Alternar entre 3+ áreas diferentes")
        print("   • Testar solo vs party")
        print("   • Variar targets (single vs AOE)")
    
    if not problemas:
        print("\n✅ DADOS COM BOA QUALIDADE!")
        print("   Continue coletando em diferentes condições")
    
    # Análise de clusters recomendados
    print("\n" + "="*70)
    print("🎯 NÚMERO IDEAL DE CLUSTERS:")
    print("="*70)
    
    n_unique_patterns = len(X_unique)
    
    if n_unique_patterns < 10:
        print(f"   Recomendado: 2 clusters (apenas {n_unique_patterns} padrões únicos)")
        print("   ⚠️  Precisa coletar dados mais variados!")
    elif n_unique_patterns < 50:
        print(f"   Recomendado: 2-3 clusters ({n_unique_patterns} padrões únicos)")
    elif n_unique_patterns < 200:
        print(f"   Recomendado: 3-5 clusters ({n_unique_patterns} padrões únicos)")
    else:
        print(f"   Recomendado: 5-10 clusters ({n_unique_patterns} padrões únicos)")
        print("   ✅ Dados diversificados!")
    
    print("\n" + "="*70)
    
    # Retorna métricas
    return {
        'total_samples': len(X),
        'unique_samples': len(X_unique),
        'pct_unique': pct_unique,
        'mean_variance': mean_var,
        'mean_distance': mean_dist,
        'recommended_clusters': min(3, max(2, n_unique_patterns // 50))
    }


def sugerir_plano_coleta():
    """Sugere plano para coletar dados mais diversos"""
    
    print("\n" + "="*70)
    print("📋 PLANO DE COLETA DIVERSIFICADA")
    print("="*70)
    
    print("\n🎯 OBJETIVO: Coletar 1.000 amostras VARIADAS")
    print("\n📅 ROTEIRO (4 sessões de 1h):\n")
    
    print("SESSÃO 1 - Área Principal (30min)")
    print("  • Sua área atual de farming")
    print("  • Meta: 200 amostras")
    print("  • Foco: Estabelecer baseline\n")
    
    print("SESSÃO 2 - Área Alternativa 1 (30min)")
    print("  • Mobs diferentes (outro nível/tipo)")
    print("  • Meta: 200 amostras")
    print("  • Foco: Diversidade de combate\n")
    
    print("SESSÃO 3 - Área Alternativa 2 (30min)")
    print("  • Terreno diferente (cave/outdoor/dungeon)")
    print("  • Meta: 200 amostras")
    print("  • Foco: Variação de ambiente\n")
    
    print("SESSÃO 4 - Mix Estratégias (30min)")
    print("  • Alterna entre todas as áreas")
    print("  • Meta: 400 amostras")
    print("  • Foco: Adaptabilidade\n")
    
    print("✅ RESULTADO ESPERADO:")
    print("  • 1.000 amostras diversificadas")
    print("  • 3-5 padrões distintos")
    print("  • ML aprende diferentes contextos")
    print("  • Performance > 120% bot nativo")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    metricas = analisar_diversidade()
    
    if metricas and metricas['pct_unique'] < 70:
        print("\n")
        sugerir_plano_coleta()
