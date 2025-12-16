#!/usr/bin/env python3
"""
Script de teste para popular o dashboard com dados simulados
Execute junto com o dashboard_web.py para ver dados em tempo real
"""

import json
import time
import random
from pathlib import Path
from datetime import datetime, timedelta

def gerar_metricas_simuladas(sessao: int):
    """Gera métricas simuladas de farming"""
    
    # Simula farming com variação realista
    tempo_base = sessao * 300  # 5 minutos por sessão
    
    # Tendência de melhora ao longo do tempo
    fator_melhora = 1 + (sessao * 0.05)
    
    metricas = {
        'timestamp': datetime.now().isoformat(),
        'duracao_total': tempo_base,
        
        # XP
        'xp_total': round(40 + (sessao * 2.5) + random.uniform(-1, 1), 2),
        'xp_por_minuto': round(0.8 + (sessao * 0.05) * fator_melhora + random.uniform(-0.1, 0.1), 2),
        
        # Kills
        'kills_total': int(100 + (sessao * 25) + random.randint(-10, 10)),
        'kills_por_minuto': round(2.5 + (sessao * 0.1) * fator_melhora + random.uniform(-0.2, 0.2), 1),
        
        # Combate
        'mortes': max(0, int(sessao * 0.2 + random.randint(-1, 1))),
        'potions_usadas': int(sessao * 3 + random.randint(-2, 2)),
        
        # Skills
        'skills_usadas': {
            'skill1': int(sessao * 15 + random.randint(-5, 5)),
            'skill2': int(sessao * 12 + random.randint(-5, 5)),
            'skill3': int(sessao * 8 + random.randint(-3, 3)),
        },
        
        # ML
        'ml_predicoes': int(sessao * 10),
        'ml_acuracia': round(60 + (sessao * 2) + random.uniform(-5, 5), 1),
        
        # Movimento
        'movimentos_inteligentes': int(sessao * 5),
        'areas_exploradas': int(sessao * 2),
    }
    
    return metricas


def criar_arquivo_metrica(sessao: int):
    """Cria arquivo de métrica na pasta analytics_data"""
    
    analytics_folder = Path("analytics_data")
    analytics_folder.mkdir(exist_ok=True)
    
    # Gera métricas
    metricas = gerar_metricas_simuladas(sessao)
    
    # Nome do arquivo com timestamp
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo = analytics_folder / f"metrics_{timestamp_str}.json"
    
    # Salva
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(metricas, f, indent=2, ensure_ascii=False)
    
    return metricas


def simular_sessao_farming(duracao_minutos: int = 5, intervalo_segundos: int = 10):
    """
    Simula sessão de farming gerando métricas continuamente
    
    Args:
        duracao_minutos: Duração da simulação
        intervalo_segundos: Intervalo entre atualizações
    """
    
    print("🤖 SIMULADOR DE FARMING - TESTE DE DASHBOARD")
    print("="*70)
    print(f"\n⏱️  Simulando farming por {duracao_minutos} minutos")
    print(f"📊 Atualizando a cada {intervalo_segundos} segundos")
    print(f"🌐 Abra o dashboard em: http://localhost:5000")
    print("\n🎮 Simulação iniciada! (Ctrl+C para parar)\n")
    
    sessao = 0
    inicio = time.time()
    duracao_segundos = duracao_minutos * 60
    
    try:
        while (time.time() - inicio) < duracao_segundos:
            sessao += 1
            
            # Cria métricas
            metricas = criar_arquivo_metrica(sessao)
            
            # Exibe progresso
            tempo_decorrido = int(time.time() - inicio)
            minutos = tempo_decorrido // 60
            segundos = tempo_decorrido % 60
            
            print(f"[{minutos:02d}:{segundos:02d}] "
                  f"📊 Sessão {sessao} | "
                  f"⚔️ {metricas['kills_total']} kills | "
                  f"💰 {metricas['xp_total']:.1f}% XP | "
                  f"📈 {metricas['xp_por_minuto']:.2f}%/min")
            
            # Aguarda próximo ciclo
            time.sleep(intervalo_segundos)
    
    except KeyboardInterrupt:
        print("\n\n⏸️  Simulação interrompida pelo usuário")
    
    print("\n✅ Simulação concluída!")
    print(f"📁 {sessao} arquivos de métricas criados em analytics_data/")
    print("🌐 Veja os dados em tempo real no dashboard!")


