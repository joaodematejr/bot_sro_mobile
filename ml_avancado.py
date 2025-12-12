#!/usr/bin/env python3
"""
Sistema de ML Avançado para Otimização de Farming
- Aprende melhores rotas baseado em EXP/hora
- Otimiza rotação de skills
- Mapeia densidade de mobs
- Adapta estratégia por horário
"""

import numpy as np
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os

class MLAvancado:
    def __init__(self, arquivo_dados='ml_avancado_dados.json', arquivo_modelo='ml_avancado_modelo.pkl'):
        self.arquivo_dados = arquivo_dados
        self.arquivo_modelo = arquivo_modelo
        
        # Dados de rotas
        self.historico_rotas = []  # [(coordenadas, exp_ganho, tempo, horario, area)]
        self.densidade_mobs = {}  # {(x, y): {'combates': N, 'exp_total': X, 'tempo_total': T}}
        
        # Dados de skills
        self.historico_skills = defaultdict(list)  # {skill_id: [(damage_estimado, cooldown, sucesso)]}
        self.combos_eficientes = []  # [(combo, eficiencia)]
        
        # Dados temporais
        self.performance_por_hora = defaultdict(list)  # {hora: [exp_por_minuto]}
        self.areas_por_horario = defaultdict(lambda: defaultdict(float))  # {hora: {area: eficiencia}}
        
        # Modelos ML
        self.modelo_rota = GradientBoostingRegressor(n_estimators=100, max_depth=5)
        self.modelo_skill = RandomForestRegressor(n_estimators=50, max_depth=4)
        self.scaler_rota = StandardScaler()
        self.scaler_skill = StandardScaler()
        
        # Estado
        self.modelos_treinados = False
        self.ultima_atualizacao = time.time()
        self.min_dados_treino = 20
        
        # Otimização de Parâmetros
        self.historico_parametros = []  # [(timestamp, params, exp_hora, mortes)]
        self.melhores_parametros = {}  # Parâmetros ótimos descobertos
        self.parametros_testados = set()  # Para evitar testes duplicados
        
        # Carregar dados existentes
        self.carregar_dados()
    
    def registrar_rota(self, x, y, exp_ganho, tempo_gasto, area_id=0):
        """
        Registra dados de uma rota/posição
        
        Args:
            x, y: Coordenadas
            exp_ganho: EXP total ganho na posição
            tempo_gasto: Tempo em segundos
            area_id: ID da área (para multi-área)
        """
        hora = datetime.now().hour
        
        # Adiciona ao histórico
        self.historico_rotas.append({
            'x': x,
            'y': y,
            'exp': exp_ganho,
            'tempo': tempo_gasto,
            'hora': hora,
            'area': area_id,
            'timestamp': time.time(),
            'exp_por_minuto': (exp_ganho / tempo_gasto * 60) if tempo_gasto > 0 else 0
        })
        
        # Atualiza densidade de mobs
        chave = self._normalizar_coordenada(x, y)
        if chave not in self.densidade_mobs:
            self.densidade_mobs[chave] = {
                'combates': 0,
                'exp_total': 0,
                'tempo_total': 0,
                'ultima_visita': time.time()
            }
        
        self.densidade_mobs[chave]['combates'] += 1
        self.densidade_mobs[chave]['exp_total'] += exp_ganho
        self.densidade_mobs[chave]['tempo_total'] += tempo_gasto
        self.densidade_mobs[chave]['ultima_visita'] = time.time()
        
        # Atualiza performance por horário
        exp_min = (exp_ganho / tempo_gasto * 60) if tempo_gasto > 0 else 0
        self.performance_por_hora[hora].append(exp_min)
        self.areas_por_horario[hora][area_id] += exp_min
        
        # Salva periodicamente
        if time.time() - self.ultima_atualizacao > 300:  # A cada 5 min
            self.salvar_dados()
            self.ultima_atualizacao = time.time()
    
    def registrar_skill(self, skill_id, damage_estimado, cooldown, sucesso=True):
        """
        Registra uso de skill e sua eficiência
        
        Args:
            skill_id: ID ou nome da skill
            damage_estimado: Dano estimado ou impacto
            cooldown: Tempo de recarga em segundos
            sucesso: Se o uso foi bem-sucedido
        """
        self.historico_skills[skill_id].append({
            'damage': damage_estimado,
            'cooldown': cooldown,
            'sucesso': 1 if sucesso else 0,
            'timestamp': time.time(),
            'eficiencia': damage_estimado / cooldown if cooldown > 0 else 0
        })
        
        # Mantém apenas últimos 100 registros por skill
        if len(self.historico_skills[skill_id]) > 100:
            self.historico_skills[skill_id] = self.historico_skills[skill_id][-100:]
    
    def registrar_combo(self, skills_usadas, tempo_combate, exp_ganho):
        """
        Registra um combo de skills e sua eficiência
        
        Args:
            skills_usadas: Lista de IDs das skills na ordem
            tempo_combate: Tempo total do combate
            exp_ganho: EXP ganho
        """
        combo_str = '_'.join(map(str, skills_usadas))
        eficiencia = exp_ganho / tempo_combate if tempo_combate > 0 else 0
        
        self.combos_eficientes.append({
            'combo': combo_str,
            'skills': skills_usadas,
            'eficiencia': eficiencia,
            'tempo': tempo_combate,
            'exp': exp_ganho,
            'timestamp': time.time()
        })
        
        # Mantém últimos 200 combos
        if len(self.combos_eficientes) > 200:
            self.combos_eficientes = self.combos_eficientes[-200:]
    
    def _normalizar_coordenada(self, x, y, grid_size=50):
        """Normaliza coordenadas para grid (reduz granularidade)"""
        return (int(x // grid_size) * grid_size, int(y // grid_size) * grid_size)
    
    def obter_densidade_area(self, x, y):
        """Retorna densidade de mobs em uma área"""
        chave = self._normalizar_coordenada(x, y)
        
        if chave not in self.densidade_mobs:
            return 0.0
        
        dados = self.densidade_mobs[chave]
        if dados['tempo_total'] == 0:
            return 0.0
        
        # Densidade = EXP por minuto na área
        densidade = (dados['exp_total'] / dados['tempo_total']) * 60
        
        # Penaliza áreas visitadas recentemente (para espalhar farming)
        tempo_desde_visita = time.time() - dados['ultima_visita']
        fator_tempo = min(1.0, tempo_desde_visita / 300)  # Recupera em 5 min
        
        return densidade * fator_tempo
    
    def obter_areas_rankadas(self, top_n=5):
        """Retorna as N melhores áreas para farmar"""
        areas_rankeadas = []
        
        for coords, dados in self.densidade_mobs.items():
            if dados['combates'] >= 3:  # Mínimo de dados
                densidade = self.obter_densidade_area(coords[0], coords[1])
                areas_rankeadas.append({
                    'x': coords[0],
                    'y': coords[1],
                    'densidade': densidade,
                    'combates': dados['combates'],
                    'exp_total': dados['exp_total']
                })
        
        # Ordena por densidade
        areas_rankeadas.sort(key=lambda x: x['densidade'], reverse=True)
        return areas_rankeadas[:top_n]
    
    def recomendar_proxima_posicao(self, x_atual, y_atual, raio_max=200):
        """
        Recomenda próxima melhor posição para ir
        
        Returns:
            (x, y, densidade_esperada) ou None
        """
        if len(self.densidade_mobs) < 5:
            return None
        
        melhores = []
        
        for coords, dados in self.densidade_mobs.items():
            # Calcula distância
            dist = np.sqrt((coords[0] - x_atual)**2 + (coords[1] - y_atual)**2)
            
            if dist > raio_max or dist < 10:  # Muito longe ou muito perto
                continue
            
            densidade = self.obter_densidade_area(coords[0], coords[1])
            
            # Score = densidade / (distância + 1) - favorece áreas boas e próximas
            score = densidade / (dist + 1)
            
            melhores.append({
                'x': coords[0],
                'y': coords[1],
                'densidade': densidade,
                'distancia': dist,
                'score': score
            })
        
        if not melhores:
            return None
        
        # Retorna melhor score
        melhores.sort(key=lambda x: x['score'], reverse=True)
        melhor = melhores[0]
        return (melhor['x'], melhor['y'], melhor['densidade'])
    
    def obter_melhor_horario(self):
        """Retorna horário com melhor performance média"""
        if not self.performance_por_hora:
            return None
        
        medias = {}
        for hora, valores in self.performance_por_hora.items():
            if len(valores) >= 3:
                medias[hora] = np.mean(valores)
        
        if not medias:
            return None
        
        return max(medias.items(), key=lambda x: x[1])
    
    def obter_skills_rankadas(self):
        """Retorna skills ordenadas por eficiência"""
        skills_eficiencia = []
        
        for skill_id, registros in self.historico_skills.items():
            if len(registros) >= 3:
                eficiencias = [r['eficiencia'] for r in registros]
                taxa_sucesso = np.mean([r['sucesso'] for r in registros])
                
                skills_eficiencia.append({
                    'skill_id': skill_id,
                    'eficiencia_media': np.mean(eficiencias),
                    'taxa_sucesso': taxa_sucesso,
                    'usos': len(registros),
                    'score': np.mean(eficiencias) * taxa_sucesso
                })
        
        skills_eficiencia.sort(key=lambda x: x['score'], reverse=True)
        return skills_eficiencia
    
    def recomendar_rotacao_skills(self, max_skills=4):
        """
        Recomenda melhor rotação de skills baseado em ML
        
        Returns:
            Lista de skill_ids na ordem recomendada
        """
        # Se temos combos eficientes registrados, usa eles
        if self.combos_eficientes:
            # Pega top 10 combos mais eficientes
            top_combos = sorted(self.combos_eficientes, 
                              key=lambda x: x['eficiencia'], 
                              reverse=True)[:10]
            
            if top_combos:
                return top_combos[0]['skills']
        
        # Senão, usa skills individuais mais eficientes
        skills_rankeadas = self.obter_skills_rankadas()
        if skills_rankeadas:
            return [s['skill_id'] for s in skills_rankeadas[:max_skills]]
        
        return []
    
    def treinar_modelos(self):
        """Treina modelos ML com dados coletados"""
        # Treina modelo de rotas
        if len(self.historico_rotas) >= self.min_dados_treino:
            try:
                # Prepara dados de rotas
                X_rotas = []
                y_rotas = []
                
                for rota in self.historico_rotas:
                    features = [
                        rota['x'],
                        rota['y'],
                        rota['hora'],
                        rota['area']
                    ]
                    X_rotas.append(features)
                    y_rotas.append(rota['exp_por_minuto'])
                
                X_rotas = np.array(X_rotas)
                y_rotas = np.array(y_rotas)
                
                # Treina
                X_scaled = self.scaler_rota.fit_transform(X_rotas)
                self.modelo_rota.fit(X_scaled, y_rotas)
                
                print(f"  ✓ Modelo de rotas treinado ({len(X_rotas)} amostras)")
                self.modelos_treinados = True
                
            except Exception as e:
                print(f"  ⚠️ Erro ao treinar modelo de rotas: {e}")
        
        # Treina modelo de skills
        skill_data = []
        for skill_id, registros in self.historico_skills.items():
            for r in registros:
                skill_data.append({
                    'skill_id': skill_id,
                    'damage': r['damage'],
                    'cooldown': r['cooldown'],
                    'sucesso': r['sucesso'],
                    'eficiencia': r['eficiencia']
                })
        
        if len(skill_data) >= self.min_dados_treino:
            try:
                # Prepara dados de skills
                # Converte skill_id para numérico
                skill_ids_unicos = list(set(d['skill_id'] for d in skill_data))
                skill_id_map = {sid: i for i, sid in enumerate(skill_ids_unicos)}
                
                X_skills = []
                y_skills = []
                
                for d in skill_data:
                    features = [
                        skill_id_map[d['skill_id']],
                        d['damage'],
                        d['cooldown']
                    ]
                    X_skills.append(features)
                    y_skills.append(d['eficiencia'])
                
                X_skills = np.array(X_skills)
                y_skills = np.array(y_skills)
                
                # Treina
                X_scaled = self.scaler_skill.fit_transform(X_skills)
                self.modelo_skill.fit(X_scaled, y_skills)
                
                print(f"  ✓ Modelo de skills treinado ({len(X_skills)} amostras)")
                
            except Exception as e:
                print(f"  ⚠️ Erro ao treinar modelo de skills: {e}")
    
    def prever_exp_posicao(self, x, y, hora=None, area_id=0):
        """Prevê EXP/min em uma posição usando ML"""
        if not self.modelos_treinados:
            # Fallback: usa densidade direta
            return self.obter_densidade_area(x, y)
        
        if hora is None:
            hora = datetime.now().hour
        
        try:
            features = np.array([[x, y, hora, area_id]])
            features_scaled = self.scaler_rota.transform(features)
            previsao = self.modelo_rota.predict(features_scaled)[0]
            return max(0, previsao)
        except:
            return self.obter_densidade_area(x, y)
    
    def gerar_mapa_calor_3d(self, grid_size=50, max_x=1000, max_y=1000):
        """
        Gera dados para mapa de calor 3D
        
        Returns:
            dict com 'x', 'y', 'densidade' para plotagem
        """
        pontos_x = []
        pontos_y = []
        densidades = []
        
        for x in range(0, max_x, grid_size):
            for y in range(0, max_y, grid_size):
                densidade = self.obter_densidade_area(x, y)
                if densidade > 0:
                    pontos_x.append(x)
                    pontos_y.append(y)
                    densidades.append(densidade)
        
        return {
            'x': pontos_x,
            'y': pontos_y,
            'densidade': densidades,
            'grid_size': grid_size
        }
    
    def salvar_dados(self):
        """Salva dados históricos"""
        try:
            dados = {
                'historico_rotas': self.historico_rotas[-1000:],  # Últimas 1000
                'densidade_mobs': dict(self.densidade_mobs),
                'historico_skills': {k: v for k, v in self.historico_skills.items()},
                'combos_eficientes': self.combos_eficientes[-200:],
                'performance_por_hora': dict(self.performance_por_hora),
                'areas_por_horario': {k: dict(v) for k, v in self.areas_por_horario.items()},
                'historico_parametros': self.historico_parametros[-100:],
                'melhores_parametros': self.melhores_parametros
            }
            
            # Converte tuplas para strings no densidade_mobs
            dados['densidade_mobs'] = {
                f"{k[0]},{k[1]}": v for k, v in dados['densidade_mobs'].items()
            }
            
            with open(self.arquivo_dados, 'w') as f:
                json.dump(dados, f, indent=2)
            
            # Salva modelos
            if self.modelos_treinados:
                with open(self.arquivo_modelo, 'wb') as f:
                    pickle.dump({
                        'modelo_rota': self.modelo_rota,
                        'modelo_skill': self.modelo_skill,
                        'scaler_rota': self.scaler_rota,
                        'scaler_skill': self.scaler_skill
                    }, f)
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar dados ML: {e}")
    
    def carregar_dados(self):
        """Carrega dados históricos"""
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, 'r') as f:
                    dados = json.load(f)
                
                self.historico_rotas = dados.get('historico_rotas', [])
                
                # Reconverte strings para tuplas no densidade_mobs
                densidade_str = dados.get('densidade_mobs', {})
                self.densidade_mobs = {
                    tuple(map(int, k.split(','))): v 
                    for k, v in densidade_str.items()
                }
                
                self.historico_skills = defaultdict(list, dados.get('historico_skills', {}))
                self.combos_eficientes = dados.get('combos_eficientes', [])
                
                perf_hora = dados.get('performance_por_hora', {})
                self.performance_por_hora = defaultdict(list, {
                    int(k): v for k, v in perf_hora.items()
                })
                
                areas_hora = dados.get('areas_por_horario', {})
                self.areas_por_horario = defaultdict(lambda: defaultdict(float), {
                    int(k): defaultdict(float, v) for k, v in areas_hora.items()
                })
                
                self.historico_parametros = dados.get('historico_parametros', [])
                self.melhores_parametros = dados.get('melhores_parametros', {})
                
                print(f"  ✓ Dados ML carregados: {len(self.historico_rotas)} rotas, {len(self.densidade_mobs)} áreas")
                
            except Exception as e:
                print(f"  ⚠️ Erro ao carregar dados ML: {e}")
        
        # Carrega modelos
        if os.path.exists(self.arquivo_modelo):
            try:
                with open(self.arquivo_modelo, 'rb') as f:
                    modelos = pickle.load(f)
                
                self.modelo_rota = modelos['modelo_rota']
                self.modelo_skill = modelos['modelo_skill']
                self.scaler_rota = modelos['scaler_rota']
                self.scaler_skill = modelos['scaler_skill']
                self.modelos_treinados = True
                
                print(f"  ✓ Modelos ML carregados")
                
            except Exception as e:
                print(f"  ⚠️ Erro ao carregar modelos ML: {e}")
    
    def obter_estatisticas(self):
        """Retorna estatísticas completas do sistema ML"""
        stats = {
            'total_rotas': len(self.historico_rotas),
            'total_areas': len(self.densidade_mobs),
            'total_skills_treinadas': len(self.historico_skills),
            'total_combos': len(self.combos_eficientes),
            'modelos_treinados': self.modelos_treinados
        }
        
        # Melhores áreas
        top_areas = self.obter_areas_rankadas(3)
        stats['top_3_areas'] = top_areas
        
        # Melhor horário
        melhor_horario = self.obter_melhor_horario()
        if melhor_horario:
            stats['melhor_horario'] = {
                'hora': melhor_horario[0],
                'exp_min': melhor_horario[1]
            }
        
        # Melhores skills
        top_skills = self.obter_skills_rankadas()[:3]
        stats['top_3_skills'] = top_skills
        
        return stats
    
    def otimizar_parametros(self, stats_atuais):
        """Otimiza parâmetros do bot baseado em aprendizado
        
        Args:
            stats_atuais (dict): Estatísticas atuais do bot
            
        Returns:
            dict: Parâmetros otimizados para melhor performance
        """
        if len(self.historico_parametros) < 5:
            return {}  # Precisa de mais dados
        
        # Analisa últimas 20 sessões
        recentes = self.historico_parametros[-20:]
        
        # Calcula eficiência (exp/hora dividido por mortes+1)
        eficiencias = []
        for timestamp, params, exp_hora, mortes in recentes:
            eficiencia = exp_hora / (mortes + 1)
            eficiencias.append((eficiencia, params))
        
        # Ordena por eficiência
        eficiencias.sort(reverse=True, key=lambda x: x[0])
        
        # Pega top 5 melhores configurações
        top_configs = eficiencias[:5]
        
        # Calcula média dos melhores parâmetros
        params_otimizados = {}
        
        for key in ['threshold_hp', 'threshold_hp_teleporte', 'intervalo_skills', 
                    'threshold_poucos_inimigos', 'raio_movimento_circular']:
            valores = []
            for _, params in top_configs:
                if key in params:
                    valores.append(params[key])
            
            if valores:
                # Média ponderada (favorece melhores configurações)
                params_otimizados[key] = int(np.mean(valores))
        
        # Parâmetros booleanos - usa moda (mais comum nos top 5)
        for key in ['usar_movimento_circular', 'auto_buff', 'usar_teleporte_emergencia']:
            valores = []
            for _, params in top_configs:
                if key in params:
                    valores.append(params[key])
            
            if valores:
                # Usa o valor mais comum
                params_otimizados[key] = max(set(valores), key=valores.count)
        
        self.melhores_parametros = params_otimizados
        return params_otimizados
    
    def registrar_sessao_parametros(self, parametros_config, exp_ganho, tempo_decorrido, mortes):
        """Registra uma sessão com seus parâmetros e resultados
        
        Args:
            parametros_config (dict): Parâmetros usados na sessão
            exp_ganho (int): EXP total ganho
            tempo_decorrido (float): Tempo em segundos
            mortes (int): Número de mortes
        """
        # Calcula EXP/hora
        if tempo_decorrido > 0:
            exp_hora = (exp_ganho / tempo_decorrido) * 3600
        else:
            exp_hora = 0
        
        # Extrai parâmetros relevantes
        params_relevantes = {
            'threshold_hp': parametros_config.get('threshold_hp', 40),
            'threshold_hp_teleporte': parametros_config.get('threshold_hp_teleporte', 15),
            'intervalo_skills': parametros_config.get('intervalo_skills', 3000),
            'threshold_poucos_inimigos': parametros_config.get('threshold_poucos_inimigos', 5),
            'raio_movimento_circular': parametros_config.get('raio_movimento_circular', 0.8),
            'usar_movimento_circular': parametros_config.get('usar_movimento_circular', True),
            'auto_buff': parametros_config.get('auto_buff', True),
            'usar_teleporte_emergencia': parametros_config.get('usar_teleporte_emergencia', True),
        }
        
        # Registra
        self.historico_parametros.append((
            time.time(),
            params_relevantes,
            exp_hora,
            mortes
        ))
        
        # Limita histórico a últimas 100 sessões
        if len(self.historico_parametros) > 100:
            self.historico_parametros = self.historico_parametros[-100:]
    
    def obter_relatorio_parametros(self):
        """Gera relatório de otimização de parâmetros
        
        Returns:
            dict: Relatório com histórico e melhores parâmetros
        """
        if not self.historico_parametros:
            return {
                'sessoes_registradas': 0,
                'mensagem': 'Nenhuma sessão registrada ainda'
            }
        
        # Calcula eficiências
        eficiencias = []
        for timestamp, params, exp_hora, mortes in self.historico_parametros:
            eficiencia = exp_hora / (mortes + 1)
            eficiencias.append({
                'timestamp': timestamp,
                'exp_hora': exp_hora,
                'mortes': mortes,
                'eficiencia': eficiencia,
                'params': params
            })
        
        # Ordena por eficiência
        eficiencias.sort(reverse=True, key=lambda x: x['eficiencia'])
        
        # Top 5 melhores sessões
        top_5 = eficiencias[:5]
        
        # Média geral
        media_exp_hora = np.mean([e['exp_hora'] for e in eficiencias])
        media_mortes = np.mean([e['mortes'] for e in eficiencias])
        
        return {
            'sessoes_registradas': len(self.historico_parametros),
            'media_exp_hora': media_exp_hora,
            'media_mortes': media_mortes,
            'top_5_sessoes': top_5,
            'melhores_parametros': self.melhores_parametros,
            'ultima_atualizacao': time.time()
        }
