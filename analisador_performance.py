#!/usr/bin/env python3
"""
Analisador de Performance - Baseado em Dados Reais
Analisa coletas do dia e gera recomendações precisas
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import statistics

class AnalisadorPerformance:
    """Analisa dados reais coletados e sugere melhorias"""
    
    def __init__(self):
        self.analytics_folder = Path("analytics_data")
        self.config_file = Path("config_farming_adb.json")
    
    def analisar_sessoes_recentes(self, horas: int = 24) -> Dict[str, Any]:
        """Analisa sessões das últimas N horas"""
        cutoff = datetime.now() - timedelta(hours=horas)
        
        metricas_sessoes = []
        
        for arquivo in sorted(self.analytics_folder.glob("metrics_*.json")):
            try:
                # Extrai timestamp do nome
                timestamp_str = arquivo.stem.replace('metrics_', '')
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                if timestamp < cutoff:
                    continue
                
                with open(arquivo, 'r') as f:
                    data = json.load(f)
                    metricas_sessoes.append(data)
            except Exception as e:
                continue
        
        return self._processar_metricas(metricas_sessoes)
    
    def _processar_metricas(self, sessoes: List[Dict]) -> Dict[str, Any]:
        """Processa métricas de múltiplas sessões"""
        if not sessoes:
            return {'status': 'sem_dados'}
        
        # Extrai dados
        kills_totais = []
        kills_por_min = []
        duracoes = []
        mortes_totais = []
        deteccoes_ml = []
        movimentos_ml = []
        
        for s in sessoes:
            try:
                stats = s.get('statistics', {})
                
                # Combat
                combat = stats.get('combat', {})
                kills_totais.append(combat.get('kills', 0))
                kills_por_min.append(combat.get('kills_per_minute', 0))
                mortes_totais.append(combat.get('deaths', 0))
                
                # Sessão
                session = stats.get('session', {})
                duracoes.append(session.get('elapsed_minutes', 0))
                
                # AI
                ai = stats.get('ai', {})
                deteccoes_ml.append(ai.get('detections', 0))
                
                # Movimento
                mov = stats.get('movement', {})
                movimentos_ml.append(mov.get('ml_movements', 0))
            except:
                continue
        
        # Filtra zeros
        kills_totais = [k for k in kills_totais if k > 0]
        kills_por_min = [k for k in kills_por_min if k > 0]
        duracoes = [d for d in duracoes if d > 0]
        
        resultado = {
            'status': 'ok',
            'sessoes_analisadas': len(sessoes),
            'periodo_horas': 24,
            'kills': {
                'total': sum(kills_totais),
                'media_por_sessao': statistics.mean(kills_totais) if kills_totais else 0,
                'media_por_minuto': statistics.mean(kills_por_min) if kills_por_min else 0,
                'melhor_kills_min': max(kills_por_min) if kills_por_min else 0
            },
            'tempo': {
                'total_minutos': sum(duracoes),
                'media_sessao': statistics.mean(duracoes) if duracoes else 0
            },
            'mortes': {
                'total': sum(mortes_totais),
                'taxa_morte_hora': sum(mortes_totais) / (sum(duracoes)/60) if duracoes else 0
            },
            'ml': {
                'deteccoes_total': sum(deteccoes_ml),
                'movimentos_total': sum(movimentos_ml),
                'uso_ml_percent': (sum(movimentos_ml) / sum(kills_totais) * 100) if kills_totais else 0
            }
        }
        
        return resultado
    
    def gerar_recomendacoes(self, analise: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas nos dados"""
        if analise.get('status') != 'ok':
            return []
        
        recomendacoes = []
        
        # 1. Kills/min baixo
        kills_min = analise['kills']['media_por_minuto']
        if kills_min < 0.3:  # Menos de 1 kill a cada 3 minutos
            recomendacoes.append({
                'prioridade': 'CRÍTICA',
                'problema': f'Kills/min muito baixo: {kills_min:.2f}',
                'impacto': 'Performance 80% abaixo do ideal',
                'solucoes': [
                    'Reduzir intervalo_target de 1.8 para 1.0',
                    'Aumentar clicks_por_ciclo de 22 para 30',
                    'Reduzir pausa_entre_ciclos de 8 para 5',
                    'Verificar se está em área com mobs suficientes'
                ],
                'config_sugerida': {
                    'intervalo_target': 1.0,
                    'target_clicks_por_ciclo': 30,
                    'target_pausa_entre_ciclos': 5
                }
            })
        elif kills_min < 1.5:
            recomendacoes.append({
                'prioridade': 'ALTA',
                'problema': f'Kills/min abaixo do ideal: {kills_min:.2f}',
                'impacto': 'Performance 50% abaixo do potencial',
                'solucoes': [
                    'Reduzir intervalo_target para 1.2',
                    'Aumentar clicks_por_ciclo para 25',
                    'Ativar movimento inteligente ML'
                ],
                'config_sugerida': {
                    'intervalo_target': 1.2,
                    'target_clicks_por_ciclo': 25
                }
            })
        
        # 2. Uso do ML baixo
        uso_ml = analise['ml']['uso_ml_percent']
        if uso_ml < 10:
            recomendacoes.append({
                'prioridade': 'MÉDIA',
                'problema': f'Sistema ML pouco utilizado: {uso_ml:.1f}%',
                'impacto': 'Perdendo otimizações de IA',
                'solucoes': [
                    'Ativar movimento inteligente',
                    'Coletar mais amostras de treino (50+ necessário)',
                    'Executar treino ML: python3 retreinar_otimizado.py',
                    'Verificar se hotspots estão sendo detectados'
                ],
                'config_sugerida': {
                    'usar_movimento_inteligente': True,
                    'intervalo_captura_minimap': 3
                }
            })
        
        # 3. Taxa de morte
        taxa_morte = analise['mortes']['taxa_morte_hora']
        if taxa_morte > 0.5:
            recomendacoes.append({
                'prioridade': 'ALTA',
                'problema': f'Mortes frequentes: {taxa_morte:.1f}/hora',
                'impacto': 'Tempo perdido respawnando',
                'solucoes': [
                    'Aumentar threshold HP para usar potion',
                    'Ativar sistema de fuga automática',
                    'Ajustar detecção de inimigos perigosos'
                ],
                'config_sugerida': {
                    'threshold_hp_baixo': 50,
                    'usar_fuga_automatica': True
                }
            })
        
        # 4. Sessões muito curtas
        media_sessao = analise['tempo']['media_sessao']
        if media_sessao < 15:
            recomendacoes.append({
                'prioridade': 'BAIXA',
                'problema': f'Sessões muito curtas: {media_sessao:.1f}min',
                'impacto': 'ML precisa de sessões longas para aprender',
                'solucoes': [
                    'Farmar por pelo menos 30 minutos seguidos',
                    'Ativar modo AFK com supervisão',
                    'Configurar sistema de recuperação automática'
                ],
                'config_sugerida': {
                    'usar_auto_recovery': True
                }
            })
        
        return sorted(recomendacoes, 
                     key=lambda x: {'CRÍTICA': 0, 'ALTA': 1, 'MÉDIA': 2, 'BAIXA': 3}[x['prioridade']])
    
    def aplicar_config_otimizada(self, recomendacoes: List[Dict]) -> bool:
        """Aplica configurações otimizadas automaticamente"""
        if not self.config_file.exists():
            return False
        
        try:
            # Carrega config atual
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Backup
            backup_file = self.config_file.with_suffix('.json.bak')
            with open(backup_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Aplica mudanças de cada recomendação
            mudancas = {}
            for rec in recomendacoes:
                if rec['prioridade'] in ['CRÍTICA', 'ALTA']:
                    config_sugerida = rec.get('config_sugerida', {})
                    for key, valor in config_sugerida.items():
                        if key in config:
                            mudancas[key] = {
                                'anterior': config[key],
                                'novo': valor
                            }
                            config[key] = valor
            
            # Salva config atualizada
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Erro ao aplicar config: {e}")
            return False
    
    def relatorio_completo(self) -> str:
        """Gera relatório completo"""
        analise = self.analisar_sessoes_recentes(24)
        
        if analise.get('status') != 'ok':
            return "⚠️ Sem dados suficientes para análise (farme por pelo menos 10 minutos)"
        
        recomendacoes = self.gerar_recomendacoes(analise)
        
        relatorio = f"""
╔══════════════════════════════════════════════════════════════════════╗
║            📊 ANÁLISE DE PERFORMANCE - ÚLTIMAS 24 HORAS             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  📅 Sessões analisadas: {analise['sessoes_analisadas']:>2}                                      ║
║  ⏱️  Tempo total: {analise['tempo']['total_minutos']:>6.1f} minutos                           ║
║  📊 Média por sessão: {analise['tempo']['media_sessao']:>5.1f} min                            ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  ⚔️  COMBATE                                                         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Kills total: {analise['kills']['total']:>4}                                            ║
║  Kills/sessão: {analise['kills']['media_por_sessao']:>5.1f}                                      ║
║  Kills/min: {analise['kills']['media_por_minuto']:>8.2f}  {"🟢" if analise['kills']['media_por_minuto'] >= 1.5 else "🟡" if analise['kills']['media_por_minuto'] >= 0.5 else "🔴"}                                ║
║  Melhor: {analise['kills']['melhor_kills_min']:>11.2f} kills/min                           ║
║                                                                      ║
║  Mortes: {analise['mortes']['total']:>6}                                              ║
║  Taxa: {analise['mortes']['taxa_morte_hora']:>9.2f} mortes/hora  {"🟢" if analise['mortes']['taxa_morte_hora'] < 0.2 else "🟡" if analise['mortes']['taxa_morte_hora'] < 1 else "🔴"}                  ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  🧠 INTELIGÊNCIA ARTIFICIAL                                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Detecções ML: {analise['ml']['deteccoes_total']:>5}                                        ║
║  Movimentos ML: {analise['ml']['movimentos_total']:>4}                                       ║
║  Uso do ML: {analise['ml']['uso_ml_percent']:>8.1f}%  {"🟢" if analise['ml']['uso_ml_percent'] >= 20 else "🟡" if analise['ml']['uso_ml_percent'] >= 5 else "🔴"}                           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

"""
        
        if recomendacoes:
            relatorio += f"""
╔══════════════════════════════════════════════════════════════════════╗
║                  ⚠️  RECOMENDAÇÕES DE MELHORIA                       ║
╚══════════════════════════════════════════════════════════════════════╝

"""
            for i, rec in enumerate(recomendacoes, 1):
                emoji_prioridade = {
                    'CRÍTICA': '🔴',
                    'ALTA': '🟡',
                    'MÉDIA': '🟠',
                    'BAIXA': '⚪'
                }
                
                relatorio += f"""
{'─'*72}
{emoji_prioridade[rec['prioridade']]} PRIORIDADE {rec['prioridade']} #{i}
{'─'*72}

❌ PROBLEMA: {rec['problema']}
💥 IMPACTO: {rec['impacto']}

✅ SOLUÇÕES:
"""
                for sol in rec['solucoes']:
                    relatorio += f"   • {sol}\n"
                
                if rec.get('config_sugerida'):
                    relatorio += f"\n⚙️  CONFIGURAÇÃO SUGERIDA:\n"
                    for key, valor in rec['config_sugerida'].items():
                        relatorio += f"   {key} = {valor}\n"
        else:
            relatorio += "\n✅ Performance excelente! Nenhuma recomendação crítica.\n"
        
        return relatorio


if __name__ == "__main__":
    import sys
    
    print("📊 ANALISADOR DE PERFORMANCE")
    print("="*72)
    
    analisador = AnalisadorPerformance()
    
    # Gera relatório
    print(analisador.relatorio_completo())
    
    # Pergunta se quer aplicar
    if len(sys.argv) > 1 and sys.argv[1] == '--aplicar':
        analise = analisador.analisar_sessoes_recentes(24)
        recomendacoes = analisador.gerar_recomendacoes(analise)
        
        criticas_altas = [r for r in recomendacoes if r['prioridade'] in ['CRÍTICA', 'ALTA']]
        
        if criticas_altas:
            print("\n" + "="*72)
            print("⚙️  APLICANDO CONFIGURAÇÕES OTIMIZADAS...")
            print("="*72)
            
            if analisador.aplicar_config_otimizada(recomendacoes):
                print("\n✅ Configurações aplicadas com sucesso!")
                print("📁 Backup salvo em: config_farming_adb.json.bak")
                print("\n🎮 Reinicie o bot para usar as novas configurações")
            else:
                print("\n❌ Erro ao aplicar configurações")
        else:
            print("\n✅ Nenhuma mudança crítica necessária")
    else:
        print("\n💡 Para aplicar automaticamente as configurações:")
        print("   python3 analisador_performance.py --aplicar")
