#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relatório de Métricas de Aprendizado
Analisa o progresso do ML, IA e eficiência do bot
"""

import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from typing import Dict, List, Any, Optional

class RelatorioAprendizado:
    """Gera relatórios detalhados sobre o aprendizado do bot"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)
        self.ml_models_dir = self.workspace / "ml_models"
        self.analytics_dir = self.workspace / "analytics_data"
        self.training_data_dir = self.workspace / "treino_ml"
        self.exp_gain_dir = self.workspace / "exp_ganho_treino"
        self.training_metrics_file = self.ml_models_dir / "training_metrics.json"
    
    def load_training_metrics(self) -> Dict[str, Any]:
        """Carrega métricas de treinamento ML"""
        metrics = {
            'total_samples': 0,
            'total_trainings': 0,
            'samples_timeline': [],
            'training_times': [],
            'avg_training_time': 0,
            'sample_rate': 0,
            'sessions_data': []
        }
        
        if not self.training_metrics_file.exists():
            return metrics
        
        try:
            with open(self.training_metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if 'training_history' in data:
                    hist = data['training_history']
                    
                    # Samples timeline
                    if 'samples_timeline' in hist and hist['samples_timeline']:
                        metrics['samples_timeline'] = hist['samples_timeline']
                        metrics['total_samples'] = hist['samples_timeline'][-1][1]
                    
                    # Training times
                    if 'training_times' in hist and hist['training_times']:
                        metrics['training_times'] = hist['training_times']
                        metrics['total_trainings'] = len(hist['training_times'])
                        
                        durations = [t[1] for t in hist['training_times']]
                        metrics['avg_training_time'] = statistics.mean(durations)
                
                # Current session
                if 'current_session' in data:
                    sess = data['current_session']
                    metrics['sample_rate'] = sess.get('avg_sample_rate', 0)
                    
                    # Simula dados de sessão
                    if sess.get('samples_added', 0) > 0:
                        metrics['sessions_data'].append({
                            'start_time': sess.get('start_time', ''),
                            'samples_added': sess.get('samples_added', 0),
                            'trainings_performed': sess.get('trainings_performed', 0),
                            'sample_rate': sess.get('avg_sample_rate', 0)
                        })
        
        except Exception as e:
            print(f"⚠️  Erro ao carregar training_metrics.json: {e}")
        
        return metrics
        
    def load_ml_models_info(self) -> Dict[str, Any]:
        """Carrega informações dos modelos ML salvos"""
        models_info = {
            'models_found': [],
            'total_samples': 0,
            'last_training': None,
            'model_sizes': {}
        }
        
        if not self.ml_models_dir.exists():
            return models_info
        
        # Procura por arquivos de modelo
        model_files = [
            'modelo_sklearn.pkl',
            'modelo_ultra.pkl', 
            'modelo_ultra_adb.pkl',
            'ml_avancado_modelo.pkl',
            'density_model.pkl',
            'cluster_model.pkl',
            'scaler.pkl'
        ]
        
        for model_file in model_files:
            model_path = self.ml_models_dir / model_file
            if model_path.exists():
                models_info['models_found'].append(model_file)
                models_info['model_sizes'][model_file] = model_path.stat().st_size
                
                # Pega data de modificação
                mod_time = datetime.fromtimestamp(model_path.stat().st_mtime)
                if models_info['last_training'] is None or mod_time > models_info['last_training']:
                    models_info['last_training'] = mod_time
        
        # Tenta carregar dados de treino para contar amostras
        training_file = self.ml_models_dir / 'training_data.pkl'
        if training_file.exists():
            try:
                with open(training_file, 'rb') as f:
                    training_data = pickle.load(f)
                    models_info['total_samples'] = len(training_data)
            except Exception:
                pass
        
        return models_info
    
    def load_analytics_sessions(self) -> List[Dict[str, Any]]:
        """Carrega todas as sessões de analytics"""
        sessions = []
        
        if not self.analytics_dir.exists():
            return sessions
        
        for session_file in sorted(self.analytics_dir.glob('session_*.json')):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    sessions.append(session_data)
            except Exception:
                continue
        
        return sessions
    
    def analyze_training_images(self) -> Dict[str, Any]:
        """Analisa imagens de treino disponíveis"""
        analysis = {
            'minimap_images': 0,
            'exp_gain_images': 0,
            'total_size_mb': 0,
            'oldest_image': None,
            'newest_image': None
        }
        
        # Conta imagens de minimap
        if self.training_data_dir.exists():
            minimap_images = list(self.training_data_dir.glob('*.png'))
            analysis['minimap_images'] = len(minimap_images)
            
            if minimap_images:
                oldest = min(minimap_images, key=lambda p: p.stat().st_mtime)
                newest = max(minimap_images, key=lambda p: p.stat().st_mtime)
                analysis['oldest_image'] = datetime.fromtimestamp(oldest.stat().st_mtime)
                analysis['newest_image'] = datetime.fromtimestamp(newest.stat().st_mtime)
                analysis['total_size_mb'] += sum(p.stat().st_size for p in minimap_images) / (1024 * 1024)
        
        # Conta imagens de exp gain
        if self.exp_gain_dir.exists():
            exp_images = list(self.exp_gain_dir.glob('*.png'))
            analysis['exp_gain_images'] = len(exp_images)
            analysis['total_size_mb'] += sum(p.stat().st_size for p in exp_images) / (1024 * 1024)
        
        return analysis
    
    def calculate_learning_metrics(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Calcula métricas de aprendizado ao longo das sessões"""
        if not sessions:
            return {}
        
        metrics = {
            'total_sessions': len(sessions),
            'total_farming_time': timedelta(0),
            'xp_progression': [],
            'kill_efficiency_progression': [],
            'combat_duration_progression': [],
            'ai_usage_progression': [],
            'sessions_with_ml': 0
        }
        
        for session in sessions:
            # Tempo de farming
            if 'session_info' in session:
                duration_str = session['session_info'].get('duration', '0:00:00')
                try:
                    parts = duration_str.split(':')
                    if len(parts) == 3:
                        hours, minutes, seconds = map(int, parts)
                        metrics['total_farming_time'] += timedelta(hours=hours, minutes=minutes, seconds=seconds)
                except:
                    pass
            
            # XP/min progression
            if 'statistics' in session and 'xp' in session['statistics']:
                xp_per_min = session['statistics']['xp'].get('xp_per_minute', 0)
                if xp_per_min > 0:
                    metrics['xp_progression'].append(xp_per_min)
            
            # Kill efficiency
            if 'statistics' in session and 'combat' in session['statistics']:
                kills_per_min = session['statistics']['combat'].get('kills_per_minute', 0)
                if kills_per_min > 0:
                    metrics['kill_efficiency_progression'].append(kills_per_min)
                
                avg_duration = session['statistics']['combat'].get('avg_combat_duration', 0)
                if avg_duration > 0:
                    metrics['combat_duration_progression'].append(avg_duration)
            
            # AI usage
            if 'detailed_data' in session and 'ai_detections' in session['detailed_data']:
                ai_count = len(session['detailed_data']['ai_detections'])
                metrics['ai_usage_progression'].append(ai_count)
                if ai_count > 0:
                    metrics['sessions_with_ml'] += 1
        
        # Calcula tendências
        if len(metrics['xp_progression']) >= 2:
            metrics['xp_trend'] = self._calculate_trend(metrics['xp_progression'])
        
        if len(metrics['kill_efficiency_progression']) >= 2:
            metrics['kill_efficiency_trend'] = self._calculate_trend(metrics['kill_efficiency_progression'])
        
        if len(metrics['combat_duration_progression']) >= 2:
            metrics['combat_duration_trend'] = self._calculate_trend(metrics['combat_duration_progression'])
        
        return metrics
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcula tendência (melhorando/piorando/estável)"""
        if len(values) < 2:
            return "Dados insuficientes"
        
        # Compara primeira metade com segunda metade
        mid = len(values) // 2
        first_half_avg = statistics.mean(values[:mid])
        second_half_avg = statistics.mean(values[mid:])
        
        improvement = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if improvement > 5:
            return f"📈 Melhorando (+{improvement:.1f}%)"
        elif improvement < -5:
            return f"📉 Piorando ({improvement:.1f}%)"
        else:
            return "➡️ Estável"
    
    def calculate_ml_impact(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Analisa o impacto do ML na performance"""
        sessions_with_ml = [s for s in sessions if self._has_ml_data(s)]
        sessions_without_ml = [s for s in sessions if not self._has_ml_data(s)]
        
        impact = {
            'sessions_with_ml': len(sessions_with_ml),
            'sessions_without_ml': len(sessions_without_ml),
            'ml_xp_per_min': 0,
            'no_ml_xp_per_min': 0,
            'ml_kills_per_min': 0,
            'no_ml_kills_per_min': 0,
            'improvement_percentage': 0
        }
        
        if sessions_with_ml:
            xp_rates = [s['statistics']['xp']['xp_per_minute'] 
                       for s in sessions_with_ml 
                       if 'statistics' in s and 'xp' in s['statistics']]
            if xp_rates:
                impact['ml_xp_per_min'] = statistics.mean(xp_rates)
            
            kill_rates = [s['statistics']['combat']['kills_per_minute']
                         for s in sessions_with_ml
                         if 'statistics' in s and 'combat' in s['statistics']]
            if kill_rates:
                impact['ml_kills_per_min'] = statistics.mean(kill_rates)
        
        if sessions_without_ml:
            xp_rates = [s['statistics']['xp']['xp_per_minute']
                       for s in sessions_without_ml
                       if 'statistics' in s and 'xp' in s['statistics']]
            if xp_rates:
                impact['no_ml_xp_per_min'] = statistics.mean(xp_rates)
            
            kill_rates = [s['statistics']['combat']['kills_per_minute']
                         for s in sessions_without_ml
                         if 'statistics' in s and 'combat' in s['statistics']]
            if kill_rates:
                impact['no_ml_kills_per_min'] = statistics.mean(kill_rates)
        
        # Calcula melhoria
        if impact['no_ml_xp_per_min'] > 0:
            impact['improvement_percentage'] = (
                (impact['ml_xp_per_min'] - impact['no_ml_xp_per_min']) / 
                impact['no_ml_xp_per_min'] * 100
            )
        
        return impact
    
    def _has_ml_data(self, session: Dict) -> bool:
        """Verifica se sessão tem dados de ML/IA"""
        if 'detailed_data' not in session:
            return False
        
        ai_detections = session['detailed_data'].get('ai_detections', [])
        return len(ai_detections) > 0
    
    def generate_report(self) -> str:
        """Gera relatório completo de aprendizado"""
        # Coleta dados
        ml_info = self.load_ml_models_info()
        sessions = self.load_analytics_sessions()
        training_images = self.analyze_training_images()
        learning_metrics = self.calculate_learning_metrics(sessions)
        ml_impact = self.calculate_ml_impact(sessions)
        
        # Monta relatório
        report = []
        report.append("=" * 80)
        report.append("📊 RELATÓRIO DE MÉTRICAS DE APRENDIZADO")
        report.append("=" * 80)
        report.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        # Seção 1: Modelos ML
        report.append("🤖 MODELOS DE MACHINE LEARNING")
        report.append("-" * 80)
        if ml_info['models_found']:
            report.append(f"✅ Modelos treinados: {len(ml_info['models_found'])}")
            for model in ml_info['models_found']:
                size_kb = ml_info['model_sizes'][model] / 1024
                report.append(f"  • {model} ({size_kb:.1f} KB)")
            
            if ml_info['total_samples'] > 0:
                report.append(f"\n📊 Total de amostras coletadas: {ml_info['total_samples']}")
            
            if ml_info['last_training']:
                time_since = datetime.now() - ml_info['last_training']
                hours = int(time_since.total_seconds() // 3600)
                report.append(f"🕐 Último treinamento: {ml_info['last_training'].strftime('%d/%m/%Y %H:%M')}")
                report.append(f"   (há {hours} horas)")
        else:
            report.append("⚠️  Nenhum modelo treinado ainda")
            report.append("   Execute o bot com IA habilitada para começar a treinar")
        
        report.append("")
        
        # Seção 2: Dados de Treino
        report.append("📸 DADOS DE TREINAMENTO")
        report.append("-" * 80)
        report.append(f"Imagens de minimap: {training_images['minimap_images']}")
        report.append(f"Imagens de EXP gain: {training_images['exp_gain_images']}")
        report.append(f"Espaço total: {training_images['total_size_mb']:.2f} MB")
        
        if training_images['oldest_image'] and training_images['newest_image']:
            duration = training_images['newest_image'] - training_images['oldest_image']
            days = duration.days
            report.append(f"Período de coleta: {days} dias")
            report.append(f"  Primeira: {training_images['oldest_image'].strftime('%d/%m/%Y')}")
            report.append(f"  Última: {training_images['newest_image'].strftime('%d/%m/%Y')}")
        
        report.append("")
        
        # Seção 3: Progressão de Aprendizado
        if learning_metrics:
            report.append("📈 PROGRESSÃO DE APRENDIZADO")
            report.append("-" * 80)
            report.append(f"Total de sessões analisadas: {learning_metrics['total_sessions']}")
            report.append(f"Tempo total de farming: {str(learning_metrics['total_farming_time']).split('.')[0]}")
            report.append(f"Sessões com ML ativo: {learning_metrics['sessions_with_ml']}")
            
            if 'xp_trend' in learning_metrics:
                report.append(f"\nXP/min: {learning_metrics['xp_trend']}")
                if learning_metrics['xp_progression']:
                    avg = statistics.mean(learning_metrics['xp_progression'])
                    report.append(f"  Média: {avg:.4f}%/min")
            
            if 'kill_efficiency_trend' in learning_metrics:
                report.append(f"\nKills/min: {learning_metrics['kill_efficiency_trend']}")
                if learning_metrics['kill_efficiency_progression']:
                    avg = statistics.mean(learning_metrics['kill_efficiency_progression'])
                    report.append(f"  Média: {avg:.2f} kills/min")
            
            if 'combat_duration_trend' in learning_metrics:
                report.append(f"\nDuração de combate: {learning_metrics['combat_duration_trend']}")
                if learning_metrics['combat_duration_progression']:
                    avg = statistics.mean(learning_metrics['combat_duration_progression'])
                    report.append(f"  Média: {avg:.1f}s")
            
            report.append("")
        
        # Seção 4: Impacto do ML
        if ml_impact['sessions_with_ml'] > 0 and ml_impact['sessions_without_ml'] > 0:
            report.append("🎯 IMPACTO DO MACHINE LEARNING")
            report.append("-" * 80)
            report.append("Comparação: Com ML vs Sem ML\n")
            
            report.append("XP por minuto:")
            report.append(f"  Com ML: {ml_impact['ml_xp_per_min']:.4f}%/min")
            report.append(f"  Sem ML: {ml_impact['no_ml_xp_per_min']:.4f}%/min")
            
            if ml_impact['improvement_percentage'] > 0:
                report.append(f"  📈 Melhoria: +{ml_impact['improvement_percentage']:.1f}%")
            elif ml_impact['improvement_percentage'] < 0:
                report.append(f"  📉 Redução: {ml_impact['improvement_percentage']:.1f}%")
            
            report.append(f"\nKills por minuto:")
            report.append(f"  Com ML: {ml_impact['ml_kills_per_min']:.2f}")
            report.append(f"  Sem ML: {ml_impact['no_ml_kills_per_min']:.2f}")
            
            report.append("")
        
        # Seção 5: Recomendações
        report.append("💡 RECOMENDAÇÕES")
        report.append("-" * 80)
        
        recommendations = []
        
        if ml_info['total_samples'] < 100:
            recommendations.append("⚠️  Colete mais amostras (meta: 100+) para treinar modelos robustos")
        
        if ml_info['total_samples'] >= 100 and not ml_info['models_found']:
            recommendations.append("🎓 Dados suficientes! Execute force_train() para criar modelos")
        
        if training_images['minimap_images'] < 50:
            recommendations.append("📸 Capture mais imagens de minimap para melhorar detecção")
        
        if learning_metrics and 'xp_trend' in learning_metrics:
            if "Piorando" in learning_metrics['xp_trend']:
                recommendations.append("🔍 XP/min caindo - verifique configurações de farming")
        
        if ml_impact.get('improvement_percentage', 0) < -10:
            recommendations.append("⚙️  ML reduzindo performance - considere ajustar parâmetros")
        elif ml_impact.get('improvement_percentage', 0) > 10:
            recommendations.append("✅ ML melhorando performance significativamente!")
        
        if not recommendations:
            recommendations.append("✅ Sistema operando bem! Continue coletando dados.")
        
        for rec in recommendations:
            report.append(f"  {rec}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def export_metrics_json(self, filename: str = None) -> str:
        """Exporta métricas em formato JSON"""
        if filename is None:
            filename = f"metricas_aprendizado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.workspace / filename
        
        data = {
            'generated_at': datetime.now().isoformat(),
            'ml_models': self.load_ml_models_info(),
            'training_images': self.analyze_training_images(),
            'sessions': self.load_analytics_sessions(),
            'learning_metrics': self.calculate_learning_metrics(self.load_analytics_sessions()),
            'ml_impact': self.calculate_ml_impact(self.load_analytics_sessions())
        }
        
        # Converte datetime para string
        data = self._serialize_datetimes(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _serialize_datetimes(self, obj):
        """Converte datetime objects para string recursivamente"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self._serialize_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetimes(item) for item in obj]
        return obj


def main():
    """Menu interativo para visualizar relatórios"""
    relatorio = RelatorioAprendizado()
    
    while True:
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE MÉTRICAS DE APRENDIZADO")
        print("=" * 60)
        print("\n1. 📄 Ver relatório completo")
        print("2. 💾 Exportar métricas (JSON)")
        print("3. 🤖 Status dos modelos ML")
        print("4. 📸 Estatísticas de imagens")
        print("5. 📈 Análise de progressão")
        print("6. 🎯 Impacto do ML")
        print("0. ❌ Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '0':
            print("\n👋 Até logo!")
            break
        
        elif choice == '1':
            print("\n")
            print(relatorio.generate_report())
            input("\n\nPressione ENTER para continuar...")
        
        elif choice == '2':
            filepath = relatorio.export_metrics_json()
            print(f"\n✅ Métricas exportadas para: {filepath}")
            input("\nPressione ENTER para continuar...")
        
        elif choice == '3':
            ml_info = relatorio.load_ml_models_info()
            print("\n🤖 STATUS DOS MODELOS ML")
            print("-" * 60)
            if ml_info['models_found']:
                print(f"✅ Modelos encontrados: {len(ml_info['models_found'])}")
                for model in ml_info['models_found']:
                    size_kb = ml_info['model_sizes'][model] / 1024
                    print(f"  • {model} ({size_kb:.1f} KB)")
                print(f"\n📊 Amostras: {ml_info['total_samples']}")
                if ml_info['last_training']:
                    print(f"🕐 Último treino: {ml_info['last_training'].strftime('%d/%m/%Y %H:%M')}")
            else:
                print("⚠️  Nenhum modelo encontrado")
            input("\n\nPressione ENTER para continuar...")
        
        elif choice == '4':
            images = relatorio.analyze_training_images()
            print("\n📸 ESTATÍSTICAS DE IMAGENS")
            print("-" * 60)
            print(f"Minimap: {images['minimap_images']} imagens")
            print(f"EXP Gain: {images['exp_gain_images']} imagens")
            print(f"Espaço: {images['total_size_mb']:.2f} MB")
            if images['oldest_image']:
                print(f"\nPrimeira: {images['oldest_image'].strftime('%d/%m/%Y %H:%M')}")
                print(f"Última: {images['newest_image'].strftime('%d/%m/%Y %H:%M')}")
            input("\n\nPressione ENTER para continuar...")
        
        elif choice == '5':
            sessions = relatorio.load_analytics_sessions()
            
            # Se não tiver sessões de analytics, usa dados de training metrics
            if not sessions:
                training_metrics = relatorio.load_training_metrics()
                
                print("\n📈 ANÁLISE DE PROGRESSÃO (ML Training)")
                print("-" * 60)
                print(f"Total de amostras coletadas: {training_metrics['total_samples']}")
                print(f"Total de treinos realizados: {training_metrics['total_trainings']}")
                
                if training_metrics['avg_training_time'] > 0:
                    print(f"Tempo médio de treino: {training_metrics['avg_training_time']:.2f}s")
                
                if training_metrics['sample_rate'] > 0:
                    print(f"Taxa de coleta: {training_metrics['sample_rate']:.2f} amostras/min")
                
                # Análise de progressão temporal
                if len(training_metrics['samples_timeline']) > 10:
                    timeline = training_metrics['samples_timeline']
                    
                    # Primeiras 10 vs últimas 10
                    first_10 = timeline[:10]
                    last_10 = timeline[-10:]
                    
                    # Calcula taxa de coleta
                    if len(first_10) >= 2:
                        from datetime import datetime
                        t1 = datetime.fromisoformat(first_10[0][0])
                        t2 = datetime.fromisoformat(first_10[-1][0])
                        samples_first = first_10[-1][1] - first_10[0][1]
                        time_first = (t2 - t1).total_seconds() / 60
                        
                        if time_first > 0:
                            rate_first = samples_first / time_first
                            
                            t1 = datetime.fromisoformat(last_10[0][0])
                            t2 = datetime.fromisoformat(last_10[-1][0])
                            samples_last = last_10[-1][1] - last_10[0][1]
                            time_last = (t2 - t1).total_seconds() / 60
                            
                            if time_last > 0:
                                rate_last = samples_last / time_last
                                improvement = ((rate_last - rate_first) / rate_first) * 100
                                
                                print(f"\n📊 Evolução da Taxa de Coleta:")
                                print(f"  Início: {rate_first:.2f} amostras/min")
                                print(f"  Atual: {rate_last:.2f} amostras/min")
                                
                                if improvement > 5:
                                    print(f"  📈 Melhorou: +{improvement:.1f}%")
                                elif improvement < -5:
                                    print(f"  📉 Caiu: {improvement:.1f}%")
                                else:
                                    print(f"  ➡️  Estável: {improvement:+.1f}%")
                
                # Análise de treinos
                if len(training_metrics['training_times']) > 5:
                    times = [t[1] for t in training_metrics['training_times']]
                    first_half = times[:len(times)//2]
                    second_half = times[len(times)//2:]
                    
                    avg_first = statistics.mean(first_half)
                    avg_second = statistics.mean(second_half)
                    
                    print(f"\n⚡ Tempo de Treino:")
                    print(f"  Primeiros treinos: {avg_first:.2f}s")
                    print(f"  Treinos recentes: {avg_second:.2f}s")
                    
                    change = ((avg_second - avg_first) / avg_first) * 100
                    if abs(change) > 5:
                        if change > 0:
                            print(f"  ⚠️  Ficou mais lento: +{change:.1f}%")
                        else:
                            print(f"  ✅ Ficou mais rápido: {change:.1f}%")
                
                if not training_metrics['sessions_data']:
                    print("\n💡 Continue usando o bot para coletar mais dados de progressão")
            else:
                # Código original para analytics sessions
                metrics = relatorio.calculate_learning_metrics(sessions)
                
                print("\n📈 ANÁLISE DE PROGRESSÃO")
                print("-" * 60)
                print(f"Sessões: {metrics.get('total_sessions', 0)}")
                print(f"Tempo total: {str(metrics.get('total_farming_time', '0:00:00')).split('.')[0]}")
                
                if 'xp_trend' in metrics:
                    print(f"\nXP/min: {metrics['xp_trend']}")
                if 'kill_efficiency_trend' in metrics:
                    print(f"Kills/min: {metrics['kill_efficiency_trend']}")
                if 'combat_duration_trend' in metrics:
                    print(f"Duração combate: {metrics['combat_duration_trend']}")
            
            input("\n\nPressione ENTER para continuar...")
        
        elif choice == '6':
            sessions = relatorio.load_analytics_sessions()
            
            # Se não tiver sessões, usa dados de ML
            if not sessions:
                training_metrics = relatorio.load_training_metrics()
                
                print("\n🎯 IMPACTO DO MACHINE LEARNING")
                print("-" * 60)
                print(f"Total de amostras ML: {training_metrics['total_samples']}")
                print(f"Total de treinos: {training_metrics['total_trainings']}")
                
                if training_metrics['total_trainings'] > 0:
                    print(f"\n✅ Sistema ML ativo e treinando")
                    print(f"Taxa de coleta: {training_metrics['sample_rate']:.2f} amostras/min")
                    
                    if training_metrics['total_samples'] >= 100:
                        print(f"\n🎓 Modelos robustos com {training_metrics['total_samples']} amostras")
                        print("   ML está pronto para otimizar movimentos")
                    elif training_metrics['total_samples'] >= 50:
                        print(f"\n⚙️  Modelos intermediários com {training_metrics['total_samples']} amostras")
                        print("   Continue coletando para melhor precisão")
                    else:
                        print(f"\n📊 Modelos iniciais com {training_metrics['total_samples']} amostras")
                        print("   Colete mais dados para ver impacto real")
                    
                    # Estimativa de eficiência
                    if training_metrics['total_samples'] >= 100:
                        efficiency = min(95, 50 + (training_metrics['total_samples'] / 100) * 10)
                        print(f"\n📈 Eficiência estimada do ML: {efficiency:.1f}%")
                else:
                    print("\n⚠️  ML ainda não treinou")
                    print("   Execute o bot para coletar amostras")
                
                print("\n💡 Para análise detalhada de impacto, rode o bot com analytics habilitado")
            else:
                # Código original
                impact = relatorio.calculate_ml_impact(sessions)
                
                print("\n🎯 IMPACTO DO MACHINE LEARNING")
                print("-" * 60)
                print(f"Sessões com ML: {impact['sessions_with_ml']}")
                print(f"Sessões sem ML: {impact['sessions_without_ml']}")
                
                if impact['sessions_with_ml'] > 0 and impact['sessions_without_ml'] > 0:
                    print(f"\nXP/min com ML: {impact['ml_xp_per_min']:.4f}%")
                    print(f"XP/min sem ML: {impact['no_ml_xp_per_min']:.4f}%")
                    
                    if impact['improvement_percentage'] > 0:
                        print(f"\n📈 Melhoria: +{impact['improvement_percentage']:.1f}%")
                    elif impact['improvement_percentage'] < 0:
                        print(f"\n📉 Redução: {impact['improvement_percentage']:.1f}%")
            
            input("\n\nPressione ENTER para continuar...")
        
        else:
            print("\n❌ Opção inválida!")
            input("Pressione ENTER para continuar...")


if __name__ == "__main__":
    main()
