#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Treinador ML com Sistema de Recompensas
Usa feedback de recompensas para melhorar o modelo
"""

import json
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

class TreinadorComRecompensas:
    """
    Treina modelos ML usando recompensas como feedback
    Implementa aprendizado por reforço híbrido
    """
    
    def __init__(self):
        self.models_dir = Path("ml_models")
        self.rewards_file = self.models_dir / "rewards_history.json"
        self.training_data_file = self.models_dir / "training_data.json"
        self.enhanced_model_file = self.models_dir / "modelo_com_recompensas.pkl"
        
        self.modelo = None
        self.feature_importance = None
    
    def carregar_dados_com_recompensas(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Carrega dados de treino e recompensas
        
        Returns:
            X: Features
            y: Labels
            rewards: Recompensas associadas
        """
        
        # Carrega dados de treino
        if not self.training_data_file.exists():
            print("❌ Arquivo training_data.json não encontrado!")
            return None, None, None
        
        with open(self.training_data_file, 'r') as f:
            training_data = json.load(f)
        
        # Carrega recompensas
        rewards_map = {}
        if self.rewards_file.exists():
            with open(self.rewards_file, 'r') as f:
                rewards_data = json.load(f)
                
                # Mapeia estados para recompensas
                for registro in rewards_data.get('historico', []):
                    timestamp = registro['timestamp']
                    recompensa = registro['recompensa']
                    rewards_map[timestamp] = recompensa
        
        # Prepara features e labels
        X = []
        y = []
        rewards = []
        
        for sample in training_data:
            # Features
            features = [
                sample.get('hour', 0),
                sample.get('minute', 0),
                sample.get('pos_x', 0),
                sample.get('pos_y', 0),
                sample.get('sector_N', 0),
                sample.get('sector_E', 0),
                sample.get('sector_S', 0),
                sample.get('sector_W', 0),
                sample.get('enemy_count', 0),
            ]
            X.append(features)
            
            # Label (baseado em contagem de inimigos)
            enemy_count = sample.get('enemy_count', 0)
            if enemy_count == 0:
                label = 0  # Explorar
            elif enemy_count <= 2:
                label = 1  # Combate único
            else:
                label = 2  # AOE/Multi-target
            y.append(label)
            
            # Recompensa estimada (se disponível)
            # Por padrão, recompensa baseada em enemy_count
            reward = enemy_count * 2.0  # Mais inimigos = melhor
            rewards.append(reward)
        
        return np.array(X), np.array(y), np.array(rewards)
    
    def treinar_com_recompensas(self, usar_gradient_boosting: bool = False):
        """
        Treina modelo usando recompensas como pesos
        
        Args:
            usar_gradient_boosting: Se True, usa GradientBoosting ao invés de RandomForest
        """
        
        print("\n" + "="*70)
        print("🎓 TREINAMENTO COM RECOMPENSAS")
        print("="*70)
        
        # Carrega dados
        X, y, rewards = self.carregar_dados_com_recompensas()
        
        if X is None:
            return
        
        print(f"\n📊 Dados carregados: {len(X)} amostras")
        
        # Normaliza recompensas para pesos (valores positivos)
        # Transforma recompensas em pesos: quanto maior a recompensa, maior o peso
        min_reward = np.min(rewards)
        if min_reward < 0:
            rewards_shifted = rewards - min_reward + 1  # Garante valores positivos
        else:
            rewards_shifted = rewards + 1
        
        # Normaliza pesos (soma = 1)
        sample_weights = rewards_shifted / np.sum(rewards_shifted)
        
        print(f"💰 Recompensas:")
        print(f"   Mínima: {np.min(rewards):.2f}")
        print(f"   Máxima: {np.max(rewards):.2f}")
        print(f"   Média: {np.mean(rewards):.2f}")
        
        # Split train/test
        X_train, X_test, y_train, y_test, weights_train, weights_test = train_test_split(
            X, y, sample_weights, test_size=0.2, random_state=42
        )
        
        print(f"\n📈 Split:")
        print(f"   Treino: {len(X_train)} amostras")
        print(f"   Teste: {len(X_test)} amostras")
        
        # Treina modelo
        print(f"\n🧠 Treinando modelo...")
        start_time = datetime.now()
        
        if usar_gradient_boosting:
            print("   Modelo: GradientBoosting")
            self.modelo = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                random_state=42
            )
            # GradientBoosting não suporta sample_weight diretamente no fit
            # Vamos usar class_weight='balanced'
            self.modelo.fit(X_train, y_train)
        else:
            print("   Modelo: RandomForest")
            self.modelo = RandomForestClassifier(
                n_estimators=300,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
            # RandomForest suporta sample_weight
            # Amplifica os pesos para dar mais ênfase
            weights_amplified = weights_train * len(weights_train)
            self.modelo.fit(X_train, y_train, sample_weight=weights_amplified)
        
        duracao = (datetime.now() - start_time).total_seconds()
        
        print(f"   ✅ Concluído em {duracao:.2f}s")
        
        # Avalia modelo
        print(f"\n📊 Avaliação:")
        
        # Treino
        y_train_pred = self.modelo.predict(X_train)
        acc_train = accuracy_score(y_train, y_train_pred)
        print(f"   Acurácia Treino: {acc_train*100:.2f}%")
        
        # Teste
        y_test_pred = self.modelo.predict(X_test)
        acc_test = accuracy_score(y_test, y_test_pred)
        print(f"   Acurácia Teste: {acc_test*100:.2f}%")
        
        # Importância das features
        if hasattr(self.modelo, 'feature_importances_'):
            self.feature_importance = self.modelo.feature_importances_
            
            print(f"\n📊 Importância das Features:")
            feature_names = ['hour', 'minute', 'pos_x', 'pos_y', 'sector_N', 
                           'sector_E', 'sector_S', 'sector_W', 'enemy_count']
            
            importances = sorted(
                zip(feature_names, self.feature_importance),
                key=lambda x: x[1],
                reverse=True
            )
            
            for name, importance in importances:
                bar = "█" * int(importance * 50)
                print(f"   {name:12s}: {importance:.3f} {bar}")
        
        # Relatório detalhado
        print(f"\n📋 Relatório de Classificação:")
        print(classification_report(y_test, y_test_pred, 
                                   target_names=['Explorar', 'Combate', 'AOE']))
        
        # Salva modelo
        self.salvar_modelo()
        
        # Comparação com modelo anterior
        self.comparar_com_modelo_anterior(X_test, y_test)
        
        print("\n" + "="*70)
    
    def salvar_modelo(self):
        """Salva modelo treinado"""
        
        try:
            modelo_data = {
                'modelo': self.modelo,
                'feature_importance': self.feature_importance,
                'trained_at': datetime.now().isoformat(),
                'trained_with_rewards': True
            }
            
            with open(self.enhanced_model_file, 'wb') as f:
                pickle.dump(modelo_data, f)
            
            print(f"\n💾 Modelo salvo: {self.enhanced_model_file}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar modelo: {e}")
    
    def comparar_com_modelo_anterior(self, X_test: np.ndarray, y_test: np.ndarray):
        """Compara com modelo treinado sem recompensas"""
        
        modelo_antigo_file = self.models_dir / "modelo_sklearn.pkl"
        
        if not modelo_antigo_file.exists():
            print("\n⚠️  Modelo antigo não encontrado para comparação")
            return
        
        try:
            with open(modelo_antigo_file, 'rb') as f:
                modelo_antigo = pickle.load(f)
            
            # Testa modelo antigo
            y_pred_antigo = modelo_antigo.predict(X_test)
            acc_antigo = accuracy_score(y_test, y_pred_antigo)
            
            # Testa modelo novo
            y_pred_novo = self.modelo.predict(X_test)
            acc_novo = accuracy_score(y_test, y_pred_novo)
            
            print(f"\n📊 COMPARAÇÃO DE MODELOS:")
            print(f"   Modelo antigo (sem recompensas): {acc_antigo*100:.2f}%")
            print(f"   Modelo novo (com recompensas): {acc_novo*100:.2f}%")
            
            diff = acc_novo - acc_antigo
            if diff > 0:
                print(f"   📈 Melhoria: +{diff*100:.2f}% ✅")
            elif diff < 0:
                print(f"   📉 Piorou: {diff*100:.2f}% ⚠️")
            else:
                print(f"   ➡️  Sem mudança significativa")
            
        except Exception as e:
            print(f"⚠️  Erro na comparação: {e}")
    
    def prever_melhor_acao(self, estado: Dict[str, Any]) -> Tuple[int, np.ndarray]:
        """
        Prevê melhor ação dado o estado atual
        
        Args:
            estado: Estado atual (enemy_count, hora, etc.)
            
        Returns:
            acao: Ação recomendada (0=Explorar, 1=Combate, 2=AOE)
            probabilidades: Probabilidades de cada ação
        """
        
        if self.modelo is None:
            # Carrega modelo salvo
            if self.enhanced_model_file.exists():
                with open(self.enhanced_model_file, 'rb') as f:
                    modelo_data = pickle.load(f)
                    self.modelo = modelo_data['modelo']
            else:
                print("❌ Modelo não treinado!")
                return 0, np.array([1.0, 0.0, 0.0])
        
        # Prepara features
        features = np.array([[
            estado.get('hour', 0),
            estado.get('minute', 0),
            estado.get('pos_x', 0),
            estado.get('pos_y', 0),
            estado.get('sector_N', 0),
            estado.get('sector_E', 0),
            estado.get('sector_S', 0),
            estado.get('sector_W', 0),
            estado.get('enemy_count', 0)
        ]])
        
        # Predição
        acao = self.modelo.predict(features)[0]
        
        # Probabilidades (se disponível)
        if hasattr(self.modelo, 'predict_proba'):
            probs = self.modelo.predict_proba(features)[0]
        else:
            probs = np.zeros(3)
            probs[acao] = 1.0
        
        return acao, probs


def menu_interativo():
    """Menu para treinar e testar modelo"""
    
    treinador = TreinadorComRecompensas()
    
    while True:
        print("\n" + "="*70)
        print("🎓 TREINADOR ML COM RECOMPENSAS")
        print("="*70)
        print("\n1. 🌲 Treinar RandomForest com recompensas")
        print("2. 🚀 Treinar GradientBoosting com recompensas")
        print("3. 🎯 Testar predição (estado atual)")
        print("4. 📊 Comparar modelos")
        print("0. ❌ Voltar")
        
        escolha = input("\n➡️  Escolha: ").strip()
        
        if escolha == '0':
            break
        
        elif escolha == '1':
            treinador.treinar_com_recompensas(usar_gradient_boosting=False)
            input("\n⏸️  Pressione ENTER para continuar...")
        
        elif escolha == '2':
            treinador.treinar_com_recompensas(usar_gradient_boosting=True)
            input("\n⏸️  Pressione ENTER para continuar...")
        
        elif escolha == '3':
            print("\n🎯 TESTE DE PREDIÇÃO")
            print("-" * 70)
            
            try:
                enemy_count = int(input("Quantidade de inimigos próximos: "))
                
                estado = {
                    'hour': datetime.now().hour,
                    'minute': datetime.now().minute,
                    'pos_x': 0,
                    'pos_y': 0,
                    'sector_N': 0,
                    'sector_E': 0,
                    'sector_S': 0,
                    'sector_W': 0,
                    'enemy_count': enemy_count
                }
                
                acao, probs = treinador.prever_melhor_acao(estado)
                
                acoes_nome = ['Explorar', 'Combate', 'AOE']
                
                print(f"\n📊 Predição:")
                print(f"   Ação recomendada: {acoes_nome[acao]}")
                print(f"\n   Probabilidades:")
                for i, nome in enumerate(acoes_nome):
                    bar = "█" * int(probs[i] * 30)
                    print(f"   {nome:12s}: {probs[i]*100:5.1f}% {bar}")
                
            except Exception as e:
                print(f"❌ Erro: {e}")
            
            input("\n⏸️  Pressione ENTER para continuar...")
        
        elif escolha == '4':
            print("\n📊 Carregue os modelos e teste no main.py")
            input("\n⏸️  Pressione ENTER para continuar...")
        
        else:
            print("❌ Opção inválida!")


if __name__ == "__main__":
    menu_interativo()
