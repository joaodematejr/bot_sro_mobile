#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Mapeamento de Hotspots
Identifica e ranqueia melhores áreas de farming
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

class MapeadorHotspots:
    """
    Mapeia áreas de farming e identifica hotspots
    Registra XP/hora, kills/min, mortes por região
    """
    
    def __init__(self):
        self.hotspots_file = Path("ml_models/hotspots_map.json")
        self.heatmap_dir = Path("analytics_data/heatmaps")
        self.heatmap_dir.mkdir(parents=True, exist_ok=True)
        
        # Estrutura: {region_id: {stats}}
        self.regioes = {}
        
        # Sessão atual
        self.sessao_atual = {
            'regiao_id': None,
            'inicio': None,
            'xp_inicial': 0,
            'kills': 0,
            'mortes': 0,
            'mobs_detectados': []
        }
        
        # Grid de mapeamento (10x10 células)
        self.grid_size = 10
        self.grid_data = defaultdict(lambda: {
            'visits': 0,
            'xp_gained': 0,
            'kills': 0,
            'deaths': 0,
            'avg_mobs': 0,
            'total_time': 0
        })
        
        self._carregar_mapa()
    
    def _carregar_mapa(self):
        """Carrega mapa de hotspots salvo"""
        if self.hotspots_file.exists():
            try:
                with open(self.hotspots_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.regioes = data.get('regioes', {})
                    
                    # Carrega grid se existir
                    grid_raw = data.get('grid', {})
                    for key, value in grid_raw.items():
                        self.grid_data[key] = value
                    
                    print(f"🗺️  Mapa carregado: {len(self.regioes)} regiões mapeadas")
            except Exception as e:
                print(f"⚠️ Erro ao carregar mapa: {e}")
    
    def _salvar_mapa(self):
        """Salva mapa de hotspots"""
        try:
            data = {
                'regioes': self.regioes,
                'grid': dict(self.grid_data),
                'ultima_atualizacao': datetime.now().isoformat(),
                'total_regioes': len(self.regioes),
                'total_celulas': len(self.grid_data)
            }
            
            with open(self.hotspots_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar mapa: {e}")
    
    def _posicao_para_grid(self, pos_x: int, pos_y: int) -> str:
        """Converte posição real para célula do grid"""
        # Normaliza posição para grid 10x10
        # Assume coordenadas entre 0-1000
        grid_x = min(int(pos_x / 100), self.grid_size - 1)
        grid_y = min(int(pos_y / 100), self.grid_size - 1)
        
        return f"{grid_x},{grid_y}"
    
    def _grid_para_posicao(self, grid_id: str) -> Tuple[int, int]:
        """Converte célula do grid para posição central"""
        x, y = map(int, grid_id.split(','))
        
        # Retorna centro da célula
        pos_x = (x * 100) + 50
        pos_y = (y * 100) + 50
        
        return pos_x, pos_y
    
    def iniciar_sessao_regiao(self, regiao_id: str, xp_inicial: float, 
                              pos_x: int = 0, pos_y: int = 0):
        """
        Inicia rastreamento de uma região
        
        Args:
            regiao_id: ID único da região (ex: "area_central", "dungeon_1")
            xp_inicial: XP % no início
            pos_x, pos_y: Coordenadas da região
        """
        
        self.sessao_atual = {
            'regiao_id': regiao_id,
            'inicio': datetime.now(),
            'xp_inicial': xp_inicial,
            'kills': 0,
            'mortes': 0,
            'mobs_detectados': [],
            'pos_x': pos_x,
            'pos_y': pos_y
        }
        
        print(f"📍 Sessão iniciada: {regiao_id}")
    
    def atualizar_estado(self, xp_atual: float, kills: int, mortes: int, 
                        mobs_nearby: int, pos_x: int = 0, pos_y: int = 0):
        """
        Atualiza estado da sessão atual
        
        Args:
            xp_atual: XP % atual
            kills: Total de kills até agora
            mortes: Total de mortes até agora
            mobs_nearby: Mobs detectados no momento
            pos_x, pos_y: Posição atual
        """
        
        if self.sessao_atual['regiao_id'] is None:
            # Cria região automaticamente baseada em posição
            grid_id = self._posicao_para_grid(pos_x, pos_y)
            self.iniciar_sessao_regiao(f"auto_{grid_id}", xp_atual, pos_x, pos_y)
        
        self.sessao_atual['kills'] = kills
        self.sessao_atual['mortes'] = mortes
        self.sessao_atual['mobs_detectados'].append(mobs_nearby)
        self.sessao_atual['pos_x'] = pos_x
        self.sessao_atual['pos_y'] = pos_y
        
        # Atualiza grid
        grid_id = self._posicao_para_grid(pos_x, pos_y)
        self.grid_data[grid_id]['visits'] += 1
        self.grid_data[grid_id]['avg_mobs'] = np.mean(
            [self.grid_data[grid_id]['avg_mobs'], mobs_nearby]
        )
    
    def finalizar_sessao_regiao(self, xp_final: float) -> Dict[str, Any]:
        """
        Finaliza sessão e calcula métricas da região
        
        Args:
            xp_final: XP % no final
            
        Returns:
            Estatísticas da sessão
        """
        
        if self.sessao_atual['regiao_id'] is None:
            print("⚠️ Nenhuma sessão ativa")
            return {}
        
        # Calcula duração
        duracao = datetime.now() - self.sessao_atual['inicio']
        duracao_min = duracao.total_seconds() / 60
        
        # Calcula métricas
        xp_ganho = xp_final - self.sessao_atual['xp_inicial']
        xp_por_hora = (xp_ganho / duracao_min) * 60 if duracao_min > 0 else 0
        kills_por_min = self.sessao_atual['kills'] / duracao_min if duracao_min > 0 else 0
        mortes_por_hora = (self.sessao_atual['mortes'] / duracao_min) * 60 if duracao_min > 0 else 0
        media_mobs = np.mean(self.sessao_atual['mobs_detectados']) if self.sessao_atual['mobs_detectados'] else 0
        
        # Calcula score da região
        score = self._calcular_score_regiao(
            xp_por_hora, kills_por_min, mortes_por_hora, media_mobs
        )
        
        # Atualiza/cria região
        regiao_id = self.sessao_atual['regiao_id']
        
        if regiao_id not in self.regioes:
            self.regioes[regiao_id] = {
                'pos_x': self.sessao_atual['pos_x'],
                'pos_y': self.sessao_atual['pos_y'],
                'sessoes': [],
                'xp_por_hora_medio': 0,
                'kills_por_min_medio': 0,
                'mortes_por_hora_medio': 0,
                'media_mobs': 0,
                'score': 0,
                'rank': 0
            }
        
        # Adiciona sessão ao histórico
        sessao_dados = {
            'timestamp': datetime.now().isoformat(),
            'duracao_min': duracao_min,
            'xp_ganho': xp_ganho,
            'xp_por_hora': xp_por_hora,
            'kills': self.sessao_atual['kills'],
            'kills_por_min': kills_por_min,
            'mortes': self.sessao_atual['mortes'],
            'mortes_por_hora': mortes_por_hora,
            'media_mobs': media_mobs,
            'score': score
        }
        
        self.regioes[regiao_id]['sessoes'].append(sessao_dados)
        
        # Atualiza médias
        self._atualizar_medias_regiao(regiao_id)
        
        # Atualiza grid
        grid_id = self._posicao_para_grid(
            self.sessao_atual['pos_x'], 
            self.sessao_atual['pos_y']
        )
        self.grid_data[grid_id]['xp_gained'] += xp_ganho
        self.grid_data[grid_id]['kills'] += self.sessao_atual['kills']
        self.grid_data[grid_id]['deaths'] += self.sessao_atual['mortes']
        self.grid_data[grid_id]['total_time'] += duracao_min
        
        # Salva mapa
        self._salvar_mapa()
        
        # Rankeia regiões
        self._rankear_regioes()
        
        print(f"\n✅ Sessão finalizada: {regiao_id}")
        print(f"   XP/hora: {xp_por_hora:.4f}%")
        print(f"   Kills/min: {kills_por_min:.2f}")
        print(f"   Score: {score:.2f}")
        print(f"   Rank: #{self.regioes[regiao_id]['rank']}")
        
        # Reset sessão
        self.sessao_atual = {
            'regiao_id': None,
            'inicio': None,
            'xp_inicial': 0,
            'kills': 0,
            'mortes': 0,
            'mobs_detectados': []
        }
        
        return sessao_dados
    
    def _calcular_score_regiao(self, xp_por_hora: float, kills_por_min: float,
                               mortes_por_hora: float, media_mobs: float) -> float:
        """
        Calcula score de qualidade da região
        
        Score = XP/hora * 0.5 + Kills/min * 20 * 0.3 + Mobs * 5 * 0.1 - Mortes * 10 * 0.1
        """
        
        score = (
            xp_por_hora * 1000 * 0.5 +      # XP é o mais importante
            kills_por_min * 20 * 0.3 +       # Kills também importam
            media_mobs * 5 * 0.1 -           # Densidade de mobs é boa
            mortes_por_hora * 10 * 0.1       # Mortes penalizam
        )
        
        return max(0, score)  # Não permite scores negativos
    
    def _atualizar_medias_regiao(self, regiao_id: str):
        """Atualiza médias de todas as métricas da região"""
        
        sessoes = self.regioes[regiao_id]['sessoes']
        
        if not sessoes:
            return
        
        self.regioes[regiao_id]['xp_por_hora_medio'] = np.mean([s['xp_por_hora'] for s in sessoes])
        self.regioes[regiao_id]['kills_por_min_medio'] = np.mean([s['kills_por_min'] for s in sessoes])
        self.regioes[regiao_id]['mortes_por_hora_medio'] = np.mean([s['mortes_por_hora'] for s in sessoes])
        self.regioes[regiao_id]['media_mobs'] = np.mean([s['media_mobs'] for s in sessoes])
        self.regioes[regiao_id]['score'] = np.mean([s['score'] for s in sessoes])
    
    def _rankear_regioes(self):
        """Rankeia regiões por score"""
        
        # Ordena por score
        regioes_sorted = sorted(
            self.regioes.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Atribui ranks
        for rank, (regiao_id, _) in enumerate(regioes_sorted, 1):
            self.regioes[regiao_id]['rank'] = rank
    
    def get_top_hotspots(self, n: int = 5) -> List[Tuple[str, Dict]]:
        """
        Retorna top N hotspots
        
        Args:
            n: Quantidade de hotspots a retornar
            
        Returns:
            Lista de (regiao_id, dados)
        """
        
        regioes_sorted = sorted(
            self.regioes.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        return regioes_sorted[:n]
    
    def get_melhor_hotspot(self) -> Optional[Tuple[str, Dict]]:
        """Retorna o melhor hotspot mapeado"""
        
        top = self.get_top_hotspots(n=1)
        return top[0] if top else None
    
    def exibir_relatorio(self):
        """Exibe relatório completo de hotspots"""
        
        print("\n" + "="*70)
        print("🗺️  MAPA DE HOTSPOTS")
        print("="*70)
        
        if not self.regioes:
            print("\n⚠️  Nenhuma região mapeada ainda!")
            print("   Execute o bot para começar a mapear áreas")
            return
        
        top_hotspots = self.get_top_hotspots(n=10)
        
        print(f"\n🏆 TOP {len(top_hotspots)} HOTSPOTS:")
        print("-" * 70)
        
        for regiao_id, dados in top_hotspots:
            rank = dados['rank']
            score = dados['score']
            xp_hora = dados['xp_por_hora_medio']
            kills_min = dados['kills_por_min_medio']
            mortes_hora = dados['mortes_por_hora_medio']
            mobs = dados['media_mobs']
            sessoes = len(dados['sessoes'])
            
            print(f"\n#{rank}. {regiao_id}")
            print(f"   Score: {score:.2f}")
            print(f"   XP/hora: {xp_hora:.4f}%")
            print(f"   Kills/min: {kills_min:.2f}")
            print(f"   Mortes/hora: {mortes_hora:.2f}")
            print(f"   Mobs médios: {mobs:.1f}")
            print(f"   Sessões: {sessoes}")
            
            # Indicador visual
            if rank == 1:
                print(f"   🌟🌟🌟 MELHOR HOTSPOT!")
            elif rank <= 3:
                print(f"   🌟🌟 Excelente!")
            elif rank <= 5:
                print(f"   🌟 Muito bom!")
        
        print("\n" + "="*70)
    
    def gerar_heatmap(self, metrica: str = 'score'):
        """
        Gera mapa de calor visual
        
        Args:
            metrica: 'score', 'xp', 'kills', 'deaths'
        """
        
        if not self.grid_data:
            print("⚠️ Dados insuficientes para heatmap")
            return
        
        # Prepara matriz
        grid_matrix = np.zeros((self.grid_size, self.grid_size))
        
        for grid_id, dados in self.grid_data.items():
            x, y = map(int, grid_id.split(','))
            
            if metrica == 'score':
                # Calcula score da célula
                if dados['total_time'] > 0:
                    xp_hora = (dados['xp_gained'] / dados['total_time']) * 60
                    kills_min = dados['kills'] / dados['total_time']
                    mortes_hora = (dados['deaths'] / dados['total_time']) * 60
                    
                    value = self._calcular_score_regiao(
                        xp_hora, kills_min, mortes_hora, dados['avg_mobs']
                    )
                else:
                    value = 0
            elif metrica == 'xp':
                value = dados['xp_gained']
            elif metrica == 'kills':
                value = dados['kills']
            elif metrica == 'deaths':
                value = dados['deaths']
            else:
                value = dados['visits']
            
            grid_matrix[y, x] = value
        
        # Cria visualização
        plt.figure(figsize=(12, 10))
        
        # Heatmap
        im = plt.imshow(grid_matrix, cmap='YlOrRd', interpolation='nearest')
        plt.colorbar(im, label=metrica.capitalize())
        
        # Adiciona valores nas células
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = grid_matrix[i, j]
                if value > 0:
                    text = plt.text(j, i, f'{value:.0f}',
                                  ha="center", va="center", color="black", fontsize=8)
        
        # Marca top hotspots
        top_3 = self.get_top_hotspots(n=3)
        for idx, (regiao_id, dados) in enumerate(top_3):
            pos_x = dados['pos_x']
            pos_y = dados['pos_y']
            grid_x, grid_y = map(int, self._posicao_para_grid(pos_x, pos_y).split(','))
            
            color = ['gold', 'silver', '#CD7F32'][idx]  # Ouro, Prata, Bronze
            circle = Circle((grid_x, grid_y), 0.3, color=color, fill=False, linewidth=3)
            plt.gca().add_patch(circle)
        
        plt.title(f'Heatmap de Hotspots - {metrica.capitalize()}', fontsize=16)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True, alpha=0.3)
        
        # Salva
        filename = self.heatmap_dir / f"heatmap_{metrica}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Heatmap salvo: {filename}")


def menu_interativo():
    """Menu para visualizar hotspots"""
    
    mapeador = MapeadorHotspots()
    
    while True:
        print("\n" + "="*70)
        print("🗺️  MAPEAMENTO DE HOTSPOTS")
        print("="*70)
        print("\n1. 📊 Ver relatório de hotspots")
        print("2. 🎨 Gerar heatmap (score)")
        print("3. 🎨 Gerar heatmap (XP)")
        print("4. 🎨 Gerar heatmap (Kills)")
        print("5. 🏆 Ver melhor hotspot")
        print("0. ❌ Voltar")
        
        escolha = input("\n➡️  Escolha: ").strip()
        
        if escolha == '0':
            break
        
        elif escolha == '1':
            mapeador.exibir_relatorio()
            input("\n⏸️  Pressione ENTER para continuar...")
        
        elif escolha == '2':
            mapeador.gerar_heatmap('score')
            input("\n⏸️  Pressione ENTER para continuar...")
        
        elif escolha == '3':
            mapeador.gerar_heatmap('xp')
            input("\n⏸️  Pressione ENTER para continuar...")
        
        elif escolha == '4':
            mapeador.gerar_heatmap('kills')
            input("\n⏸️  Pressione ENTER para continuar...")
        
        elif escolha == '5':
            melhor = mapeador.get_melhor_hotspot()
            
            if melhor:
                regiao_id, dados = melhor
                print(f"\n🌟 MELHOR HOTSPOT: {regiao_id}")
                print(f"   Score: {dados['score']:.2f}")
                print(f"   XP/hora: {dados['xp_por_hora_medio']:.4f}%")
                print(f"   Kills/min: {dados['kills_por_min_medio']:.2f}")
                print(f"   Posição: ({dados['pos_x']}, {dados['pos_y']})")
            else:
                print("\n⚠️  Nenhum hotspot mapeado")
            
            input("\n⏸️  Pressione ENTER para continuar...")
        
        else:
            print("❌ Opção inválida!")


if __name__ == "__main__":
    menu_interativo()
