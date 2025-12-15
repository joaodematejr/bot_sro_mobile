#!/usr/bin/env python3
"""
Análise completa dos dados de treino para sugerir melhorias no farming
"""
import os
import json
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

print("🔍 ANÁLISE COMPLETA DOS DADOS DE TREINO")
print("="*80)

# Pastas de treino
pastas_treino = [
    "treino_ml",
    "exp_ganho_treino",
    "minimap_captures",
    "debug_deteccao"
]

# Estatísticas gerais
total_imagens = 0
stats_por_pasta = {}

print("\n📊 COLETANDO DADOS DAS PASTAS DE TREINO...\n")

for pasta in pastas_treino:
    if not os.path.exists(pasta):
        continue
    
    arquivos = [f for f in os.listdir(pasta) if f.endswith('.png')]
    total = len(arquivos)
    total_imagens += total
    
    if total == 0:
        continue
    
    # Analisa timestamps
    timestamps = []
    for arquivo in arquivos:
        try:
            # Extrai timestamp do nome do arquivo
            if '_' in arquivo:
                ts_str = arquivo.split('_')[-1].replace('.png', '')
                if ts_str.isdigit() and len(ts_str) >= 8:
                    timestamp = datetime.strptime(ts_str[:14] if len(ts_str) >= 14 else ts_str[:8], 
                                                 '%Y%m%d%H%M%S' if len(ts_str) >= 14 else '%Y%m%d')
                    timestamps.append(timestamp)
        except:
            pass
    
    stats_por_pasta[pasta] = {
        'total': total,
        'timestamps': timestamps
    }
    
    print(f"📁 {pasta:25s}: {total:4d} imagens")

print(f"\n{'='*80}")
print(f"📊 TOTAL DE IMAGENS COLETADAS: {total_imagens}")
print(f"{'='*80}")

# Análise de EXP ganho
print("\n💰 ANÁLISE DE EXP GANHO (exp_ganho_treino)")
print("-"*80)

if 'exp_ganho_treino' in stats_por_pasta:
    exp_pasta = 'exp_ganho_treino'
    total_exp = stats_por_pasta[exp_pasta]['total']
    
    print(f"Total de capturas: {total_exp}")
    
    if total_exp > 0:
        # Calcula intervalo médio entre capturas
        timestamps = sorted(stats_por_pasta[exp_pasta]['timestamps'])
        if len(timestamps) > 1:
            intervalos = []
            for i in range(1, len(timestamps)):
                diff = (timestamps[i] - timestamps[i-1]).total_seconds()
                if diff > 0 and diff < 300:  # Ignora intervalos > 5min
                    intervalos.append(diff)
            
            if intervalos:
                media_intervalo = np.mean(intervalos)
                print(f"Intervalo médio entre kills: {media_intervalo:.1f}s")
                
                # Estima kills por hora
                if media_intervalo > 0:
                    kills_por_hora = 3600 / media_intervalo
                    print(f"📈 Estimativa: {kills_por_hora:.1f} kills/hora")
                    
                    # Análise de eficiência
                    if kills_por_hora < 100:
                        print(f"⚠️  EFICIÊNCIA BAIXA - Você está matando poucos mobs")
                        print(f"   Sugestões:")
                        print(f"   • Reduza intervalo de target (está em 2s)")
                        print(f"   • Aumente clicks por ciclo (está em 15)")
                        print(f"   • Verifique se está em área com muitos mobs")
                    elif kills_por_hora < 200:
                        print(f"✅ EFICIÊNCIA NORMAL")
                    else:
                        print(f"🚀 EFICIÊNCIA ALTA - Bom farming!")
else:
    print("❌ Nenhuma captura de EXP ganho encontrada")

# Análise do minimapa
print("\n🗺️  ANÁLISE DO MINIMAPA (minimap_captures)")
print("-"*80)

