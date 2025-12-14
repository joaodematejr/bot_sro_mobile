#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Recompensas para Aprendizado por Reforço
Ensina o bot quais ações são boas ou ruins
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque

class SistemaRecompensas:
    """
    Sistema de recompensas para treinar bot com reinforcement learning
    """
    
    def __init__(self):
        self.rewards_file = Path("ml_models/rewards_history.json")
        self.estado_anterior = None
        self.acao_anterior = None
        self.historico_recompensas = []
        self.metricas_sessao = {
            'recompensa_total': 0,
            'recompensas_positivas': 0,
            'recompensas_negativas': 0,
            'melhor_acao': None,
            'pior_acao': None
        }
        
        # Pesos de recompensas (ajustáveis)
        self.pesos = {
            # Combate
            'kill': 10.0,           # Matou um mob
            'kill_rapido': 5.0,     # Matou em < 5s
            'multi_kill': 15.0,     # Matou 2+ mobs seguidos
            'xp_ganho': 1.0,        # Por cada 0.01% de XP
            
            # Sobrevivência
            'morte': -50.0,         # Morreu
            'hp_critico': -10.0,    # HP < 20%
            'hp_baixo': -5.0,       # HP < 50%
            'sem_dano': 2.0,        # Matou sem levar dano
            
            # Eficiência
            'tempo_ocioso': -2.0,   # Sem ação por 10s+
            'mob_proximo': 5.0,     # Detectou e foi para mob
            'fuga_sucesso': 8.0,    # Fugiu com sucesso (HP baixo)
            'item_coletado': 3.0,   # Coletou item
            
            # Movimento
            'area_boa': 5.0,        # Área com muitos mobs
            'area_ruim': -3.0,      # Área vazia (sem mobs)
            'stuck': -8.0,          # Ficou preso/travado
            
            # Skills
            'skill_eficiente': 3.0,  # Skill com cooldown otimizado
            'skill_desperdicada': -2.0,  # Skill usada sem alvo
            'aoe_eficiente': 7.0,    # AOE com 3+ mobs
        }
        
        # Histórico recente (últimas 100 ações)
        self.historico_recente = deque(maxlen=100)
        
        # Carrega histórico
        self._carregar_historico()
    
    def _carregar_historico(self):
        """Carrega histórico de recompensas"""
        if self.rewards_file.exists():
            try:
                with open(self.rewards_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.historico_recompensas = data.get('historico', [])
            except Exception as e:
                print(f"⚠️ Erro ao carregar histórico de recompensas: {e}")
    
    def _salvar_historico(self):
        """Salva histórico de recompensas"""
        try:
            self.rewards_file.parent.mkdir(exist_ok=True)
            
            data = {
                'historico': self.historico_recompensas[-1000:],  # Últimas 1000
                'metricas_totais': self._calcular_metricas_totais(),
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
            with open(self.rewards_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erro ao salvar histórico: {e}")
    
    def registrar_estado(self, estado: Dict[str, Any]) -> Optional[float]:
        """
        Registra estado atual e calcula recompensa da ação anterior
        
        Args:
            estado: Dicionário com informações do estado atual
                - hp_percent: HP atual (0-100)
                - mobs_nearby: Quantidade de mobs próximos
                - xp_percent: XP atual (0-100)
                - in_combat: Se está em combate
                - position: Posição atual (x, y)
                - last_action: Última ação tomada
                - kills_recent: Kills nos últimos 10s
                - damage_taken: Dano recebido recentemente
                
        Returns:
            Recompensa calculada para a ação anterior (ou None se primeira iteração)
        """
        recompensa = None
        
        # Calcula recompensa se houver estado anterior
        if self.estado_anterior is not None:
            recompensa = self._calcular_recompensa(self.estado_anterior, estado)
            
            # Registra no histórico
            self._adicionar_recompensa(
                estado_anterior=self.estado_anterior,
                acao=self.acao_anterior,
                recompensa=recompensa,
                novo_estado=estado
            )
        
        # Atualiza estado anterior
        self.estado_anterior = estado.copy()
        self.acao_anterior = estado.get('last_action', 'none')
        
        return recompensa
    
    def _calcular_recompensa(self, estado_anterior: Dict, estado_atual: Dict) -> float:
        """Calcula recompensa baseada na transição de estados"""
        
        recompensa_total = 0.0
        detalhes = []
        
        # 1. Combate e Kills
        kills_atual = estado_atual.get('kills_recent', 0)
        kills_anterior = estado_anterior.get('kills_recent', 0)
        
        if kills_atual > kills_anterior:
            diff_kills = kills_atual - kills_anterior
            recompensa_total += self.pesos['kill'] * diff_kills
            detalhes.append(f"+{self.pesos['kill'] * diff_kills:.1f} (kill)")
            
            # Multi-kill bonus
            if diff_kills >= 2:
                recompensa_total += self.pesos['multi_kill']
                detalhes.append(f"+{self.pesos['multi_kill']:.1f} (multi-kill)")
            
            # Kill sem dano
            if estado_atual.get('damage_taken', 0) == 0:
                recompensa_total += self.pesos['sem_dano']
                detalhes.append(f"+{self.pesos['sem_dano']:.1f} (sem dano)")
        
        # 2. XP Ganho
        xp_atual = estado_atual.get('xp_percent', 0)
        xp_anterior = estado_anterior.get('xp_percent', 0)
        
        if xp_atual > xp_anterior:
            xp_ganho = xp_atual - xp_anterior
            recompensa_xp = xp_ganho * 100 * self.pesos['xp_ganho']  # x100 para escalar
            recompensa_total += recompensa_xp
            detalhes.append(f"+{recompensa_xp:.1f} (xp)")
        
        # 3. Sobrevivência e HP
        hp_atual = estado_atual.get('hp_percent', 100)
        hp_anterior = estado_anterior.get('hp_percent', 100)
        
        # Morte detectada
        if hp_atual == 100 and hp_anterior < 20:
            # Provavelmente morreu e respawnou
            recompensa_total += self.pesos['morte']
            detalhes.append(f"{self.pesos['morte']:.1f} (morte)")
        
        # HP crítico
        elif hp_atual < 20:
            recompensa_total += self.pesos['hp_critico']
            detalhes.append(f"{self.pesos['hp_critico']:.1f} (hp crítico)")
        
        # HP baixo
        elif hp_atual < 50:
            recompensa_total += self.pesos['hp_baixo']
            detalhes.append(f"{self.pesos['hp_baixo']:.1f} (hp baixo)")
        
        # 4. Eficiência e Movimento
        mobs_atual = estado_atual.get('mobs_nearby', 0)
        mobs_anterior = estado_anterior.get('mobs_nearby', 0)
        in_combat = estado_atual.get('in_combat', False)
        
        # Área boa (muitos mobs)
        if mobs_atual >= 3:
            recompensa_total += self.pesos['area_boa']
            detalhes.append(f"+{self.pesos['area_boa']:.1f} (área boa)")
        
        # Área ruim (sem mobs e não em combate)
        elif mobs_atual == 0 and not in_combat:
            recompensa_total += self.pesos['area_ruim']
            detalhes.append(f"{self.pesos['area_ruim']:.1f} (área vazia)")
        
        # Detectou mob e foi para ele
        if mobs_atual > mobs_anterior and in_combat:
            recompensa_total += self.pesos['mob_proximo']
            detalhes.append(f"+{self.pesos['mob_proximo']:.1f} (mob detectado)")
        
        # 5. Skills e Ações
        ultima_acao = estado_atual.get('last_action', 'none')
        
        # AOE com múltiplos alvos
        if 'aoe' in ultima_acao.lower() and mobs_atual >= 3:
            recompensa_total += self.pesos['aoe_eficiente']
            detalhes.append(f"+{self.pesos['aoe_eficiente']:.1f} (aoe eficiente)")
        
        # Skill sem alvo
        elif 'skill' in ultima_acao.lower() and mobs_atual == 0:
            recompensa_total += self.pesos['skill_desperdicada']
            detalhes.append(f"{self.pesos['skill_desperdicada']:.1f} (skill desperdiçada)")
        
        # 6. Items Coletados
        items_atual = estado_atual.get('items_collected', 0)
        items_anterior = estado_anterior.get('items_collected', 0)
        
        if items_atual > items_anterior:
            diff_items = items_atual - items_anterior
            recompensa_total += self.pesos['item_coletado'] * diff_items
            detalhes.append(f"+{self.pesos['item_coletado'] * diff_items:.1f} (items)")
        
        # Atualiza métricas da sessão
        self.metricas_sessao['recompensa_total'] += recompensa_total
        
        if recompensa_total > 0:
            self.metricas_sessao['recompensas_positivas'] += 1
        elif recompensa_total < 0:
            self.metricas_sessao['recompensas_negativas'] += 1
        
        # Log detalhado (apenas se significativo)
        if abs(recompensa_total) > 5.0:
            print(f"  💰 Recompensa: {recompensa_total:+.1f} - {', '.join(detalhes)}")
        
        return recompensa_total
    
    def _adicionar_recompensa(self, estado_anterior: Dict, acao: str, 
                             recompensa: float, novo_estado: Dict):
        """Adiciona recompensa ao histórico"""
        
        registro = {
            'timestamp': datetime.now().isoformat(),
            'estado_anterior': {
                'hp': estado_anterior.get('hp_percent', 0),
                'mobs': estado_anterior.get('mobs_nearby', 0),
                'xp': estado_anterior.get('xp_percent', 0)
            },
            'acao': acao,
            'recompensa': recompensa,
            'novo_estado': {
                'hp': novo_estado.get('hp_percent', 0),
                'mobs': novo_estado.get('mobs_nearby', 0),
                'xp': novo_estado.get('xp_percent', 0)
            }
        }
        
        self.historico_recompensas.append(registro)
        self.historico_recente.append(recompensa)
        
        # Atualiza melhor/pior ação
        if (self.metricas_sessao['melhor_acao'] is None or 
            recompensa > self.metricas_sessao['melhor_acao'][1]):
            self.metricas_sessao['melhor_acao'] = (acao, recompensa)
        
        if (self.metricas_sessao['pior_acao'] is None or 
            recompensa < self.metricas_sessao['pior_acao'][1]):
            self.metricas_sessao['pior_acao'] = (acao, recompensa)
        
        # Salva periodicamente (a cada 50 registros)
        if len(self.historico_recompensas) % 50 == 0:
            self._salvar_historico()
    
    def _calcular_metricas_totais(self) -> Dict[str, Any]:
        """Calcula métricas totais do histórico"""
        
        if not self.historico_recompensas:
            return {}
        
        recompensas = [r['recompensa'] for r in self.historico_recompensas]
        
        return {
            'total_registros': len(self.historico_recompensas),
            'recompensa_media': np.mean(recompensas),
            'recompensa_total': np.sum(recompensas),
            'recompensa_maxima': np.max(recompensas),
            'recompensa_minima': np.min(recompensas),
            'desvio_padrao': np.std(recompensas)
        }
    
    def get_metricas_sessao(self) -> Dict[str, Any]:
        """Retorna métricas da sessão atual"""
        
        metricas = self.metricas_sessao.copy()
        
        if len(self.historico_recente) > 0:
            metricas['recompensa_media_recente'] = np.mean(list(self.historico_recente))
            metricas['tendencia'] = 'positiva' if metricas['recompensa_media_recente'] > 0 else 'negativa'
        
        return metricas
    
    def exibir_relatorio(self):
        """Exibe relatório de recompensas"""
        
        print("\n" + "="*70)
        print("💰 RELATÓRIO DE RECOMPENSAS")
        print("="*70)
        
        metricas = self.get_metricas_sessao()
        
        print(f"\n📊 Sessão Atual:")
        print(f"  Recompensa total: {metricas['recompensa_total']:+.1f}")
        print(f"  Ações positivas: {metricas['recompensas_positivas']}")
        print(f"  Ações negativas: {metricas['recompensas_negativas']}")
        
        if metricas.get('recompensa_media_recente'):
            print(f"  Média recente: {metricas['recompensa_media_recente']:+.1f}")
            print(f"  Tendência: {metricas['tendencia']}")
        
        if metricas['melhor_acao']:
            acao, valor = metricas['melhor_acao']
            print(f"\n🌟 Melhor ação: {acao} ({valor:+.1f})")
        
        if metricas['pior_acao']:
            acao, valor = metricas['pior_acao']
            print(f"⚠️  Pior ação: {acao} ({valor:+.1f})")
        
        # Métricas totais
        metricas_totais = self._calcular_metricas_totais()
        
        if metricas_totais:
            print(f"\n📈 Histórico Total:")
            print(f"  Registros: {metricas_totais['total_registros']}")
            print(f"  Recompensa total: {metricas_totais['recompensa_total']:+.1f}")
            print(f"  Média: {metricas_totais['recompensa_media']:+.1f}")
            print(f"  Máxima: {metricas_totais['recompensa_maxima']:+.1f}")
            print(f"  Mínima: {metricas_totais['recompensa_minima']:+.1f}")
        
        print("\n" + "="*70)
    
    def finalizar_sessao(self):
        """Finaliza sessão e salva dados"""
        self._salvar_historico()
        self.exibir_relatorio()
