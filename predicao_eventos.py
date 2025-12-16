#!/usr/bin/env python3
"""
Sistema de Predição de Eventos
Usa séries temporais para prever eventos no jogo
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

class PredicaoEventos:
    """
    Prediz eventos como:
    - Quando HP ficará baixo
    - Quando skills estarão disponíveis
    - Padrões de spawn de mobs
    - Horários de pico de XP
    """
    
    def __init__(self):
        self.predicao_file = Path("ml_models/predicoes.json")
        
        # Histórico de eventos
        self.historico_hp = []
        self.historico_skills = defaultdict(list)
        self.historico_spawns = []
        self.historico_xp = []
        
        # Padrões aprendidos
        self.padroes = {
            'hp_medio_combate': 0,
            'tempo_medio_kill': 0,
            'intervalo_spawn': 0,
            'xp_medio_kill': 0
        }
        
        self._carregar_historico()
    
    def _carregar_historico(self):
        """Carrega histórico de predições"""
        if self.predicao_file.exists():
            try:
                with open(self.predicao_file, 'r') as f:
                    data = json.load(f)
                    self.padroes = data.get('padroes', self.padroes)
            except Exception as e:
                print(f"⚠️ Erro ao carregar predições: {e}")
    
    def _salvar_predicao(self):
        """Salva predições"""
        try:
            self.predicao_file.parent.mkdir(exist_ok=True)
            
            data = {
                'padroes': self.padroes,
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
            with open(self.predicao_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar predições: {e}")
    
    def registrar_combate(self, dados_combate: Dict[str, Any]):
        """
        Registra dados de combate para aprendizado
        
        Args:
            dados_combate: {
                'hp_inicial': 100,
                'hp_final': 85,
                'duracao': 8.5,
                'xp_ganho': 0.05,
                'skills_usadas': ['skill1', 'skill2']
            }
        """
        # Registra HP
        dano_sofrido = dados_combate.get('hp_inicial', 100) - dados_combate.get('hp_final', 100)
        self.historico_hp.append({
            'timestamp': datetime.now(),
            'dano': dano_sofrido,
            'duracao': dados_combate.get('duracao', 0)
        })
        
        # Registra XP
        self.historico_xp.append({
            'timestamp': datetime.now(),
            'xp': dados_combate.get('xp_ganho', 0),
            'duracao': dados_combate.get('duracao', 0)
        })
        
        # Atualiza padrões
        if len(self.historico_hp) > 10:
            # Calcula dano médio por segundo
            danos_recentes = [h['dano']/max(h['duracao'], 1) for h in self.historico_hp[-10:]]
            self.padroes['dano_medio_por_segundo'] = np.mean(danos_recentes)
        
        if len(self.historico_xp) > 10:
            xps_recentes = [h['xp'] for h in self.historico_xp[-10:]]
            self.padroes['xp_medio_kill'] = np.mean(xps_recentes)
            
            duracoes = [h['duracao'] for h in self.historico_xp[-10:]]
            self.padroes['tempo_medio_kill'] = np.mean(duracoes)
        
        self._salvar_predicao()
    
    def prever_tempo_ate_hp_baixo(self, hp_atual: float, threshold: float = 30) -> Optional[float]:
        """
        Prevê quanto tempo até HP ficar abaixo do threshold
        
        Args:
            hp_atual: HP atual (%)
            threshold: Threshold de HP baixo (%)
        
        Returns:
            Tempo estimado em segundos, ou None se não souber
        """
        if hp_atual <= threshold:
            return 0
        
        dano_por_segundo = self.padroes.get('dano_medio_por_segundo', 0)
        
        if dano_por_segundo <= 0:
            return None
        
        # Calcula quanto HP precisa perder
        hp_a_perder = hp_atual - threshold
        
        # Tempo = HP a perder / dano por segundo
        tempo_estimado = hp_a_perder / dano_por_segundo
        
        return tempo_estimado
    
    def prever_xp_proxima_hora(self) -> float:
        """
        Prevê quanto XP será ganho na próxima hora
        
        Returns:
            XP estimado
        """
        xp_medio = self.padroes.get('xp_medio_kill', 0)
        tempo_medio = self.padroes.get('tempo_medio_kill', 0)
        
        if tempo_medio <= 0:
            return 0
        
        # Kills por hora
        kills_por_hora = 3600 / tempo_medio
        
        # XP total
        xp_estimado = kills_por_hora * xp_medio
        
        return xp_estimado
    
    def prever_level_up(self, xp_atual: float, xp_para_level: float = 100) -> Optional[datetime]:
        """
        Prevê quando chegará a 100% de XP
        
        Args:
            xp_atual: XP atual (%)
            xp_para_level: XP necessário (%)
        
        Returns:
            Data/hora estimada do level up
        """
        xp_faltante = xp_para_level - xp_atual
        
        if xp_faltante <= 0:
            return datetime.now()
        
        xp_por_hora = self.prever_xp_proxima_hora()
        
        if xp_por_hora <= 0:
            return None
        
        # Horas necessárias
        horas = xp_faltante / xp_por_hora
        
        # Adiciona ao horário atual
        level_up_em = datetime.now() + timedelta(hours=horas)
        
        return level_up_em
    
    def detectar_padroes_temporais(self) -> Dict[str, Any]:
        """
        Detecta padrões de performance por horário
        
        Returns:
            Padrões detectados
        """
        if len(self.historico_xp) < 20:
            return {'status': 'dados_insuficientes'}
        
        # Agrupa por hora do dia
        xp_por_hora = defaultdict(list)
        
        for registro in self.historico_xp[-100:]:
            hora = registro['timestamp'].hour
            xp_por_hora[hora].append(registro['xp'])
        
        # Calcula média por hora
        medias = {
            hora: np.mean(xps)
            for hora, xps in xp_por_hora.items()
            if len(xps) >= 3
        }
        
        if not medias:
            return {'status': 'dados_insuficientes'}
        
        # Encontra melhor e pior horário
        melhor_hora = max(medias, key=medias.get)
        pior_hora = min(medias, key=medias.get)
        
        return {
            'status': 'padroes_detectados',
            'melhor_horario': melhor_hora,
            'xp_melhor_horario': medias[melhor_hora],
            'pior_horario': pior_hora,
            'xp_pior_horario': medias[pior_hora],
            'todas_medias': medias
        }
    
    def sugerir_melhor_horario(self) -> str:
        """
        Sugere melhor horário para farmar
        
        Returns:
            Sugestão de horário
        """
        padroes = self.detectar_padroes_temporais()
        
        if padroes.get('status') != 'padroes_detectados':
            return "⚠️ Dados insuficientes para sugestão (mínimo 20 combates)"
        
        melhor = padroes['melhor_horario']
        pior = padroes['pior_horario']
        
        sugestao = f"""
