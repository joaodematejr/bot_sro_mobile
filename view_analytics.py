#!/usr/bin/env python3
"""
Analytics Viewer - Visualizador de histórico e estatísticas
"""

from analytics import FarmingAnalytics
from xp_detector import XPGainDetector
from pathlib import Path
import json
from datetime import datetime


def view_current_session():
    """Visualiza sessão atual"""
    analytics = FarmingAnalytics()
    
    print(analytics.generate_report())
    
    return analytics


def view_session_history():
    """Mostra histórico de sessões"""
    analytics_folder = Path("analytics_data")
    
    if not analytics_folder.exists():
        print("✗ Pasta analytics_data não encontrada")
        return
    
    sessions = sorted(analytics_folder.glob("session_*.json"))
    
    if not sessions:
        print("✗ Nenhuma sessão salva")
        return
    
    print("=" * 70)
    print("  📜 HISTÓRICO DE SESSÕES")
    print("=" * 70)
    
    for i, session_file in enumerate(sessions, 1):
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            session_id = data.get('session_id', 'Unknown')
            start = data.get('session_start', 'Unknown')
            xp_gained = data.get('current_xp', 0) - data.get('initial_xp', 0) if data.get('initial_xp') else 0
            kills = data.get('kills_count', 0)
            deaths = data.get('deaths_count', 0)
            
            print(f"\n{i}. Sessão {session_id}")
            print(f"   Início: {start}")
            print(f"   XP ganho: {xp_gained:.2f}%")
            print(f"   Kills: {kills} | Mortes: {deaths}")
            
        except Exception as e:
            print(f"\n{i}. {session_file.name} (erro ao ler)")


def analyze_xp_gains():
    """Analisa ganhos de XP das screenshots"""
    detector = XPGainDetector()
    
    print("=" * 70)
    print("  🔍 ANÁLISE DE XP GANHO (Screenshots)")
    print("=" * 70)
    
    # Processa pasta exp_ganho_treino
    results = detector.process_folder("exp_ganho_treino", limit=100)
    
    if results:
        xp_values = [xp for _, xp in results]
        stats = detector.get_statistics(xp_values)
        
        print(f"\n📊 Estatísticas ({len(results)} detecções):")
        print(f"  Total XP detectado: {stats['total']:.0f}")
        print(f"  Média por kill: {stats['mean']:.2f} XP")
        print(f"  Mediana: {stats['median']:.0f} XP")
        print(f"  Mín: {stats['min']:.0f} | Máx: {stats['max']:.0f}")
        print(f"  Desvio padrão: {stats['stdev']:.2f}")
        
        # Top 5 maiores ganhos
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        print(f"\n🏆 Top 5 maiores ganhos:")
        for filename, xp in sorted_results[:5]:
            print(f"  • {xp:.0f} XP - {filename}")
    else:
        print("\n✗ Nenhum valor de XP detectado nas screenshots")


def export_all_metrics():
    """Exporta todas as métricas"""
    analytics = FarmingAnalytics()
    
    filepath = analytics.export_metrics()
    
    print("=" * 70)
    print("  💾 EXPORTAÇÃO DE MÉTRICAS")
    print("=" * 70)
    print(f"\n✓ Métricas exportadas para:")
    print(f"  {filepath}")
    
    # Mostra tamanho do arquivo
    size = Path(filepath).stat().st_size / 1024
    print(f"\n  Tamanho: {size:.1f} KB")


def calculate_farming_efficiency():
    """Calcula eficiência geral de farming"""
    analytics = FarmingAnalytics()
    stats = analytics.get_current_statistics()
    
    print("=" * 70)
    print("  ⚡ ANÁLISE DE EFICIÊNCIA")
    print("=" * 70)
    
    # Eficiência de XP
    xp_per_min = stats['xp']['xp_per_minute']
    if xp_per_min > 0:
        hours_to_level = (100 - stats['xp']['current']) / xp_per_min / 60
        print(f"\n📈 Eficiência de XP:")
        print(f"  Taxa atual: {xp_per_min:.4f}%/min")
        print(f"  Horas para level: {hours_to_level:.2f}h")
        
        # Benchmark (você pode ajustar esses valores)
        if xp_per_min >= 0.5:
            rating = "Excelente ⭐⭐⭐"
        elif xp_per_min >= 0.3:
            rating = "Bom ⭐⭐"
        elif xp_per_min >= 0.1:
            rating = "Regular ⭐"
        else:
            rating = "Baixo ⚠️"
        
        print(f"  Avaliação: {rating}")
    
    # Eficiência de combate
    print(f"\n⚔️  Eficiência de Combate:")
    print(f"  Kill rate: {stats['combat']['kill_rate']:.1f}%")
    print(f"  Kills/min: {stats['combat']['kills_per_minute']:.2f}")
    print(f"  Duração média: {stats['combat']['avg_combat_duration']:.1f}s")
    
    # Taxa de morte
    if stats['combat']['kills'] > 0:
        death_rate = stats['combat']['deaths'] / stats['combat']['kills'] * 100
        print(f"  Taxa de morte: {death_rate:.1f}%")
        
        if death_rate < 1:
            safety = "Muito seguro ✓"
        elif death_rate < 5:
            safety = "Seguro ✓"
        elif death_rate < 10:
            safety = "Moderado ⚠️"
        else:
            safety = "Perigoso ⚠️⚠️"
        
        print(f"  Segurança: {safety}")
    
    # Uso de recursos
    total_potions = stats['resources']['total_potions']
    elapsed_min = stats['session']['elapsed_minutes']
    
    if elapsed_min > 0:
        potions_per_hour = total_potions / elapsed_min * 60
        print(f"\n💊 Uso de Recursos:")
        print(f"  Poções/hora: {potions_per_hour:.1f}")
        print(f"  Total usado: {total_potions}")


def interactive_menu():
    """Menu interativo"""
    while True:
        print("\n" + "=" * 70)
        print("  📊 ANALYTICS - MENU")
        print("=" * 70)
        print("\n1. Ver estatísticas da sessão atual")
        print("2. Histórico de sessões")
        print("3. Analisar XP ganho (screenshots)")
        print("4. Exportar métricas completas")
        print("5. Análise de eficiência")
        print("6. Relatório completo")
        print("7. Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            view_current_session()
        elif choice == '2':
            view_session_history()
        elif choice == '3':
            analyze_xp_gains()
        elif choice == '4':
            export_all_metrics()
        elif choice == '5':
            calculate_farming_efficiency()
        elif choice == '6':
            analytics = view_current_session()
            print("\n")
            analyze_xp_gains()
            print("\n")
            calculate_farming_efficiency()
        elif choice == '7':
            print("\n👋 Até logo!\n")
            break
        else:
            print("\n✗ Opção inválida")
        
        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    interactive_menu()