def limpar_metricas_antigas():
    """Remove métricas antigas para resetar teste"""
    analytics_folder = Path("analytics_data")
    
    if not analytics_folder.exists():
        return
    
    arquivos = list(analytics_folder.glob("metrics_*.json"))
    
    if not arquivos:
        print("✅ Nenhuma métrica antiga encontrada")
        return
    
    print(f"🗑️  Removendo {len(arquivos)} métricas antigas...")
    
    for arquivo in arquivos:
        arquivo.unlink()
    
    print("✅ Métricas antigas removidas!")


def gerar_dados_historicos(quantidade: int = 50):
    """
    Gera histórico de dados para gráficos
    
    Args:
        quantidade: Número de pontos históricos
    """
    print(f"📊 Gerando {quantidade} pontos de histórico...")
    
    analytics_folder = Path("analytics_data")
    analytics_folder.mkdir(exist_ok=True)
    
    # Gera dados retroativos
    tempo_atual = datetime.now()
    
    for i in range(quantidade):
        # Timestamp retroativo (a cada 5 minutos)
        timestamp = tempo_atual - timedelta(minutes=(quantidade - i) * 5)
        
        # Gera métricas para esse ponto
        metricas = gerar_metricas_simuladas(i)
        metricas['timestamp'] = timestamp.isoformat()
        
        # Salva
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        arquivo = analytics_folder / f"metrics_{timestamp_str}.json"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(metricas, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {quantidade} pontos históricos gerados!")


if __name__ == "__main__":
    import sys
    
    print("🎮 TESTADOR DE DASHBOARD - Bot SRO Mobile")
    print("="*70)
    print()
    print("Opções:")
    print("  1 - Limpar métricas antigas")
    print("  2 - Gerar dados históricos (50 pontos)")
    print("  3 - Simular farming (5 minutos)")
    print("  4 - Simular farming (30 minutos)")
    print("  5 - Teste rápido (1 minuto)")
    print()
    
    if len(sys.argv) > 1:
        opcao = sys.argv[1]
    else:
        opcao = input("Escolha uma opção (1-5): ").strip()
    
    print()
    
    if opcao == "1":
        limpar_metricas_antigas()
    
    elif opcao == "2":
        gerar_dados_historicos(50)
        print("\n💡 Agora recarregue o dashboard para ver os gráficos!")
    
    elif opcao == "3":
        print("⚠️  Certifique-se que o dashboard está rodando!")
        print("   Execute: python3 dashboard_web.py\n")
        time.sleep(2)
        simular_sessao_farming(duracao_minutos=5, intervalo_segundos=10)
    
    elif opcao == "4":
        print("⚠️  Certifique-se que o dashboard está rodando!")
        print("   Execute: python3 dashboard_web.py\n")
        time.sleep(2)
        simular_sessao_farming(duracao_minutos=30, intervalo_segundos=15)
    
    elif opcao == "5":
        print("⚠️  Certifique-se que o dashboard está rodando!")
        print("   Execute: python3 dashboard_web.py\n")
        time.sleep(2)
        simular_sessao_farming(duracao_minutos=1, intervalo_segundos=5)
    
    else:
        print("❌ Opção inválida!")
        print("\n💡 Uso:")
        print("   python3 testar_dashboard.py 2  # Gerar histórico")
        print("   python3 testar_dashboard.py 3  # Simular 5 minutos")
