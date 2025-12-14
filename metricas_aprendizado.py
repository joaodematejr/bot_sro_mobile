#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Métricas de Aprendizado ML
Monitora e visualiza o progresso do treinamento
"""

import json
import pickle
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Tuple
import statistics

class MetricasAprendizadoML:
    """
    Sistema completo de métricas de Machine Learning
    Monitora progresso, detecta melhorias e fornece insights
    """
    
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)
        self.ml_models_dir = self.workspace / "ml_models"
        self.metrics_file = self.ml_models_dir / "training_metrics.json"
        
        # Histórico de métricas
        self.training_history = {
            'samples_timeline': [],      # [(timestamp, sample_count)]
            'accuracy_timeline': [],     # [(timestamp, accuracy)]
            'loss_timeline': [],         # [(timestamp, loss)]
            'training_times': [],        # [(timestamp, duration_seconds)]
            'model_versions': []         # [(timestamp, version, sample_count)]
        }
        
        # Métricas da sessão atual
        self.current_session = {
            'start_time': datetime.now(),
            'samples_at_start': 0,
            'samples_added': 0,
            'trainings_performed': 0,
            'avg_sample_rate': 0.0  # samples/min
        }
        
        # Performance tracking
        self.performance_metrics = {
            'xp_rates_history': deque(maxlen=100),
            'kill_rates_history': deque(maxlen=100),
            'combat_duration_history': deque(maxlen=100),
            'correlation_ml_performance': 0.0
        }
        
        # Carrega histórico
        self.load_metrics()
    
    def load_metrics(self):
        """Carrega métricas salvas anteriormente"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Restaura timelines
                    if 'training_history' in data:
                        for key in ['samples_timeline', 'accuracy_timeline', 'loss_timeline', 
                                   'training_times', 'model_versions']:
                            if key in data['training_history']:
                                self.training_history[key] = data['training_history'][key]
                    
                    # Restaura performance
                    if 'performance_metrics' in data:
                        perf = data['performance_metrics']
                        for key, values in perf.items():
                            if key != 'correlation_ml_performance' and values:
                                self.performance_metrics[key] = deque(values, maxlen=100)
                        
                        self.performance_metrics['correlation_ml_performance'] = \
                            perf.get('correlation_ml_performance', 0.0)
                    
                    # Restaura sessão atual
                    if 'current_session' in data:
                        sess = data['current_session']
                        if 'start_time' in sess and isinstance(sess['start_time'], str):
                            sess['start_time'] = datetime.fromisoformat(sess['start_time'])
                        
                        # Atualiza apenas campos que existem
                        for key in ['samples_at_start', 'samples_added', 'trainings_performed', 'avg_sample_rate']:
                            if key in sess:
                                self.current_session[key] = sess[key]
                    
                    # Mostra estatísticas carregadas
                    total_samples = 0
                    if self.training_history['samples_timeline']:
                        total_samples = self.training_history['samples_timeline'][-1][1]
                    
                    print(f"✅ Métricas carregadas: {total_samples} amostras, {len(self.training_history['training_times'])} treinos")
                    
            except Exception as e:
                print(f"⚠️  Erro ao carregar métricas: {e}")
                import traceback
                traceback.print_exc()
    
    def save_metrics(self):
        """Salva métricas no disco"""
        self.ml_models_dir.mkdir(exist_ok=True)
        
        # Converte deques para listas
        perf_data = {
            k: list(v) if isinstance(v, deque) else v 
            for k, v in self.performance_metrics.items()
        }
        
        data = {
            'last_updated': datetime.now().isoformat(),
            'training_history': self.training_history,
            'current_session': {
                **self.current_session,
                'start_time': self.current_session['start_time'].isoformat()
            },
            'performance_metrics': perf_data
        }
        
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register_sample_collected(self, sample_count: int):
        """Registra coleta de nova amostra"""
        timestamp = datetime.now().isoformat()
        self.training_history['samples_timeline'].append([timestamp, sample_count])
        self.current_session['samples_added'] += 1
        
        # Calcula taxa de coleta
        if self.current_session['samples_added'] > 0:
            elapsed_min = (datetime.now() - self.current_session['start_time']).total_seconds() / 60
            if elapsed_min > 0:
                self.current_session['avg_sample_rate'] = \
                    self.current_session['samples_added'] / elapsed_min
        
        # Auto-save a cada 10 amostras
        if self.current_session['samples_added'] % 10 == 0:
            self.save_metrics()
    
    def register_training_completed(self, sample_count: int, duration: float, 
                                    accuracy: float = None, loss: float = None):
        """Registra conclusão de treinamento"""
        timestamp = datetime.now().isoformat()
        
        self.training_history['training_times'].append([timestamp, duration])
        self.current_session['trainings_performed'] += 1
        
        if accuracy is not None:
            self.training_history['accuracy_timeline'].append([timestamp, accuracy])
        
        if loss is not None:
            self.training_history['loss_timeline'].append([timestamp, loss])
        
        # Registra versão do modelo
        version = f"v{len(self.training_history['model_versions']) + 1}"
        self.training_history['model_versions'].append([timestamp, version, sample_count])
        
        self.save_metrics()
        
        print(f"📊 Métricas de treino salvas - Duração: {duration:.2f}s, Amostras: {sample_count}")
    
    def register_performance_data(self, xp_rate: float = None, kill_rate: float = None, 
                                 combat_duration: float = None):
        """Registra dados de performance do farming"""
        if xp_rate is not None:
            self.performance_metrics['xp_rates_history'].append(xp_rate)
        
        if kill_rate is not None:
            self.performance_metrics['kill_rates_history'].append(kill_rate)
        
        if combat_duration is not None:
            self.performance_metrics['combat_duration_history'].append(combat_duration)
        
        # Recalcula correlação se temos dados suficientes
        if len(self.performance_metrics['xp_rates_history']) > 10:
            self._update_ml_correlation()
    
    def _update_ml_correlation(self):
        """Calcula correlação entre uso de ML e performance"""
        # Simplificado: compara performance recente vs histórica
        if len(self.performance_metrics['xp_rates_history']) < 20:
            return
        
        xp_rates = list(self.performance_metrics['xp_rates_history'])
        recent = xp_rates[-10:]
        historical = xp_rates[-20:-10]
        
        if len(historical) > 0 and len(recent) > 0:
            avg_recent = statistics.mean(recent)
            avg_historical = statistics.mean(historical)
            
            if avg_historical > 0:
                improvement = ((avg_recent - avg_historical) / avg_historical) * 100
                self.performance_metrics['correlation_ml_performance'] = improvement
    
    def get_training_progress(self) -> Dict[str, Any]:
        """Retorna progresso do treinamento"""
        total_samples = 0
        if self.training_history['samples_timeline']:
            total_samples = self.training_history['samples_timeline'][-1][1]
        
        progress = {
            'total_samples': total_samples,
            'total_trainings': len(self.training_history['training_times']),
            'current_session_samples': self.current_session['samples_added'],
            'sample_rate': self.current_session['avg_sample_rate'],
            'next_milestone': self._calculate_next_milestone(total_samples),
            'progress_to_milestone': self._calculate_milestone_progress(total_samples)
        }
        
        return progress
    
    def _calculate_next_milestone(self, current_samples: int) -> Tuple[str, int]:
        """Calcula próximo marco de amostras"""
        milestones = [10, 50, 100, 200, 500, 1000, 2000, 5000]
        
        for milestone in milestones:
            if current_samples < milestone:
                return f"{milestone} amostras", milestone
        
        # Se já passou de todos, próximo múltiplo de 1000
        next_k = ((current_samples // 1000) + 1) * 1000
        return f"{next_k} amostras", next_k
    
    def _calculate_milestone_progress(self, current_samples: int) -> float:
        """Calcula progresso até próximo marco (0-100%)"""
        milestone_name, milestone_value = self._calculate_next_milestone(current_samples)
        
        # Encontra marco anterior
        milestones = [0, 10, 50, 100, 200, 500, 1000, 2000, 5000]
        previous_milestone = 0
        
        for m in milestones:
            if m < milestone_value:
                previous_milestone = m
            else:
                break
        
        if milestone_value > previous_milestone:
            progress = ((current_samples - previous_milestone) / 
                       (milestone_value - previous_milestone)) * 100
            return min(100.0, max(0.0, progress))
        
        return 0.0
    
    def get_learning_curve(self) -> Dict[str, List]:
        """Retorna dados para plotar curva de aprendizado"""
        return {
            'samples': [s[1] for s in self.training_history['samples_timeline']],
            'timestamps': [s[0] for s in self.training_history['samples_timeline']],
            'accuracy': [a[1] for a in self.training_history['accuracy_timeline']],
            'accuracy_times': [a[0] for a in self.training_history['accuracy_timeline']],
            'training_durations': [t[1] for t in self.training_history['training_times']]
        }
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Analisa tendências de performance"""
        trends = {
            'xp_rate': self._analyze_trend(list(self.performance_metrics['xp_rates_history'])),
            'kill_rate': self._analyze_trend(list(self.performance_metrics['kill_rates_history'])),
            'combat_duration': self._analyze_trend(
                list(self.performance_metrics['combat_duration_history']), 
                lower_is_better=True
            ),
            'ml_correlation': self.performance_metrics['correlation_ml_performance']
        }
        
        return trends
    
    def _analyze_trend(self, values: List[float], lower_is_better: bool = False) -> Dict[str, Any]:
        """Analisa tendência de uma métrica"""
        if len(values) < 5:
            return {
                'status': 'insufficient_data',
                'current': 0,
                'trend': 'unknown',
                'change_percent': 0
            }
        
        # Últimos 10 vs 10 anteriores
        recent_size = min(10, len(values) // 2)
        recent = values[-recent_size:]
        previous = values[-recent_size*2:-recent_size] if len(values) >= recent_size*2 else values[:-recent_size]
        
        current_avg = statistics.mean(recent)
        previous_avg = statistics.mean(previous) if previous else current_avg
        
        if previous_avg > 0:
            change = ((current_avg - previous_avg) / previous_avg) * 100
        else:
            change = 0
        
        # Determina tendência
        if lower_is_better:
            change = -change  # Inverte sinal para métricas onde menor é melhor
        
        if change > 5:
            trend = 'improving'
        elif change < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'status': 'analyzed',
            'current': current_avg,
            'previous': previous_avg,
            'trend': trend,
            'change_percent': change
        }
    
    def generate_progress_bar(self, current: int, target: int, width: int = 50) -> str:
        """Gera barra de progresso visual"""
        if target <= 0:
            return "[" + "=" * width + "]"
        
        filled = int((current / target) * width)
        filled = min(filled, width)
        
        bar = "█" * filled + "░" * (width - filled)
        percentage = min(100, (current / target) * 100)
        
        return f"[{bar}] {percentage:.1f}%"
    
    def print_live_dashboard(self):
        """Exibe dashboard ao vivo das métricas"""
        progress = self.get_training_progress()
        trends = self.get_performance_trends()
        
        print("\n" + "="*80)
        print("🧠 DASHBOARD DE APRENDIZADO ML")
        print("="*80)
        
        # Seção 1: Progresso de Coleta
        print("\n📊 PROGRESSO DE TREINAMENTO")
        print("-"*80)
        print(f"Total de amostras: {progress['total_samples']}")
        print(f"Trainings realizados: {progress['total_trainings']}")
        
        milestone_name, milestone_value = progress['next_milestone']
        print(f"\nPróximo marco: {milestone_name}")
        bar = self.generate_progress_bar(
            progress['total_samples'], 
            milestone_value,
            width=40
        )
        print(f"{bar} ({progress['total_samples']}/{milestone_value})")
        
        # Sessão atual
        print(f"\n📈 Sessão Atual:")
        print(f"  Amostras coletadas: {progress['current_session_samples']}")
        print(f"  Taxa de coleta: {progress['sample_rate']:.2f} amostras/min")
        
        # Seção 2: Performance
        print("\n🎯 TENDÊNCIAS DE PERFORMANCE")
        print("-"*80)
        
        xp_trend = trends['xp_rate']
        if xp_trend['status'] == 'analyzed':
            emoji = self._get_trend_emoji(xp_trend['trend'])
            print(f"XP/min: {emoji} {xp_trend['current']:.4f}% ({xp_trend['change_percent']:+.1f}%)")
        
        kill_trend = trends['kill_rate']
        if kill_trend['status'] == 'analyzed':
            emoji = self._get_trend_emoji(kill_trend['trend'])
            print(f"Kills/min: {emoji} {kill_trend['current']:.2f} ({kill_trend['change_percent']:+.1f}%)")
        
        combat_trend = trends['combat_duration']
        if combat_trend['status'] == 'analyzed':
            emoji = self._get_trend_emoji(combat_trend['trend'])
            print(f"Duração combate: {emoji} {combat_trend['current']:.1f}s ({combat_trend['change_percent']:+.1f}%)")
        
        # Correlação ML
        if abs(trends['ml_correlation']) > 0.1:
            print(f"\n🔗 Impacto do ML: {trends['ml_correlation']:+.1f}%")
            if trends['ml_correlation'] > 5:
                print("   ✅ ML está melhorando a performance!")
            elif trends['ml_correlation'] < -5:
                print("   ⚠️  ML pode estar prejudicando - revisar parâmetros")
        
        print("\n" + "="*80)
    
    def _get_trend_emoji(self, trend: str) -> str:
        """Retorna emoji para tendência"""
        if trend == 'improving':
            return '📈'
        elif trend == 'declining':
            return '📉'
        else:
            return '➡️'
    
    def generate_summary_report(self) -> str:
        """Gera relatório resumido de métricas"""
        progress = self.get_training_progress()
        trends = self.get_performance_trends()
        
        report = []
        report.append("="*80)
        report.append("📊 RESUMO DE MÉTRICAS DE APRENDIZADO")
        report.append("="*80)
        report.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        # Dados de treinamento
        report.append("🎓 TREINAMENTO")
        report.append("-"*80)
        report.append(f"Total de amostras: {progress['total_samples']}")
        report.append(f"Modelos treinados: {progress['total_trainings']}")
        
        if self.training_history['training_times']:
            durations = [t[1] for t in self.training_history['training_times']]
            avg_duration = statistics.mean(durations)
            report.append(f"Tempo médio de treino: {avg_duration:.2f}s")
        
        milestone_name, milestone_value = progress['next_milestone']
        report.append(f"\nPróximo marco: {milestone_name}")
        report.append(f"Progresso: {progress['progress_to_milestone']:.1f}%")
        
        # Performance
        report.append("\n🎯 PERFORMANCE")
        report.append("-"*80)
        
        for metric_name, trend_key in [
            ('XP/min', 'xp_rate'),
            ('Kills/min', 'kill_rate'),
            ('Duração combate', 'combat_duration')
        ]:
            trend = trends[trend_key]
            if trend['status'] == 'analyzed':
                emoji = self._get_trend_emoji(trend['trend'])
                report.append(f"{metric_name}: {emoji} {trend['current']:.2f} ({trend['change_percent']:+.1f}%)")
        
        # Insights
        report.append("\n💡 INSIGHTS")
        report.append("-"*80)
        
        insights = self._generate_insights(progress, trends)
        for insight in insights:
            report.append(f"  {insight}")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)
    
    def _generate_insights(self, progress: Dict, trends: Dict) -> List[str]:
        """Gera insights baseados nos dados"""
        insights = []
        
        # Progresso de coleta
        if progress['total_samples'] < 10:
            insights.append("⚠️  Poucas amostras - continue coletando para treinar modelos")
        elif progress['total_samples'] < 100:
            insights.append("📈 Bom progresso - meta de 100 amostras em vista")
        elif progress['total_samples'] >= 100:
            insights.append("✅ Dados suficientes para modelos robustos")
        
        # Taxa de coleta
        if progress['sample_rate'] > 1.0:
            insights.append(f"🔥 Alta taxa de coleta: {progress['sample_rate']:.1f}/min")
        elif progress['sample_rate'] > 0.5:
            insights.append(f"👍 Boa taxa de coleta: {progress['sample_rate']:.1f}/min")
        
        # Tendências
        xp_trend = trends['xp_rate']
        if xp_trend['status'] == 'analyzed':
            if xp_trend['trend'] == 'improving':
                insights.append("📈 XP/min melhorando - bom trabalho!")
            elif xp_trend['trend'] == 'declining':
                insights.append("📉 XP/min caindo - verificar configurações")
        
        # Impacto ML
        ml_impact = trends['ml_correlation']
        if ml_impact > 10:
            insights.append(f"🚀 ML boosting performance: +{ml_impact:.1f}%")
        elif ml_impact < -10:
            insights.append(f"⚠️  ML reduzindo performance: {ml_impact:.1f}%")
        
        # Próximo milestone
        milestone_name, _ = progress['next_milestone']
        if progress['progress_to_milestone'] > 80:
            insights.append(f"🎯 Quase alcançando {milestone_name}!")
        
        return insights if insights else ["✅ Sistema operando normalmente"]
    
    def export_detailed_metrics(self, filename: str = None) -> str:
        """Exporta métricas detalhadas para JSON"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"metricas_ml_detalhadas_{timestamp}.json"
        
        filepath = self.workspace / filename
        
        data = {
            'export_date': datetime.now().isoformat(),
            'training_history': self.training_history,
            'current_session': {
                **self.current_session,
                'start_time': self.current_session['start_time'].isoformat()
            },
            'performance_metrics': {
                'xp_rates': list(self.performance_metrics['xp_rates_history']),
                'kill_rates': list(self.performance_metrics['kill_rates_history']),
                'combat_durations': list(self.performance_metrics['combat_duration_history']),
                'ml_correlation': self.performance_metrics['correlation_ml_performance']
            },
            'progress': self.get_training_progress(),
            'trends': self.get_performance_trends()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)


def monitor_training_progress(interval: int = 30):
    """
    Monitora progresso do treinamento em tempo real
    interval: segundos entre atualizações
    """
    metricas = MetricasAprendizadoML()
    
    print("🔄 Monitoramento iniciado (Ctrl+C para parar)")
    print(f"Atualizando a cada {interval} segundos...\n")
    
    try:
        while True:
            metricas.load_metrics()  # Recarrega dados
            metricas.print_live_dashboard()
            print(f"\n⏱️  Próxima atualização em {interval}s...")
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\n👋 Monitoramento encerrado")
        print("\n" + metricas.generate_summary_report())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'monitor':
        # Modo monitor
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        monitor_training_progress(interval)
    else:
        # Exibe dashboard único
        metricas = MetricasAprendizadoML()
        metricas.print_live_dashboard()
        print("\n" + metricas.generate_summary_report())
        
        # Opção de exportar
        print("\n💾 Exportar métricas detalhadas? (s/n): ", end='')
        if input().lower() == 's':
            filepath = metricas.export_detailed_metrics()
            print(f"✅ Exportado para: {filepath}")
