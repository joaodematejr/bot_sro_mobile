#!/usr/bin/env python3
"""
Dashboard Completo - Guia + Dados Reais do ML
Exibe o guia de métricas com dados atualizados em tempo real
"""

import json
import os
from datetime import datetime
import numpy as np

def carregar_dados_ml():
    """Carrega dados do ML se existirem"""
    arquivo = 'ml_avancado_dados.json'
    if not os.path.exists(arquivo):
        return None
    
    try:
        with open(arquivo, 'r') as f:
            return json.load(f)
    except:
        return None

def calcular_metricas(dados):
    """Calcula todas as métricas"""
    if not dados:
        return None
    
    metricas = {}
    
    # Rotas
    rotas = dados.get('historico_rotas', [])
    metricas['total_rotas'] = len(rotas)
    metricas['confianca'] = min(100, (len(rotas) / 200) * 100)
    
    # Densidade
    densidade = dados.get('densidade_mobs', {})
    metricas['areas_mapeadas'] = len(densidade)
    metricas['exploracao'] = (len(densidade) / 400) * 100  # 400 áreas possíveis
    
    # EXP
    if rotas:
        exp_mins = [r.get('exp_por_minuto', 0) for r in rotas if r.get('exp_por_minuto', 0) > 0]
        if exp_mins:
            metricas['densidade_media'] = np.mean(exp_mins)
            metricas['densidade_std'] = np.std(exp_mins)
    
    # Melhor área
    if densidade:
        areas_com_densidade = []
        for coord_str, info in densidade.items():
            if info['tempo_total'] > 0:
                dens = (info['exp_total'] / info['tempo_total']) * 60
                coords = tuple(map(int, coord_str.split(',')))
                areas_com_densidade.append({
                    'coords': coords,
                    'densidade': dens,
                    'combates': info['combates']
                })
        
        if areas_com_densidade:
            areas_com_densidade.sort(key=lambda x: x['densidade'], reverse=True)
            metricas['melhor_area'] = areas_com_densidade[0]
            metricas['pior_area'] = areas_com_densidade[-1]
    
    # Skills
    skills = dados.get('historico_skills', {})
    metricas['skills_analisadas'] = len(skills)
    
    if skills:
        skills_eficiencia = []
        for skill_id, registros in skills.items():
            if len(registros) >= 3:
                eficiencias = [r.get('eficiencia', 0) for r in registros]
                skills_eficiencia.append({
                    'skill_id': skill_id,
                    'eficiencia': np.mean(eficiencias),
                    'usos': len(registros)
                })
        
        if skills_eficiencia:
            skills_eficiencia.sort(key=lambda x: x['eficiencia'], reverse=True)
            metricas['melhor_skill'] = skills_eficiencia[0]
    
    # Combos
    combos = dados.get('combos_eficientes', [])
    metricas['combos'] = len(combos)
    
    # Horário
    performance_hora = dados.get('performance_por_hora', {})
    if performance_hora:
        medias_hora = {}
        for hora, valores in performance_hora.items():
            if len(valores) >= 3:
                medias_hora[int(hora)] = np.mean(valores)
        
        if medias_hora:
            melhor_h = max(medias_hora.items(), key=lambda x: x[1])
            metricas['melhor_horario'] = {'hora': melhor_h[0], 'exp_min': melhor_h[1]}
    
    # Ganho ML
    if len(rotas) >= 40:
        primeiros = rotas[:20]
        ultimos = rotas[-20:]
        
        exp_antes = [r.get('exp_por_minuto', 0) for r in primeiros if r.get('exp_por_minuto', 0) > 0]
        exp_depois = [r.get('exp_por_minuto', 0) for r in ultimos if r.get('exp_por_minuto', 0) > 0]
        
        if exp_antes and exp_depois:
            media_antes = np.mean(exp_antes)
            media_depois = np.mean(exp_depois)
            metricas['ganho_ml'] = {
                'antes': media_antes,
                'depois': media_depois,
                'ganho_abs': media_depois - media_antes,
                'ganho_pct': ((media_depois - media_antes) / media_antes) * 100
            }
    
    return metricas

def gerar_barra_progresso(valor, total=100, largura=40):
    """Gera barra de progresso visual"""
    preenchido = int((valor / total) * largura)
    barra = '█' * preenchido + '░' * (largura - preenchido)
    return f"[{barra}] {valor:.1f}%"

