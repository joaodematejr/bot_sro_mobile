#!/usr/bin/env python3
"""
Analytics System - Sistema de estatísticas e análise de farming
Tracking de XP, combates, previsões e métricas detalhadas
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import statistics
from collections import defaultdict


class FarmingAnalytics:
    """Sistema completo de analytics para farming"""
    
    def __init__(self, data_folder: str = "analytics_data"):
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(exist_ok=True)
        
        # Sessão atual
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_start = datetime.now()
        
        # Tracking de XP
        self.xp_history = []  # [(timestamp, xp_percentage)]
        self.xp_gains = []    # [(timestamp, xp_amount)]
        self.current_xp = 0.0
        self.initial_xp = None
        
        # Combates
        self.combat_count = 0
        self.kills_count = 0
        self.deaths_count = 0
        self.combat_history = []  # [(timestamp, duration, result)]
        
        # Itens e recursos
        self.potions_used = {
            'hp': 0,
            'mp': 0,
            'vigor': 0
        }
        self.skills_used = defaultdict(int)  # {skill_name: count}
        self.loot_collected = []  # [(timestamp, item_name, quantity)]
        
        # Métricas de IA
        self.ai_detections = 0
        self.ai_movements = 0
        self.enemies_detected = []  # [(timestamp, count, positions)]
        
        # Performance
        self.actions_log = []  # [(timestamp, action_type, details)]
        
        # Carrega dados anteriores se existir
        self._load_session_data()
    
    def update_xp(self, xp_percentage: float):
        """Atualiza XP atual via OCR"""
        now = datetime.now()
        
        if self.initial_xp is None:
            self.initial_xp = xp_percentage
        
        self.current_xp = xp_percentage
        self.xp_history.append({
            'timestamp': now.isoformat(),
            'xp': xp_percentage
        })
    
    def add_xp_gain(self, xp_amount: float, source: str = 'combat'):
        """Registra ganho de XP (detectado após combate)"""
        now = datetime.now()
        
        self.xp_gains.append({
            'timestamp': now.isoformat(),
            'amount': xp_amount,
            'source': source
        })
    
    def register_combat(self, duration: float, killed: bool = True):
        """Registra combate"""
        now = datetime.now()
        
        self.combat_count += 1
        if killed:
            self.kills_count += 1
        
        self.combat_history.append({
            'timestamp': now.isoformat(),
            'duration': duration,
            'killed': killed
        })
    
    def register_death(self):
        """Registra morte do personagem"""
        self.deaths_count += 1
        self.actions_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'death',
            'details': {'deaths_total': self.deaths_count}
        })
    
    def register_potion(self, potion_type: str):
        """Registra uso de poção"""
        if potion_type in self.potions_used:
            self.potions_used[potion_type] += 1
            self.actions_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'potion',
                'details': {'type': potion_type, 'total': self.potions_used[potion_type]}
            })
    
    def register_skill(self, skill_name: str):
        """Registra uso de skill"""
        self.skills_used[skill_name] += 1
        self.actions_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'skill',
            'details': {'name': skill_name, 'total': self.skills_used[skill_name]}
        })
    
    def register_loot(self, item_name: str, quantity: int = 1):
        """Registra loot coletado"""
        now = datetime.now()
        
        self.loot_collected.append({
            'timestamp': now.isoformat(),
            'item': item_name,
            'quantity': quantity
        })
    
    def register_ai_detection(self, enemies_count: int, positions: List[Tuple[int, int]] = None):
        """Registra detecção de IA"""
        now = datetime.now()
        
        self.ai_detections += 1
        self.enemies_detected.append({
            'timestamp': now.isoformat(),
            'count': enemies_count,
            'positions': positions or []
        })
    
    def register_ai_movement(self, direction: str):
        """Registra movimento inteligente"""
        self.ai_movements += 1
        self.actions_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'ai_movement',
            'details': {'direction': direction, 'total_movements': self.ai_movements}
        })
    
    def get_xp_per_minute(self) -> float:
        """Calcula XP/min baseado no histórico"""
        if len(self.xp_history) < 2:
            return 0.0
        
        # Usa primeiros e últimos 5 registros para média
        first_samples = self.xp_history[:5]
        last_samples = self.xp_history[-5:]
        
        first_avg = sum(s['xp'] for s in first_samples) / len(first_samples)
        last_avg = sum(s['xp'] for s in last_samples) / len(last_samples)
        
        xp_gained = last_avg - first_avg
        
        # Calcula tempo decorrido
        first_time = datetime.fromisoformat(first_samples[0]['timestamp'])
        last_time = datetime.fromisoformat(last_samples[-1]['timestamp'])
        minutes = (last_time - first_time).total_seconds() / 60
        
        if minutes > 0:
            return xp_gained / minutes
        
        return 0.0
    
    def predict_time_to_level(self) -> Optional[timedelta]:
        """Prevê tempo para atingir 100% de XP"""
        xp_per_min = self.get_xp_per_minute()
        
        if xp_per_min <= 0 or self.current_xp >= 100:
            return None
        
        xp_remaining = 100 - self.current_xp
        minutes_needed = xp_remaining / xp_per_min
        
        return timedelta(minutes=minutes_needed)
    
    def get_average_xp_per_kill(self) -> float:
        """Calcula XP médio por kill"""
        if not self.xp_gains:
            return 0.0
        
        combat_gains = [g['amount'] for g in self.xp_gains if g['source'] == 'combat']
        if combat_gains:
            return statistics.mean(combat_gains)
        
        return 0.0
    
    def get_kills_per_minute(self) -> float:
        """Calcula kills por minuto"""
        if self.kills_count == 0:
            return 0.0
        
        elapsed = (datetime.now() - self.session_start).total_seconds() / 60
        if elapsed > 0:
            return self.kills_count / elapsed
        
        return 0.0
    
    def get_combat_efficiency(self) -> Dict[str, Any]:
        """Calcula eficiência de combate"""
        if not self.combat_history:
            return {
                'avg_combat_duration': 0,
                'kill_rate': 0,
                'combat_per_minute': 0
            }
        
        durations = [c['duration'] for c in self.combat_history if c['duration'] > 0]
        avg_duration = statistics.mean(durations) if durations else 0
        
        kill_rate = (self.kills_count / self.combat_count * 100) if self.combat_count > 0 else 0
        
        elapsed = (datetime.now() - self.session_start).total_seconds() / 60
        combat_per_min = self.combat_count / elapsed if elapsed > 0 else 0
        
        return {
            'avg_combat_duration': round(avg_duration, 2),
            'kill_rate': round(kill_rate, 2),
            'combat_per_minute': round(combat_per_min, 2)
        }
    
    def get_loot_summary(self) -> Dict[str, int]:
        """Resumo de loots coletados"""
        loot_counts = defaultdict(int)
        
        for loot in self.loot_collected:
            loot_counts[loot['item']] += loot['quantity']
        
        return dict(loot_counts)
    
    def get_current_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas atuais da sessão"""
        elapsed = datetime.now() - self.session_start
        elapsed_minutes = elapsed.total_seconds() / 60
        
        xp_per_min = self.get_xp_per_minute()
        time_to_level = self.predict_time_to_level()
        
        stats = {
            'session': {
                'id': self.session_id,
                'start': self.session_start.isoformat(),
                'elapsed': str(elapsed).split('.')[0],
                'elapsed_minutes': round(elapsed_minutes, 2)
            },
            'xp': {
                'current': self.current_xp,
                'initial': self.initial_xp,
                'gained': round(self.current_xp - self.initial_xp, 2) if self.initial_xp else 0,
                'xp_per_minute': round(xp_per_min, 4),
                'time_to_level': str(time_to_level).split('.')[0] if time_to_level else 'N/A',
                'total_readings': len(self.xp_history),
                'xp_gains_detected': len(self.xp_gains),
                'avg_xp_per_kill': round(self.get_average_xp_per_kill(), 4)
            },
            'combat': {
                'total_combats': self.combat_count,
                'kills': self.kills_count,
                'deaths': self.deaths_count,
                'kills_per_minute': round(self.get_kills_per_minute(), 2),
                **self.get_combat_efficiency()
            },
            'resources': {
                'potions_used': dict(self.potions_used),
                'total_potions': sum(self.potions_used.values()),
                'skills_used': dict(self.skills_used),
                'total_skills': sum(self.skills_used.values())
            },
            'loot': {
                'items_collected': self.get_loot_summary(),
                'total_items': len(self.loot_collected),
                'unique_items': len(self.get_loot_summary())
            },
            'ai': {
                'detections': self.ai_detections,
                'movements': self.ai_movements,
                'enemies_spotted': len(self.enemies_detected),
                'avg_enemies_per_detection': round(
                    statistics.mean([e['count'] for e in self.enemies_detected])
                    if self.enemies_detected else 0, 2
                )
            }
        }
        
        return stats
    
    def export_metrics(self, filename: str = None) -> str:
        """Exporta métricas completas para JSON"""
        if filename is None:
            filename = f"metrics_{self.session_id}.json"
        
        filepath = self.data_folder / filename
        
        metrics = {
            'session': {
                'id': self.session_id,
                'start': self.session_start.isoformat(),
                'end': datetime.now().isoformat(),
                'duration': str(datetime.now() - self.session_start).split('.')[0]
            },
            'statistics': self.get_current_statistics(),
            'detailed_data': {
                'xp_history': self.xp_history[-100:],  # Últimas 100 leituras
                'xp_gains': self.xp_gains,
                'combat_history': self.combat_history[-50:],  # Últimos 50 combates
                'loot_collected': self.loot_collected[-100:],  # Últimos 100 loots
                'enemies_detected': self.enemies_detected[-50:],  # Últimas 50 detecções
                'actions_log': self.actions_log[-200:]  # Últimas 200 ações
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _save_session_data(self):
        """Salva dados da sessão atual"""
        filepath = self.data_folder / f"session_{self.session_id}.json"
        
        data = {
            'session_id': self.session_id,
            'session_start': self.session_start.isoformat(),
            'current_xp': self.current_xp,
            'initial_xp': self.initial_xp,
            'xp_history': self.xp_history,
            'xp_gains': self.xp_gains,
            'combat_count': self.combat_count,
            'kills_count': self.kills_count,
            'deaths_count': self.deaths_count,
            'combat_history': self.combat_history,
            'potions_used': self.potions_used,
            'skills_used': dict(self.skills_used),
            'loot_collected': self.loot_collected,
            'ai_detections': self.ai_detections,
            'ai_movements': self.ai_movements,
            'enemies_detected': self.enemies_detected,
            'actions_log': self.actions_log
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_session_data(self):
        """Carrega dados de sessão anterior (se disponível)"""
        sessions = sorted(self.data_folder.glob("session_*.json"))
        
        if sessions:
            latest = sessions[-1]
            try:
                with open(latest, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Carrega dados
                self.xp_history = data.get('xp_history', [])
                self.xp_gains = data.get('xp_gains', [])
                self.current_xp = data.get('current_xp', 0.0)
                self.initial_xp = data.get('initial_xp')
                self.combat_count = data.get('combat_count', 0)
                self.kills_count = data.get('kills_count', 0)
                self.deaths_count = data.get('deaths_count', 0)
                self.combat_history = data.get('combat_history', [])
                self.potions_used = data.get('potions_used', {'hp': 0, 'mp': 0, 'vigor': 0})
                self.skills_used = defaultdict(int, data.get('skills_used', {}))
                self.loot_collected = data.get('loot_collected', [])
                self.ai_detections = data.get('ai_detections', 0)
                self.ai_movements = data.get('ai_movements', 0)
                self.enemies_detected = data.get('enemies_detected', [])
                self.actions_log = data.get('actions_log', [])
                
                print(f"✓ Dados da sessão anterior carregados ({latest.name})")
                
            except Exception as e:
                print(f"⚠️ Erro ao carregar sessão anterior: {e}")
    
    def auto_save(self):
        """Auto-save periódico dos dados"""
        self._save_session_data()
    
    def generate_report(self) -> str:
        """Gera relatório formatado de estatísticas"""
        stats = self.get_current_statistics()
        
        report = []
        report.append("=" * 70)
        report.append("  📊 RELATÓRIO DE ANALYTICS - FARMING")
        report.append("=" * 70)
        
        # Sessão
        report.append(f"\n📅 SESSÃO")
        report.append(f"  ID: {stats['session']['id']}")
        report.append(f"  Início: {stats['session']['start']}")
        report.append(f"  Duração: {stats['session']['elapsed']}")
        
        # XP
        report.append(f"\n📈 EXPERIÊNCIA")
        report.append(f"  XP Atual: {stats['xp']['current']:.2f}%")
        if stats['xp']['initial']:
            report.append(f"  XP Inicial: {stats['xp']['initial']:.2f}%")
            report.append(f"  XP Ganho: {stats['xp']['gained']:.2f}%")
        report.append(f"  XP/min: {stats['xp']['xp_per_minute']:.4f}%")
        report.append(f"  Tempo para Level: {stats['xp']['time_to_level']}")
        report.append(f"  Leituras de XP: {stats['xp']['total_readings']}")
        report.append(f"  XP médio/kill: {stats['xp']['avg_xp_per_kill']:.4f}%")
        
        # Combate
        report.append(f"\n⚔️  COMBATE")
        report.append(f"  Total de combates: {stats['combat']['total_combats']}")
        report.append(f"  Kills: {stats['combat']['kills']}")
        report.append(f"  Mortes: {stats['combat']['deaths']}")
        report.append(f"  Kills/min: {stats['combat']['kills_per_minute']:.2f}")
        report.append(f"  Taxa de kill: {stats['combat']['kill_rate']:.1f}%")
        report.append(f"  Duração média combate: {stats['combat']['avg_combat_duration']:.2f}s")
        report.append(f"  Combates/min: {stats['combat']['combat_per_minute']:.2f}")
        
        # Recursos
        report.append(f"\n💊 RECURSOS")
        report.append(f"  Poções HP: {stats['resources']['potions_used']['hp']}")
        report.append(f"  Poções MP: {stats['resources']['potions_used']['mp']}")
        report.append(f"  Poções Vigor: {stats['resources']['potions_used']['vigor']}")
        report.append(f"  Total poções: {stats['resources']['total_potions']}")
        
        if stats['resources']['skills_used']:
            report.append(f"\n🎯 SKILLS USADAS")
            for skill, count in sorted(stats['resources']['skills_used'].items(), 
                                      key=lambda x: x[1], reverse=True):
                report.append(f"  {skill}: {count}x")
        
        # Loot
        if stats['loot']['items_collected']:
            report.append(f"\n💰 LOOT COLETADO")
            for item, count in sorted(stats['loot']['items_collected'].items(), 
                                     key=lambda x: x[1], reverse=True):
                report.append(f"  {item}: {count}x")
            report.append(f"  Total: {stats['loot']['total_items']} itens ({stats['loot']['unique_items']} únicos)")
        
        # IA
        report.append(f"\n🧠 INTELIGÊNCIA ARTIFICIAL")
        report.append(f"  Detecções: {stats['ai']['detections']}")
        report.append(f"  Movimentos IA: {stats['ai']['movements']}")
        report.append(f"  Inimigos detectados: {stats['ai']['enemies_spotted']} vezes")
        report.append(f"  Média inimigos/detecção: {stats['ai']['avg_enemies_per_detection']:.1f}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)
    
    def print_live_stats(self, compact: bool = False) -> str:
        """Retorna string formatada para display em tempo real"""
        stats = self.get_current_statistics()
        
        if compact:
            # Versão compacta para display inline
            xp = stats['xp']
            combat = stats['combat']
            
            return (f"XP:{xp['current']:.1f}%({xp['xp_per_minute']:.3f}/min) | "
                   f"Kills:{combat['kills']}({combat['kills_per_minute']:.1f}/min) | "
                   f"Deaths:{combat['deaths']} | "
                   f"TTL:{xp['time_to_level']}")
        else:
            # Versão expandida
            return self.generate_report()