if 'minimap_captures' in stats_por_pasta:
    minimap_pasta = 'minimap_captures'
    total_minimap = stats_por_pasta[minimap_pasta]['total']
    
    print(f"Total de capturas: {total_minimap}")
    
    if total_minimap > 0:
        # Analisa detecções de mobs no minimapa
        mobs_detectados = []
        
        for arquivo in os.listdir(minimap_pasta):
            if not arquivo.endswith('.png'):
                continue
            
            img_path = os.path.join(minimap_pasta, arquivo)
            img = cv2.imread(img_path)
            
            if img is None:
                continue
            
            # Converte para HSV
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Detecta vermelho (mobs)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask_red = cv2.bitwise_or(mask1, mask2)
            
            pixels_vermelho = cv2.countNonZero(mask_red)
            total_pixels = img.shape[0] * img.shape[1]
            percentual = (pixels_vermelho / total_pixels) * 100
            
            mobs_detectados.append(percentual)
        
        if mobs_detectados:
            media_mobs = np.mean(mobs_detectados)
            max_mobs = np.max(mobs_detectados)
            min_mobs = np.min(mobs_detectados)
            
            print(f"Mobs no minimapa (% pixels vermelhos):")
            print(f"  Média: {media_mobs:.2f}%")
            print(f"  Máximo: {max_mobs:.2f}%")
            print(f"  Mínimo: {min_mobs:.2f}%")
            
            if media_mobs < 1:
                print(f"\n⚠️  POUCOS MOBS DETECTADOS")
                print(f"   Sugestões:")
                print(f"   • Mova-se para área com mais densidade de mobs")
                print(f"   • Verifique se está parado no mesmo lugar")
                print(f"   • Considere ativar movimento automático")
            elif media_mobs < 3:
                print(f"\n✅ DENSIDADE NORMAL DE MOBS")
            else:
                print(f"\n🎯 ÁREA COM MUITOS MOBS - Ótimo local!")
else:
    print("❌ Nenhuma captura de minimapa encontrada")

# Análise de treino ML
print("\n🧠 ANÁLISE DE DADOS DE TREINO ML (treino_ml)")
print("-"*80)

if 'treino_ml' in stats_por_pasta:
    ml_pasta = 'treino_ml'
    total_ml = stats_por_pasta[ml_pasta]['total']
    
    print(f"Total de imagens: {total_ml}")
    
    if total_ml >= 50:
        print(f"✅ Dados suficientes para treino ML ({total_ml} >= 50)")
    elif total_ml > 0:
        print(f"⚠️  Poucos dados para treino ML ({total_ml}/50 mínimo)")
        print(f"   Continue farmando para coletar mais amostras")
    
    # Verifica diversidade temporal
    if ml_pasta in stats_por_pasta and stats_por_pasta[ml_pasta]['timestamps']:
        timestamps = stats_por_pasta[ml_pasta]['timestamps']
        if len(timestamps) > 1:
            periodo = (max(timestamps) - min(timestamps)).total_seconds() / 3600
            print(f"Período de coleta: {periodo:.1f} horas")
else:
    print("❌ Nenhum dado de treino ML encontrado")

# Análise de sessões de farming
print("\n⏱️  ANÁLISE DE SESSÕES DE FARMING")
print("-"*80)

todas_timestamps = []
for pasta, stats in stats_por_pasta.items():
    todas_timestamps.extend(stats['timestamps'])

if todas_timestamps:
    todas_timestamps = sorted(todas_timestamps)
    
    # Detecta sessões (gaps > 30min = nova sessão)
    sessoes = []
    sessao_atual = [todas_timestamps[0]]
    
    for i in range(1, len(todas_timestamps)):
        diff = (todas_timestamps[i] - todas_timestamps[i-1]).total_seconds()
        if diff > 1800:  # 30 minutos
            sessoes.append(sessao_atual)
            sessao_atual = [todas_timestamps[i]]
        else:
            sessao_atual.append(todas_timestamps[i])
    
    if sessao_atual:
        sessoes.append(sessao_atual)
    
    print(f"Total de sessões detectadas: {len(sessoes)}")
    
    for i, sessao in enumerate(sessoes, 1):
        duracao = (max(sessao) - min(sessao)).total_seconds() / 60
        inicio = min(sessao).strftime('%d/%m %H:%M')
        fim = max(sessao).strftime('%H:%M')
        print(f"  Sessão {i}: {inicio} - {fim} ({duracao:.0f} min)")

# SUGESTÕES FINAIS
print("\n" + "="*80)
print("💡 SUGESTÕES PARA MELHORAR O XP/HORA")
print("="*80)

sugestoes = []

# Baseado em kills/hora
if 'exp_ganho_treino' in stats_por_pasta and stats_por_pasta['exp_ganho_treino']['total'] > 10:
    timestamps = sorted(stats_por_pasta['exp_ganho_treino']['timestamps'])
    if len(timestamps) > 1:
        intervalos = []
        for i in range(1, len(timestamps)):
            diff = (timestamps[i] - timestamps[i-1]).total_seconds()
            if 0 < diff < 300:
                intervalos.append(diff)
        
        if intervalos:
            media_intervalo = np.mean(intervalos)
            kills_por_hora = 3600 / media_intervalo if media_intervalo > 0 else 0
            
            if kills_por_hora < 100:
                sugestoes.append({
                    'prioridade': '🔴 ALTA',
                    'titulo': 'AUMENTAR VELOCIDADE DE KILL',
                    'acoes': [
                        'Reduza "intervalo_target" de 2s para 1s no config',
                        'Aumente "target_clicks_por_ciclo" de 15 para 20',
                        'Reduza "target_pausa_entre_ciclos" de 15s para 10s',
                        'Verifique se seu personagem tem DPS suficiente'
                    ]
                })