def exibir_dashboard():
    """Exibe dashboard completo"""
    dados = carregar_dados_ml()
    metricas = calcular_metricas(dados) if dados else None
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "📊 DASHBOARD ML - DADOS REAIS" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    print(f"\n🕐 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*18 + "🎯 MÉTRICA #1: CONFIANÇA DO MODELO" + " "*17 + "║")
    print("╚" + "="*68 + "╝")
    
    if metricas:
        confianca = metricas.get('confianca', 0)
        barra = gerar_barra_progresso(confianca)
        
        print(f"\n   {barra}")
        print()
        
        if confianca < 30:
            status = "🟥 Aprendendo (colete dados)"
        elif confianca < 60:
            status = "🟨 Funcional (otimizando)"
        elif confianca < 90:
            status = "🟩 Bom (resultados visíveis)"
        else:
            status = "🟦 Excelente (máximo desempenho)"
        
        print(f"   Status: {status}")
        print(f"   Dados coletados: {metricas['total_rotas']} rotas")
    else:
        print("\n   [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.0%")
        print("\n   ⚠️  Sem dados ainda - Execute o bot para começar!")
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*16 + "📈 MÉTRICA #2: GANHO DE PERFORMANCE" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    if metricas and metricas.get('ganho_ml'):
        ganho = metricas['ganho_ml']
        print(f"\n   Antes ML:  {ganho['antes']:,.1f} exp/min")
        print(f"   Depois ML: {ganho['depois']:,.1f} exp/min")
        print(f"   Ganho:     {ganho['ganho_abs']:+,.1f} exp/min ({ganho['ganho_pct']:+.1f}%)", end="")
        
        if ganho['ganho_pct'] > 0:
            print(" ✅")
        else:
            print(" ⚠️")
    else:
        print("\n   Antes ML:  ??? exp/min")
        print("   Depois ML: ??? exp/min")
        print("   Ganho:     Aguardando dados (mín. 40 rotas)")
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*19 + "💡 MÉTRICA #3: COBERTURA DO MAPA" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    if metricas:
        exploracao = metricas.get('exploracao', 0)
        print(f"\n   Exploração: {exploracao:.1f}% do mapa")
        print(f"   Áreas mapeadas: {metricas['areas_mapeadas']}")
        
        if exploracao < 10:
            status = "→ Explore mais áreas"
        elif exploracao < 25:
            status = "→ Cobertura razoável"
        else:
            status = "→ Excelente cobertura"
        
        print(f"   Status: {status}")
    else:
        print("\n   Exploração: 0.0% do mapa")
        print("   Áreas mapeadas: 0")
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*17 + "🗺️  MÉTRICA #4: DENSIDADE DESCOBERTA" + " "*17 + "║")
    print("╚" + "="*68 + "╝")
    
    if metricas and metricas.get('melhor_area'):
        melhor = metricas['melhor_area']
        pior = metricas.get('pior_area')
        
        print(f"\n   Melhor área: ({melhor['coords'][0]}, {melhor['coords'][1]}) - {melhor['densidade']:,.1f} exp/min")
        print(f"               {melhor['combates']} combates realizados")
        
        if pior:
            print(f"\n   Pior área:   ({pior['coords'][0]}, {pior['coords'][1]}) - {pior['densidade']:,.1f} exp/min")
        
        if metricas.get('densidade_std'):
            print(f"\n   Variância: ±{metricas['densidade_std']:.1f} exp/min", end="")
            if metricas['densidade_std'] > 500:
                print(" (alta - ML tem muito a otimizar)")
            else:
                print(" (baixa - áreas similares)")
    else:
        print("\n   Melhor área: Ainda não descoberta")
        print("   Pior área:   Ainda não descoberta")
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*17 + "⚔️  MÉTRICA #5: OTIMIZAÇÃO DE SKILLS" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    if metricas:
        print(f"\n   Skills analisadas: {metricas.get('skills_analisadas', 0)}")
        print(f"   Combos aprendidos: {metricas.get('combos', 0)}")
        
        if metricas.get('melhor_skill'):
            skill = metricas['melhor_skill']
            print(f"\n   Skill mais eficiente: Skill {skill['skill_id']}")
            print(f"   Eficiência: {skill['eficiencia']:.2f}")
            print(f"   Usos: {skill['usos']}")
    else:
        print("\n   Skills analisadas: 0")
        print("   Combos aprendidos: 0")
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*22 + "⏰ MELHOR HORÁRIO" + " "*29 + "║")
    print("╚" + "="*68 + "╝")
    
    if metricas and metricas.get('melhor_horario'):
        hora = metricas['melhor_horario']
        print(f"\n   Horário: {hora['hora']:02d}:00")
        print(f"   Performance: {hora['exp_min']:.1f} exp/min")
    else:
        print("\n   Ainda analisando padrões...")
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*24 + "🚀 COMO USAR" + " "*31 + "║")
    print("╚" + "="*68 + "╝")
    
    print("""
1️⃣  RELATÓRIO DETALHADO

    python3 metricas_aprendizado.py
    Escolha: 1

2️⃣  VISUALIZAÇÃO GRÁFICA (4 gráficos)

    python3 metricas_aprendizado.py
    Escolha: 2

3️⃣  MAPA 3D INTERATIVO

    python3 visualizador_3d_ml.py
    
4️⃣  ESTE DASHBOARD (atualização contínua)

    watch -n 60 python3 dashboard_ml.py
    """)
    
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "💡 RECOMENDAÇÕES ATUAIS" + " "*25 + "║")
    print("╚" + "="*68 + "╝\n")
    
    if not metricas:
        print("   • Inicie o bot: python3 bot_ultra_adb.py")
        print("   • Aguarde coleta de dados (20-30 min)")
    elif metricas['total_rotas'] < 20:
        print("   • Continue farmando para coletar dados iniciais")
        print(f"   • Progresso: {metricas['total_rotas']}/20 rotas")
    elif metricas['total_rotas'] < 50:
        print("   • ML começando a otimizar - Aguarde resultados")
        print("   • Primeiro treinamento em andamento")
    elif metricas.get('exploracao', 0) < 10:
        print("   • Explore mais áreas para melhor cobertura")
        print("   • Varie a região de farming")
    elif metricas.get('exploracao', 0) < 20:
        print("   • Expanda área de farming para mais dados")
    else:
        print("   ✅ Sistema otimizado! Continue farmando")
        if metricas.get('melhor_area'):
            coords = metricas['melhor_area']['coords']
            print(f"   • Área hotspot: ({coords[0]}, {coords[1]})")
            print(f"     {metricas['melhor_area']['densidade']:.1f} exp/min")
    
    print("\n" + "="*70)
    print("Para atualizar: pressione Ctrl+C e execute novamente")
    print("Ou use: watch -n 60 python3 dashboard_ml.py")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        exibir_dashboard()
    except Exception as e:
        print(f"\n⚠️  Erro ao exibir dashboard: {e}")
        print("Verifique se os arquivos de dados existem.\n")