╔══════════════════════════════════════════════════════════════╗
║           ⏰ ANÁLISE DE HORÁRIOS DE FARMING                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🌟 MELHOR HORÁRIO: {melhor:02d}:00 - {(melhor+1)%24:02d}:00                         ║
║     XP médio: {padroes['xp_melhor_horario']:.3f}% por kill                       ║
║                                                              ║
║  📉 PIOR HORÁRIO: {pior:02d}:00 - {(pior+1)%24:02d}:00                           ║
║     XP médio: {padroes['xp_pior_horario']:.3f}% por kill                         ║
║                                                              ║
║  💡 SUGESTÃO:                                                ║
║     Farme durante {melhor:02d}:00 - {(melhor+1)%24:02d}:00 para máxima eficiência  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        return sugestao
    
    def alertas_proativos(self, estado_atual: Dict[str, Any]) -> List[str]:
        """
        Gera alertas baseados em predições
        
        Args:
            estado_atual: {
                'hp': 75,
                'em_combate': True,
                'xp_atual': 45.5
            }
        
        Returns:
            Lista de alertas
        """
        alertas = []
        
        # Alerta de HP
        if estado_atual.get('em_combate'):
            tempo_hp = self.prever_tempo_ate_hp_baixo(estado_atual.get('hp', 100))
            if tempo_hp is not None and tempo_hp < 10:
                alertas.append(f"⚠️ HP ficará baixo em ~{tempo_hp:.0f}s - Prepare potion!")
        
        # Alerta de XP
        level_up = self.prever_level_up(estado_atual.get('xp_atual', 0))
        if level_up:
            tempo_restante = (level_up - datetime.now()).total_seconds()
            if tempo_restante < 600:  # Menos de 10 minutos
                alertas.append(f"🎉 Level UP estimado em {tempo_restante/60:.0f} minutos!")
        
        # Alerta de horário
        padroes = self.detectar_padroes_temporais()
        if padroes.get('status') == 'padroes_detectados':
            hora_atual = datetime.now().hour
            if hora_atual == padroes.get('melhor_horario'):
                alertas.append("⭐ Você está no melhor horário para farming!")
            elif hora_atual == padroes.get('pior_horario'):
                alertas.append("📉 Horário de baixa eficiência - Considere pausar")
        
        return alertas


if __name__ == "__main__":
    print("🔮 SISTEMA DE PREDIÇÃO DE EVENTOS")
    print("="*70)
    
    predicao = PredicaoEventos()
    
    # Simula alguns combates
    for i in range(20):
        predicao.registrar_combate({
            'hp_inicial': 100,
            'hp_final': 85 + np.random.randint(-10, 10),
            'duracao': 8 + np.random.uniform(-2, 2),
            'xp_ganho': 0.05 + np.random.uniform(-0.01, 0.01)
        })
    
    # Testa predições
    print("\n📊 PREDIÇÕES:")
    print(f"  XP/hora estimado: {predicao.prever_xp_proxima_hora():.2f}%")
    
    level_up = predicao.prever_level_up(45.5)
    if level_up:
        print(f"  Level UP em: {level_up.strftime('%H:%M:%S')}")
    
    tempo_hp = predicao.prever_tempo_ate_hp_baixo(75)
    if tempo_hp:
        print(f"  HP baixo em: {tempo_hp:.0f}s")
    
    print("\n" + predicao.sugerir_melhor_horario())