# Baseado em densidade de mobs
if 'minimap_captures' in stats_por_pasta and stats_por_pasta['minimap_captures']['total'] > 10:
    mobs_detectados = []
    for arquivo in os.listdir('minimap_captures'):
        if not arquivo.endswith('.png'):
            continue
        img = cv2.imread(os.path.join('minimap_captures', arquivo))
        if img is None:
            continue
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask1, mask2)
        pixels_vermelho = cv2.countNonZero(mask_red)
        total_pixels = img.shape[0] * img.shape[1]
        mobs_detectados.append((pixels_vermelho / total_pixels) * 100)
    
    if mobs_detectados and np.mean(mobs_detectados) < 1:
        sugestoes.append({
            'prioridade': '🟡 MÉDIA',
            'titulo': 'MUDAR PARA ÁREA COM MAIS MOBS',
            'acoes': [
                'Seu spot atual tem poucos mobs próximos',
                'Procure áreas com maior densidade de inimigos',
                'Evite ficar parado - mobs se esgotam',
                'Considere ativar movimento automático (ainda em desenvolvimento)'
            ]
        })

# Sugestões gerais
sugestoes.append({
    'prioridade': '🟢 BAIXA',
    'titulo': 'OTIMIZAÇÕES GERAIS',
    'acoes': [
        'Use Demon sempre que disponível (agora com detecção automática!)',
        'Mantenha camera resetando regularmente para melhor visão',
        'Farm em horários com menos players (menos competição)',
        'Use buffs/poções de XP se disponível no jogo'
    ]
})

# Imprime sugestões
for i, sug in enumerate(sugestoes, 1):
    print(f"\n{sug['prioridade']} - {sug['titulo']}")
    print("-"*80)
    for acao in sug['acoes']:
        print(f"  • {acao}")

# Configurações recomendadas
print("\n" + "="*80)
print("⚙️  CONFIGURAÇÕES RECOMENDADAS PARA MÁXIMO XP/HORA")
print("="*80)
print("""
{
  "intervalo_reset_camera": 2,           ← Manter
  "intervalo_target": 1,                 ← Reduzir de 2 para 1
  "target_clicks_por_ciclo": 20,         ← Aumentar de 15 para 20
  "target_pausa_entre_ciclos": 10,       ← Reduzir de 15 para 10
  "intervalo_demon": 900,                ← Ignorado (usando detecção visual agora)
  "usar_deteccao_demon": true            ← ✅ Já ativo!
}

EXPLICAÇÃO:
- Mais clicks = mata mais rápido
- Menos pausa = retorna ao combat mais rápido
- Detecção visual Demon = usa skill assim que disponível (não espera 15min)
""")

print("\n" + "="*80)
print("📈 EXPECTATIVA DE MELHORIA")
print("="*80)

# Calcula intervalos para estimativa
intervalos = []
if 'exp_ganho_treino' in stats_por_pasta and stats_por_pasta['exp_ganho_treino']['timestamps']:
    timestamps = sorted(stats_por_pasta['exp_ganho_treino']['timestamps'])
    for i in range(1, len(timestamps)):
        diff = (timestamps[i] - timestamps[i-1]).total_seconds()
        if 0 < diff < 300:
            intervalos.append(diff)

if intervalos and len(intervalos) > 0:
    media_intervalo = np.mean(intervalos)
    atual_kph = 3600 / media_intervalo if media_intervalo > 0 else 0
    
    # Estima melhoria com config otimizado
    # Reduzir intervalo de 2s para 1s + aumentar clicks = ~40% mais rápido
    otimizado_kph = atual_kph * 1.4
    
    print(f"Situação ATUAL:    ~{atual_kph:.0f} kills/hora")
    print(f"Com OTIMIZAÇÕES:   ~{otimizado_kph:.0f} kills/hora (+{((otimizado_kph/atual_kph-1)*100):.0f}%)")
    print(f"\n💰 Assumindo média de 500 XP por kill:")
    print(f"   ATUAL:    {atual_kph * 500:,.0f} XP/hora")
    print(f"   OTIMIZADO: {otimizado_kph * 500:,.0f} XP/hora")
else:
    print("⚠️  Dados insuficientes para estimar melhoria")
    print("   Farm por pelo menos 30 minutos para gerar estatísticas")

print("\n" + "="*80)
print("✅ Análise concluída!")
print("="*80)
