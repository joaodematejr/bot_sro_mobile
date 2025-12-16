#!/usr/bin/env python3
"""
Sistema de Auto-Calibração Inteligente
Ajusta parâmetros automaticamente baseado em performance
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import deque

class AutoCalibracao:
    """
    Sistema que ajusta parâmetros do bot automaticamente
    baseado em métricas de performance
    """
    
    def __init__(self):
        self.config_file = Path("config_farming_adb.json")
        self.calibracao_file = Path("ml_models/auto_calibracao.json")
        self.historico_performance = deque(maxlen=50)  # Últimas 50 sessões
        
        # Parâmetros ajustáveis
        self.parametros_ajustaveis = {
            'intervalo_target': {'min': 1.0, 'max': 5.0, 'atual': 2.0, 'step': 0.2},
            'clicks_por_ciclo': {'min': 5, 'max': 30, 'atual': 15, 'step': 2},
            'duracao_skill': {'min': 0.5, 'max': 3.0, 'atual': 1.5, 'step': 0.2},
            'raio_mob_proximo': {'min': 50, 'max': 200, 'atual': 100, 'step': 10},
            'threshold_hp_baixo': {'min': 20, 'max': 60, 'atual': 30, 'step': 5},
        }
        
        # Métricas alvo
        self.metas = {
            'kills_por_hora': 150,      # Mínimo desejado
            'xp_por_minuto': 1.0,       # Mínimo desejado
            'taxa_morte': 0.1,          # Máximo aceitável (mortes/hora)
            'tempo_ocioso': 0.15,       # Máximo 15% do tempo
        }
        
        self._carregar_calibracao()
    
    def _carregar_calibracao(self):
        """Carrega histórico de calibração"""
        if self.calibracao_file.exists():
            try:
                with open(self.calibracao_file, 'r') as f:
                    data = json.load(f)
                    self.historico_performance = deque(data.get('historico', []), maxlen=50)
                    
                    # Atualiza parâmetros atuais
                    params_salvos = data.get('parametros_otimizados', {})
                    for param, valor in params_salvos.items():
                        if param in self.parametros_ajustaveis:
                            self.parametros_ajustaveis[param]['atual'] = valor
            except Exception as e:
                print(f"⚠️ Erro ao carregar calibração: {e}")
    
    def _salvar_calibracao(self):
        """Salva calibração"""
        try:
            self.calibracao_file.parent.mkdir(exist_ok=True)
            
            data = {
                'historico': list(self.historico_performance),
                'parametros_otimizados': {
                    param: config['atual'] 
                    for param, config in self.parametros_ajustaveis.items()
                },
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
            with open(self.calibracao_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar calibração: {e}")
    
    def analisar_sessao(self, metricas: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa sessão e sugere ajustes
        
        Args:
            metricas: Métricas da sessão (kills, xp, mortes, tempo)
        
        Returns:
            Sugestões de ajustes
        """
        # Calcula métricas normalizadas
        duracao_horas = metricas.get('duracao_segundos', 0) / 3600
        
        if duracao_horas < 0.1:  # Menos de 6 minutos
            return {'status': 'sessao_muito_curta'}
        
        kills_por_hora = metricas.get('kills', 0) / duracao_horas
        xp_por_minuto = metricas.get('xp_ganho', 0) / (duracao_horas * 60)
        mortes_por_hora = metricas.get('mortes', 0) / duracao_horas
        tempo_ocioso_pct = metricas.get('tempo_ocioso', 0) / metricas.get('duracao_segundos', 1)
        
        # Registra performance
        performance = {
            'timestamp': datetime.now().isoformat(),
            'kills_por_hora': kills_por_hora,
            'xp_por_minuto': xp_por_minuto,
            'mortes_por_hora': mortes_por_hora,
            'tempo_ocioso_pct': tempo_ocioso_pct,
            'parametros': {k: v['atual'] for k, v in self.parametros_ajustaveis.items()}
        }
        
        self.historico_performance.append(performance)
        
        # Identifica problemas
        problemas = []
        ajustes = []
        
        # 1. KILLS baixos
        if kills_por_hora < self.metas['kills_por_hora']:
            problemas.append({
                'tipo': 'kills_baixos',
                'valor_atual': kills_por_hora,
                'meta': self.metas['kills_por_hora']
            })
            
            # Sugestão: Reduzir intervalo de target
            if self.parametros_ajustaveis['intervalo_target']['atual'] > 1.5:
                ajustes.append({
                    'parametro': 'intervalo_target',
                    'acao': 'diminuir',
                    'razao': 'Aumentar frequência de busca por alvos'
                })
            
            # Sugestão: Aumentar clicks
            if self.parametros_ajustaveis['clicks_por_ciclo']['atual'] < 20:
                ajustes.append({
                    'parametro': 'clicks_por_ciclo',
                    'acao': 'aumentar',
                    'razao': 'Mais clicks = mais tentativas de ataque'
                })
        
        # 2. MORTES frequentes
        if mortes_por_hora > self.metas['taxa_morte']:
            problemas.append({
                'tipo': 'mortes_frequentes',
                'valor_atual': mortes_por_hora,
                'meta': self.metas['taxa_morte']
            })
            
            # Sugestão: Aumentar threshold de HP baixo
            ajustes.append({
                'parametro': 'threshold_hp_baixo',
                'acao': 'aumentar',
                'razao': 'Usar potion mais cedo para evitar mortes'
            })
        
        # 3. TEMPO OCIOSO alto
        if tempo_ocioso_pct > self.metas['tempo_ocioso']:
            problemas.append({
                'tipo': 'tempo_ocioso_alto',
                'valor_atual': tempo_ocioso_pct,
                'meta': self.metas['tempo_ocioso']
            })
            
            # Sugestão: Aumentar raio de detecção
            ajustes.append({
                'parametro': 'raio_mob_proximo',
                'acao': 'aumentar',
                'razao': 'Detectar mobs mais distantes'
            })
        
        # 4. XP baixo
        if xp_por_minuto < self.metas['xp_por_minuto']:
            problemas.append({
                'tipo': 'xp_baixo',
                'valor_atual': xp_por_minuto,
                'meta': self.metas['xp_por_minuto']
            })
        
        resultado = {
            'status': 'analisado',
            'performance': performance,
            'problemas': problemas,
            'ajustes_sugeridos': ajustes,
            'score_geral': self._calcular_score(performance)
        }
        
        self._salvar_calibracao()
        
        return resultado
    
    def _calcular_score(self, performance: Dict[str, Any]) -> float:
        """
        Calcula score geral de performance (0-100)
        
        Args:
            performance: Métricas de performance
        
        Returns:
            Score de 0 a 100
        """
        scores = []
        
        # Score de kills (0-30 pontos)
        kills_score = min(30, (performance['kills_por_hora'] / self.metas['kills_por_hora']) * 30)
        scores.append(kills_score)
        
        # Score de XP (0-30 pontos)
        xp_score = min(30, (performance['xp_por_minuto'] / self.metas['xp_por_minuto']) * 30)
        scores.append(xp_score)
        
        # Score de sobrevivência (0-25 pontos)
        if performance['mortes_por_hora'] == 0:
            sobrevivencia_score = 25
        else:
            sobrevivencia_score = max(0, 25 - (performance['mortes_por_hora'] * 10))
        scores.append(sobrevivencia_score)
        
        # Score de atividade (0-15 pontos)
        atividade_score = max(0, 15 - (performance['tempo_ocioso_pct'] * 100))
        scores.append(atividade_score)
        
        return sum(scores)
    
    def aplicar_ajustes_automaticos(self, ajustes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aplica ajustes automaticamente na config
        
        Args:
            ajustes: Lista de ajustes sugeridos
        
        Returns:
            Novos valores aplicados
        """
        if not self.config_file.exists():
            return {'erro': 'Config não encontrada'}
        
        try:
            # Carrega config atual
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            aplicados = {}
            
            for ajuste in ajustes:
                param = ajuste['parametro']
                acao = ajuste['acao']
                
                if param not in self.parametros_ajustaveis:
                    continue
                
                config_param = self.parametros_ajustaveis[param]
                valor_atual = config_param['atual']
                step = config_param['step']
                
                # Aplica ajuste
                if acao == 'aumentar':
                    novo_valor = min(config_param['max'], valor_atual + step)
                elif acao == 'diminuir':
                    novo_valor = max(config_param['min'], valor_atual - step)
                else:
                    continue
                
                # Atualiza
                config_param['atual'] = novo_valor
                aplicados[param] = {
                    'valor_anterior': valor_atual,
                    'valor_novo': novo_valor,
                    'razao': ajuste['razao']
                }
                
                # Atualiza na config JSON
                if param in config:
                    config[param] = novo_valor
            
            # Salva config atualizada
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self._salvar_calibracao()
            
            return {
                'status': 'ajustes_aplicados',
                'ajustes': aplicados
            }
            
        except Exception as e:
            return {'erro': str(e)}
    
    def relatorio_otimizacao(self) -> str:
        """Gera relatório de otimização"""
        if len(self.historico_performance) < 2:
            return "⚠️ Dados insuficientes para relatório (mínimo 2 sessões)"
        
        # Calcula tendências
        sessoes_recentes = list(self.historico_performance)[-10:]
        
        kills_medio = np.mean([s['kills_por_hora'] for s in sessoes_recentes])
        xp_medio = np.mean([s['xp_por_minuto'] for s in sessoes_recentes])
        mortes_medio = np.mean([s['mortes_por_hora'] for s in sessoes_recentes])
        score_medio = np.mean([self._calcular_score(s) for s in sessoes_recentes])
        
        relatorio = f"""
╔══════════════════════════════════════════════════════════════╗
║        📊 RELATÓRIO DE AUTO-CALIBRAÇÃO                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📈 PERFORMANCE MÉDIA (últimas {len(sessoes_recentes)} sessões)                      ║
║                                                              ║
║  • Kills/hora:    {kills_medio:6.1f}  (Meta: {self.metas['kills_por_hora']})              ║
║  • XP/minuto:     {xp_medio:6.2f}  (Meta: {self.metas['xp_por_minuto']})                ║
║  • Mortes/hora:   {mortes_medio:6.2f}  (Meta: <{self.metas['taxa_morte']})              ║
║  • Score Geral:   {score_medio:6.1f}/100                              ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  ⚙️  PARÂMETROS OTIMIZADOS                                   ║
║                                                              ║
"""
        
        for param, config in self.parametros_ajustaveis.items():
            relatorio += f"║  • {param:20s}: {config['atual']:6.1f}\n"
        
        relatorio += """║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        return relatorio


if __name__ == "__main__":
    print("🤖 SISTEMA DE AUTO-CALIBRAÇÃO")
    print("="*70)
    
    calibrador = AutoCalibracao()
    
    # Exemplo de análise
    metricas_teste = {
        'duracao_segundos': 3600,
        'kills': 120,
        'xp_ganho': 45,
        'mortes': 1,
        'tempo_ocioso': 600
    }
    
    resultado = calibrador.analisar_sessao(metricas_teste)
    
    print("\n📊 ANÁLISE DA SESSÃO:")
    print(f"Score: {resultado['score_geral']:.1f}/100")
    
    if resultado['problemas']:
        print("\n⚠️  PROBLEMAS DETECTADOS:")
        for prob in resultado['problemas']:
            print(f"  • {prob['tipo']}: {prob['valor_atual']:.2f} (meta: {prob['meta']})")
    
    if resultado['ajustes_sugeridos']:
        print("\n💡 AJUSTES SUGERIDOS:")
        for ajuste in resultado['ajustes_sugeridos']:
            print(f"  • {ajuste['parametro']}: {ajuste['acao']}")
            print(f"    Razão: {ajuste['razao']}")
    
    print("\n" + calibrador.relatorio_otimizacao())
