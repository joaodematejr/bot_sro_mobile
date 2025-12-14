#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparador de Performance: Bot Nativo vs Bot ML
Ajuda a medir e comparar eficiência
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

class ComparadorPerformance:
    """Compara performance entre bot nativo e bot ML"""
    
    def __init__(self):
        self.workspace = Path(".")
        self.comparacoes_dir = self.workspace / "comparacoes"
        self.comparacoes_dir.mkdir(exist_ok=True)
        self.arquivo_comparacao = self.comparacoes_dir / "comparacao_bots.json"
        
        # Carrega dados existentes
        self.dados = self._carregar_dados()
    
    def _carregar_dados(self) -> Dict:
        """Carrega comparações anteriores"""
        if self.arquivo_comparacao.exists():
            with open(self.arquivo_comparacao, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'bot_nativo': [],
            'bot_ml': [],
            'historico_comparacoes': []
        }
    
    def _salvar_dados(self):
        """Salva dados no arquivo"""
        with open(self.arquivo_comparacao, 'w', encoding='utf-8') as f:
            json.dump(self.dados, f, indent=2, ensure_ascii=False)
    
    def registrar_sessao_nativo(self, duracao_min: int, xp_ganho: float, 
                               kills: int, mortes: int, area: str):
        """Registra sessão do bot nativo"""
        
        sessao = {
            'timestamp': datetime.now().isoformat(),
            'duracao_min': duracao_min,
            'xp_ganho': xp_ganho,
            'kills': kills,
            'mortes': mortes,
            'area': area,
            'xp_por_hora': (xp_ganho / duracao_min) * 60,
            'kills_por_min': kills / duracao_min,
            'mortes_por_hora': (mortes / duracao_min) * 60,
            'xp_por_kill': xp_ganho / kills if kills > 0 else 0
        }
        
        self.dados['bot_nativo'].append(sessao)
        self._salvar_dados()
        
        print("✅ Sessão do bot nativo registrada!")
        print(f"   XP/hora: {sessao['xp_por_hora']:.2f}%")
        print(f"   Kills/min: {sessao['kills_por_min']:.2f}")
    
    def registrar_sessao_ml(self):
        """Importa última sessão do analytics do bot ML"""
        analytics_dir = self.workspace / "analytics_data"
        
        if not analytics_dir.exists():
            print("❌ Nenhuma sessão de analytics encontrada!")
            print("   Execute o bot ML primeiro: python3 main.py")
            return
        
        # Pega última sessão
        sessions = sorted(analytics_dir.glob('session_*.json'))
        
        if not sessions:
            print("❌ Nenhuma sessão salva!")
            return
        
        with open(sessions[-1], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stats = data['statistics']
        info = data['session_info']
        
        # Calcula duração em minutos
        start = datetime.fromisoformat(info['start_time'])
        end = datetime.fromisoformat(info['end_time'])
        duracao_min = (end - start).total_seconds() / 60
        
        sessao = {
            'timestamp': info['end_time'],
            'duracao_min': duracao_min,
            'xp_ganho': stats['xp']['gained'],
            'kills': stats['combat']['kills'],
            'mortes': stats['combat']['deaths'],
            'area': 'ML escolhida',
            'xp_por_hora': stats['xp']['xp_per_minute'] * 60,
            'kills_por_min': stats['combat']['kills_per_minute'],
            'mortes_por_hora': (stats['combat']['deaths'] / duracao_min) * 60 if duracao_min > 0 else 0,
            'xp_por_kill': stats['xp']['avg_xp_per_kill'],
            'amostras_ml': len(data.get('detailed_data', {}).get('ai_detections', []))
        }
        
        self.dados['bot_ml'].append(sessao)
        self._salvar_dados()
        
        print("✅ Sessão do bot ML importada!")
        print(f"   XP/hora: {sessao['xp_por_hora']:.4f}%")
        print(f"   Kills/min: {sessao['kills_por_min']:.2f}")
        print(f"   Amostras ML coletadas: {sessao['amostras_ml']}")
    
    def comparar_ultima_sessao(self):
        """Compara última sessão de cada bot"""
        
        if not self.dados['bot_nativo']:
            print("❌ Sem dados do bot nativo!")
            print("   Registre uma sessão primeiro: Opção 2 no menu")
            return
        
        if not self.dados['bot_ml']:
            print("❌ Sem dados do bot ML!")
            print("   Execute o bot ML primeiro: python3 main.py")
            return
        
        nativo = self.dados['bot_nativo'][-1]
        ml = self.dados['bot_ml'][-1]
        
        print("\n" + "="*80)
        print("📊 COMPARAÇÃO: BOT NATIVO vs BOT ML")
        print("="*80)
        
        # Comparação de XP
        print("\n💰 XP por Hora:")
        print(f"  Bot Nativo: {nativo['xp_por_hora']:.2f}%")
        print(f"  Bot ML:     {ml['xp_por_hora']:.4f}%")
        
        diff_xp = ((ml['xp_por_hora'] - nativo['xp_por_hora']) / nativo['xp_por_hora']) * 100
        
        if diff_xp > 0:
            print(f"  📈 ML é {diff_xp:.1f}% MELHOR")
        else:
            print(f"  📉 ML é {abs(diff_xp):.1f}% PIOR")
        
        # Comparação de Kills
        print("\n⚔️  Kills por Minuto:")
        print(f"  Bot Nativo: {nativo['kills_por_min']:.2f}")
        print(f"  Bot ML:     {ml['kills_por_min']:.2f}")
        
        diff_kills = ((ml['kills_por_min'] - nativo['kills_por_min']) / nativo['kills_por_min']) * 100
        
        if diff_kills > 0:
            print(f"  📈 ML é {diff_kills:.1f}% MELHOR")
        else:
            print(f"  📉 ML é {abs(diff_kills):.1f}% PIOR")
        
        # Comparação de Mortes
        print("\n💀 Mortes por Hora:")
        print(f"  Bot Nativo: {nativo['mortes_por_hora']:.2f}")
        print(f"  Bot ML:     {ml['mortes_por_hora']:.2f}")
        
        if ml['mortes_por_hora'] < nativo['mortes_por_hora']:
            diff_mortes = ((nativo['mortes_por_hora'] - ml['mortes_por_hora']) / nativo['mortes_por_hora']) * 100
            print(f"  ✅ ML morre {diff_mortes:.1f}% MENOS")
        else:
            diff_mortes = ((ml['mortes_por_hora'] - nativo['mortes_por_hora']) / nativo['mortes_por_hora']) * 100
            print(f"  ❌ ML morre {diff_mortes:.1f}% MAIS")
        
        # XP por Kill
        print("\n🎯 XP por Kill:")
        print(f"  Bot Nativo: {nativo['xp_por_kill']:.4f}%")
        print(f"  Bot ML:     {ml['xp_por_kill']:.4f}%")
        
        # Score geral
        print("\n🏆 PERFORMANCE SCORE:")
        
        score_nativo = (
            nativo['xp_por_hora'] * 0.5 +
            nativo['kills_por_min'] * 50 * 0.3 -
            nativo['mortes_por_hora'] * 10 * 0.2
        )
        
        score_ml = (
            ml['xp_por_hora'] * 1000 * 0.5 +  # XP em % (precisa * 1000)
            ml['kills_por_min'] * 50 * 0.3 -
            ml['mortes_por_hora'] * 10 * 0.2
        )
        
        print(f"  Bot Nativo: {score_nativo:.2f}")
        print(f"  Bot ML:     {score_ml:.2f}")
        
        diff_score = ((score_ml - score_nativo) / score_nativo) * 100
        
        print("\n📊 RESULTADO FINAL:")
        if diff_score > 20:
            print(f"  🌟🌟🌟 BOT ML É {diff_score:.1f}% SUPERIOR!")
            print("  EXCELENTE! ML está otimizado!")
        elif diff_score > 10:
            print(f"  🌟🌟 BOT ML É {diff_score:.1f}% MELHOR!")
            print("  MUITO BOM! Continue treinando!")
        elif diff_score > 0:
            print(f"  🌟 BOT ML É {diff_score:.1f}% MELHOR!")
            print("  BOM! Está evoluindo!")
        else:
            print(f"  ⚠️  BOT ML É {abs(diff_score):.1f}% PIOR")
            print("  Precisa de mais treinamento!")
            print("  Sugestões:")
            print("  - Colete mais amostras (meta: 1000+)")
            print("  - Ajuste parâmetros de skill/movimento")
            print("  - Teste outra área")
        
        print("\n" + "="*80)
        
        # Salva comparação
        comparacao = {
            'timestamp': datetime.now().isoformat(),
            'nativo': nativo,
            'ml': ml,
            'diferenca_xp_percent': diff_xp,
            'diferenca_kills_percent': diff_kills,
            'diferenca_score_percent': diff_score,
            'vencedor': 'ML' if diff_score > 0 else 'Nativo'
        }
        
        self.dados['historico_comparacoes'].append(comparacao)
        self._salvar_dados()
    
    def relatorio_historico(self):
        """Mostra evolução ao longo do tempo"""
        
        if not self.dados['historico_comparacoes']:
            print("❌ Nenhuma comparação realizada ainda!")
            return
        
        print("\n" + "="*80)
        print("📈 HISTÓRICO DE COMPARAÇÕES")
        print("="*80)
        
        for i, comp in enumerate(self.dados['historico_comparacoes'], 1):
            data = datetime.fromisoformat(comp['timestamp']).strftime('%d/%m/%Y %H:%M')
            
            print(f"\n{i}. {data}")
            print(f"   XP: ML {comp['diferenca_xp_percent']:+.1f}% vs Nativo")
            print(f"   Kills: ML {comp['diferenca_kills_percent']:+.1f}% vs Nativo")
            print(f"   Score: ML {comp['diferenca_score_percent']:+.1f}% vs Nativo")
            print(f"   🏆 Vencedor: {comp['vencedor']}")
        
        # Análise de tendência
        if len(self.dados['historico_comparacoes']) >= 3:
            ultimas_3 = self.dados['historico_comparacoes'][-3:]
            scores = [c['diferenca_score_percent'] for c in ultimas_3]
            
            print("\n📊 TENDÊNCIA (últimas 3 comparações):")
            
            if scores[-1] > scores[0]:
                melhoria = scores[-1] - scores[0]
                print(f"  📈 Melhorando: +{melhoria:.1f}% de evolução")
                print("  ✅ Continue o treinamento atual!")
            else:
                piora = scores[0] - scores[-1]
                print(f"  📉 Piorando: -{piora:.1f}% de regressão")
                print("  ⚠️  Revise configurações e ajustes!")
        
        print("\n" + "="*80)
    
    def exportar_csv(self):
        """Exporta dados para CSV para análise externa"""
        import csv
        
        csv_file = self.comparacoes_dir / f"comparacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho
            writer.writerow([
                'Timestamp', 'Bot', 'Duracao_Min', 'XP_Ganho', 'Kills', 'Mortes',
                'XP_Hora', 'Kills_Min', 'Mortes_Hora', 'XP_Kill', 'Area'
            ])
            
            # Dados bot nativo
            for sessao in self.dados['bot_nativo']:
                writer.writerow([
                    sessao['timestamp'], 'Nativo', sessao['duracao_min'],
                    sessao['xp_ganho'], sessao['kills'], sessao['mortes'],
                    sessao['xp_por_hora'], sessao['kills_por_min'],
                    sessao['mortes_por_hora'], sessao['xp_por_kill'], sessao['area']
                ])
            
            # Dados bot ML
            for sessao in self.dados['bot_ml']:
                writer.writerow([
                    sessao['timestamp'], 'ML', sessao['duracao_min'],
                    sessao['xp_ganho'], sessao['kills'], sessao['mortes'],
                    sessao['xp_por_hora'], sessao['kills_por_min'],
                    sessao['mortes_por_hora'], sessao['xp_por_kill'], sessao.get('area', 'ML')
                ])
        
        print(f"✅ Dados exportados para: {csv_file}")
        print("   Abra no Excel/LibreOffice para análise detalhada!")


def menu_interativo():
    """Menu principal"""
    comparador = ComparadorPerformance()
    
    while True:
        print("\n" + "="*60)
        print("🤖 COMPARADOR: BOT NATIVO vs BOT ML")
        print("="*60)
        print("\n1. ⚔️  Registrar sessão do Bot NATIVO")
        print("2. 🧠 Importar sessão do Bot ML (automático)")
        print("3. 📊 Comparar última sessão")
        print("4. 📈 Ver histórico de comparações")
        print("5. 💾 Exportar dados (CSV)")
        print("6. 📋 Guia rápido de uso")
        print("0. ❌ Sair")
        
        choice = input("\n➡️  Escolha: ").strip()
        
        if choice == '0':
            print("\n👋 Até logo!")
            break
        
        elif choice == '1':
            print("\n⚔️  REGISTRAR SESSÃO DO BOT NATIVO")
            print("-" * 60)
            print("Rode o bot nativo e anote os seguintes dados:\n")
            
            try:
                duracao = int(input("Duração (minutos): "))
                xp_ganho = float(input("XP ganho (%): "))
                kills = int(input("Total de kills: "))
                mortes = int(input("Total de mortes: "))
                area = input("Área de farming: ")
                
                comparador.registrar_sessao_nativo(duracao, xp_ganho, kills, mortes, area)
                
            except ValueError:
                print("❌ Valores inválidos!")
        
        elif choice == '2':
            print("\n🧠 IMPORTAR SESSÃO DO BOT ML")
            print("-" * 60)
            comparador.registrar_sessao_ml()
        
        elif choice == '3':
            comparador.comparar_ultima_sessao()
        
        elif choice == '4':
            comparador.relatorio_historico()
        
        elif choice == '5':
            comparador.exportar_csv()
        
        elif choice == '6':
            print("\n📋 GUIA RÁPIDO:")
            print("-" * 60)
            print("1. Execute bot NATIVO por 1 hora")
            print("   Anote: XP ganho, kills, mortes")
            print("\n2. Use opção 1 para registrar dados do nativo")
            print("\n3. Execute bot ML por 1 hora:")
            print("   python3 main.py")
            print("\n4. Use opção 2 para importar dados do ML")
            print("\n5. Use opção 3 para comparar!")
            print("\n6. Repita processo para ver evolução")
            print("\n💡 Meta: Bot ML > 120% do bot nativo")
        
        else:
            print("❌ Opção inválida!")
        
        input("\n⏸️  Pressione ENTER para continuar...")


if __name__ == "__main__":
    menu_interativo()
