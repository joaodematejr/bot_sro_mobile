#!/usr/bin/env python3
"""
Sistema de A/B Testing para Bot
Testa diferentes configurações e escolhe a melhor automaticamente
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import random

class ABTesting:
    """
    Testa múltiplas variantes de configuração
    e escolhe a que tiver melhor performance
    """
    
    def __init__(self):
        self.ab_file = Path("ml_models/ab_testing.json")
        self.config_file = Path("config_farming_adb.json")
        
        # Variantes para testar
        self.variantes = {
            'A_conservador': {
                'intervalo_target': 3.0,
                'clicks_por_ciclo': 10,
                'threshold_hp_baixo': 50,
                'duracao_skill': 2.0
            },
            'B_agressivo': {
                'intervalo_target': 1.5,
                'clicks_por_ciclo': 20,
                'threshold_hp_baixo': 30,
                'duracao_skill': 1.0
            },
            'C_balanceado': {
                'intervalo_target': 2.0,
                'clicks_por_ciclo': 15,
                'threshold_hp_baixo': 40,
                'duracao_skill': 1.5
            },
            'D_experimental': {
                'intervalo_target': 1.0,
                'clicks_por_ciclo': 25,
                'threshold_hp_baixo': 25,
                'duracao_skill': 0.8
            }
        }
        
        # Resultados de cada variante
        self.resultados = {nome: [] for nome in self.variantes.keys()}
        
        # Variante ativa
        self.variante_ativa = None
        self.tempo_teste_por_variante = 1800  # 30 minutos
        
        self._carregar_resultados()
    
    def _carregar_resultados(self):
        """Carrega resultados anteriores"""
        if self.ab_file.exists():
            try:
                with open(self.ab_file, 'r') as f:
                    data = json.load(f)
                    self.resultados = data.get('resultados', self.resultados)
                    self.variante_ativa = data.get('variante_ativa')
            except Exception as e:
                print(f"⚠️ Erro ao carregar AB testing: {e}")
    
    def _salvar_resultados(self):
        """Salva resultados"""
        try:
            self.ab_file.parent.mkdir(exist_ok=True)
            
            data = {
                'resultados': self.resultados,
                'variante_ativa': self.variante_ativa,
                'melhor_variante': self.obter_melhor_variante(),
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
            with open(self.ab_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar AB testing: {e}")
    
    def selecionar_variante_teste(self) -> str:
        """
        Seleciona próxima variante para testar
        Usa estratégia epsilon-greedy (explora vs explota)
        """
        epsilon = 0.2  # 20% chance de explorar
        
        if random.random() < epsilon:
            # Exploração: testa variante aleatória
            variante = random.choice(list(self.variantes.keys()))
        else:
            # Exploração: usa a melhor
            variante = self.obter_melhor_variante()
        
        self.variante_ativa = variante
        return variante
    
    def aplicar_variante(self, nome_variante: str) -> bool:
        """
        Aplica configuração de uma variante
        
        Args:
            nome_variante: Nome da variante
        
        Returns:
            True se aplicou com sucesso
        """
        if nome_variante not in self.variantes:
            return False
        
        try:
            # Carrega config atual
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Aplica parâmetros da variante
            variante = self.variantes[nome_variante]
            for param, valor in variante.items():
                config[param] = valor
            
            # Salva
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.variante_ativa = nome_variante
            self._salvar_resultados()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao aplicar variante: {e}")
            return False
    
    def registrar_resultado(self, metricas: Dict[str, Any]):
        """
        Registra resultado de teste de variante
        
        Args:
            metricas: Métricas da sessão
        """
        if not self.variante_ativa:
            return
        
        # Calcula score
        duracao_horas = metricas.get('duracao_segundos', 0) / 3600
        
        if duracao_horas < 0.1:
            return
        
        kills_por_hora = metricas.get('kills', 0) / duracao_horas
        xp_por_minuto = metricas.get('xp_ganho', 0) / (duracao_horas * 60)
        mortes_por_hora = metricas.get('mortes', 0) / duracao_horas
        
        # Score composto
        score = (
            kills_por_hora * 0.4 +          # 40% peso
            xp_por_minuto * 50 * 0.3 +      # 30% peso
            max(0, 10 - mortes_por_hora * 10) * 0.3  # 30% peso
        )
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'duracao_horas': duracao_horas,
            'kills_por_hora': kills_por_hora,
            'xp_por_minuto': xp_por_minuto,
            'mortes_por_hora': mortes_por_hora,
            'score': score
        }
        
        self.resultados[self.variante_ativa].append(resultado)
        self._salvar_resultados()
    
    def obter_melhor_variante(self) -> str:
        """
        Retorna nome da variante com melhor performance média
        
        Returns:
            Nome da melhor variante
        """
        scores_medios = {}
        
        for nome, resultados in self.resultados.items():
            if not resultados:
                scores_medios[nome] = 0
            else:
                scores_medios[nome] = np.mean([r['score'] for r in resultados])
        
        if not scores_medios:
            return list(self.variantes.keys())[0]
        
        return max(scores_medios, key=scores_medios.get)
    
    def relatorio_ab_testing(self) -> str:
        """Gera relatório de A/B testing"""
        relatorio = f"""
╔══════════════════════════════════════════════════════════════╗
║           🧪 A/B TESTING - RELATÓRIO DE VARIANTES            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
"""
        
        for nome, resultados in self.resultados.items():
            if not resultados:
                relatorio += f"║  {nome:20s} - SEM DADOS                      ║\n"
                continue
            
            scores = [r['score'] for r in resultados]
            kills = [r['kills_por_hora'] for r in resultados]
            
            score_medio = np.mean(scores)
            kills_medio = np.mean(kills)
            n_testes = len(resultados)
            
            # Marca a melhor
            melhor = " 🏆" if nome == self.obter_melhor_variante() else ""
            
            relatorio += f"║  {nome:20s}{melhor:3s}                              ║\n"
            relatorio += f"║    Score: {score_medio:5.1f}  |  Kills/h: {kills_medio:5.1f}  |  Testes: {n_testes:2d}  ║\n"
        
        relatorio += """║                                                              ║
╠══════════════════════════════════════════════════════════════╣
"""
        
        melhor = self.obter_melhor_variante()
        relatorio += f"║  🥇 MELHOR VARIANTE: {melhor:38s} ║\n"
        relatorio += """║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        return relatorio
    
    def teste_automatico(self, duracao_total_horas: float = 4):
        """
        Executa teste A/B automático
        
        Args:
            duracao_total_horas: Tempo total de teste (horas)
        """
        tempo_por_variante = duracao_total_horas / len(self.variantes)
        
        print(f"🧪 INICIANDO A/B TESTING")
        print(f"   Testando {len(self.variantes)} variantes")
        print(f"   {tempo_por_variante*60:.0f} minutos por variante")
        print(f"   Duração total: {duracao_total_horas} horas")
        print()
        
        for nome in self.variantes.keys():
            print(f"📊 Testando variante: {nome}")
            self.aplicar_variante(nome)
            print(f"   Aguarde {tempo_por_variante*60:.0f} minutos...")
            print(f"   (Execute o bot durante este período)")
            print()


if __name__ == "__main__":
    print("🧪 SISTEMA DE A/B TESTING")
    print("="*70)
    
    ab = ABTesting()
    
    # Mostra relatório
    print(ab.relatorio_ab_testing())
    
    # Sugestão de próximo teste
    proxima = ab.selecionar_variante_teste()
    print(f"\n💡 Próxima variante sugerida: {proxima}")
    print(f"   Execute: python3 ab_testing.py --aplicar {proxima}")
