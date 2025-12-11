#!/usr/bin/env python3
"""
Visualizador 3D Interativo de Densidade de Mobs
Mostra mapa de calor 3D das melhores áreas para farmar
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np
import json
import os
from ml_avancado import MLAvancado

class Visualizador3D:
    def __init__(self):
        self.ml = MLAvancado()
        
        # Configuração do plot
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(16, 10))
        
        # Cria subplots: 3D + 2 gráficos 2D
        self.ax_3d = self.fig.add_subplot(221, projection='3d')
        self.ax_heatmap = self.fig.add_subplot(222)
        self.ax_skills = self.fig.add_subplot(223)
        self.ax_horario = self.fig.add_subplot(224)
        
        self.fig.suptitle('📊 ML Avançado - Análise de Farming', 
                         fontsize=16, fontweight='bold')
        
        # Dados históricos para animação
        self.historico_densidade = []
        
    def atualizar_visualizacao(self, frame):
        """Atualiza todos os gráficos"""
        # Limpa plots
        self.ax_3d.clear()
        self.ax_heatmap.clear()
        self.ax_skills.clear()
        self.ax_horario.clear()
        
        # 1. Mapa de calor 3D
        self._plot_mapa_3d()
        
        # 2. Heatmap 2D (vista de cima)
        self._plot_heatmap_2d()
        
        # 3. Skills rankeadas
        self._plot_skills_ranking()
        
        # 4. Performance por horário
        self._plot_performance_horario()
        
        plt.tight_layout()
    
    def _plot_mapa_3d(self):
        """Plota mapa de calor 3D"""
        dados_mapa = self.ml.gerar_mapa_calor_3d(grid_size=50, max_x=1000, max_y=1000)
        
        if not dados_mapa['x']:
            self.ax_3d.text2D(0.5, 0.5, 'Coletando dados...', 
                            transform=self.ax_3d.transAxes,
                            ha='center', va='center', fontsize=14)
            return
        
        x = np.array(dados_mapa['x'])
        y = np.array(dados_mapa['y'])
        z = np.array(dados_mapa['densidade'])
        
        # Normaliza cores
        z_norm = (z - z.min()) / (z.max() - z.min() + 0.001)
        
        # Scatter 3D com cores gradiente
        scatter = self.ax_3d.scatter(x, y, z, c=z_norm, cmap='hot', 
                                     s=100, alpha=0.6, edgecolors='w', linewidth=0.5)
        
        # Adiciona barras verticais
        for i in range(len(x)):
            self.ax_3d.plot([x[i], x[i]], [y[i], y[i]], [0, z[i]], 
                           'c-', alpha=0.3, linewidth=1)
        
        self.ax_3d.set_xlabel('X (posição)', fontsize=10)
        self.ax_3d.set_ylabel('Y (posição)', fontsize=10)
        self.ax_3d.set_zlabel('EXP/min', fontsize=10)
        self.ax_3d.set_title('🗺️ Densidade de Mobs 3D', fontsize=12, fontweight='bold')
        
        # Adiciona colorbar
        self.fig.colorbar(scatter, ax=self.ax_3d, shrink=0.5, label='Densidade')
        
        # Marca top 3 áreas
        top_areas = self.ml.obter_areas_rankadas(3)
        if top_areas:
            for i, area in enumerate(top_areas):
                self.ax_3d.text(area['x'], area['y'], area['densidade'],
                              f"#{i+1}", fontsize=10, color='yellow', fontweight='bold')
    
    def _plot_heatmap_2d(self):
        """Plota heatmap 2D (vista de cima)"""
        dados_mapa = self.ml.gerar_mapa_calor_3d(grid_size=50, max_x=1000, max_y=1000)
        
        if not dados_mapa['x']:
            self.ax_heatmap.text(0.5, 0.5, 'Coletando dados...', 
                               ha='center', va='center', fontsize=14,
                               transform=self.ax_heatmap.transAxes)
            return
        
        x = np.array(dados_mapa['x'])
        y = np.array(dados_mapa['y'])
        z = np.array(dados_mapa['densidade'])
        
        # Cria grid para interpolação
        grid_size = dados_mapa['grid_size']
        x_unique = sorted(set(x))
        y_unique = sorted(set(y))
        
        if len(x_unique) > 1 and len(y_unique) > 1:
            # Cria matriz de densidade
            densidade_grid = np.zeros((len(y_unique), len(x_unique)))
            
            for i, xi in enumerate(x):
                x_idx = x_unique.index(xi)
                y_idx = y_unique.index(y[i])
                densidade_grid[y_idx, x_idx] = z[i]
            
            # Plota heatmap
            im = self.ax_heatmap.imshow(densidade_grid, cmap='hot', 
                                       interpolation='bilinear', origin='lower',
                                       extent=[min(x_unique), max(x_unique), 
                                             min(y_unique), max(y_unique)])
            
            self.fig.colorbar(im, ax=self.ax_heatmap, label='EXP/min')
            
            # Marca top áreas
            top_areas = self.ml.obter_areas_rankadas(5)
            for i, area in enumerate(top_areas):
                self.ax_heatmap.plot(area['x'], area['y'], 'y*', 
                                   markersize=15, markeredgecolor='white')
                self.ax_heatmap.text(area['x'], area['y'], f"#{i+1}", 
                                   ha='center', va='center', 
                                   fontsize=10, fontweight='bold')
        
        self.ax_heatmap.set_xlabel('X (posição)')
        self.ax_heatmap.set_ylabel('Y (posição)')
        self.ax_heatmap.set_title('🎯 Heatmap 2D - Top Áreas', fontweight='bold')
        self.ax_heatmap.grid(True, alpha=0.3)
    
    def _plot_skills_ranking(self):
        """Plota ranking de skills"""
        skills = self.ml.obter_skills_rankadas()
        
        if not skills:
            self.ax_skills.text(0.5, 0.5, 'Sem dados de skills ainda', 
                              ha='center', va='center', fontsize=12,
                              transform=self.ax_skills.transAxes)
            return
        
        # Pega top 10
        top_skills = skills[:10]
        
        skill_names = [f"Skill {s['skill_id']}" for s in top_skills]
        eficiencias = [s['eficiencia_media'] for s in top_skills]
        taxas = [s['taxa_sucesso'] * 100 for s in top_skills]
        
        # Bar plot duplo
        x_pos = np.arange(len(skill_names))
        width = 0.35
        
        bars1 = self.ax_skills.barh(x_pos - width/2, eficiencias, width, 
                                    label='Eficiência', color='cyan', alpha=0.8)
        bars2 = self.ax_skills.barh(x_pos + width/2, taxas, width, 
                                    label='Taxa Sucesso %', color='lime', alpha=0.8)
        
        self.ax_skills.set_yticks(x_pos)
        self.ax_skills.set_yticklabels(skill_names, fontsize=9)
        self.ax_skills.set_xlabel('Valor')
        self.ax_skills.set_title('⚔️ Ranking de Skills', fontweight='bold')
        self.ax_skills.legend(loc='lower right', fontsize=8)
        self.ax_skills.grid(axis='x', alpha=0.3)
        
        # Adiciona valores nas barras
        for bars in [bars1, bars2]:
            for bar in bars:
                width = bar.get_width()
                self.ax_skills.text(width, bar.get_y() + bar.get_height()/2,
                                  f'{width:.1f}',
                                  ha='left', va='center', fontsize=8)
    
    def _plot_performance_horario(self):
        """Plota performance por horário do dia"""
        if not self.ml.performance_por_hora:
            self.ax_horario.text(0.5, 0.5, 'Sem dados de horário ainda', 
                               ha='center', va='center', fontsize=12,
                               transform=self.ax_horario.transAxes)
            return
        
        horas = []
        medias = []
        maximos = []
        
        for hora in range(24):
            if hora in self.ml.performance_por_hora:
                valores = self.ml.performance_por_hora[hora]
                if valores:
                    horas.append(hora)
                    medias.append(np.mean(valores))
                    maximos.append(np.max(valores))
        
        if not horas:
            return
        
        # Plot de linha com área preenchida
        self.ax_horario.plot(horas, medias, 'o-', color='cyan', 
                           linewidth=2, markersize=8, label='Média')
        self.ax_horario.fill_between(horas, 0, medias, alpha=0.3, color='cyan')
        
        # Linha de máximo
        self.ax_horario.plot(horas, maximos, 's--', color='yellow', 
                           linewidth=1.5, markersize=6, alpha=0.7, label='Pico')
        
        # Marca melhor horário
        melhor = self.ml.obter_melhor_horario()
        if melhor:
            hora_melhor, exp_melhor = melhor
            self.ax_horario.axvline(hora_melhor, color='lime', 
                                   linestyle='--', linewidth=2, alpha=0.7)
            self.ax_horario.text(hora_melhor, max(medias) * 1.1, 
                               f'Melhor: {hora_melhor}h\n{exp_melhor:.0f} exp/min',
                               ha='center', fontsize=9, 
                               bbox=dict(boxstyle='round', facecolor='lime', alpha=0.3))
        
        self.ax_horario.set_xlabel('Hora do Dia', fontsize=10)
        self.ax_horario.set_ylabel('EXP/min', fontsize=10)
        self.ax_horario.set_title('⏰ Performance por Horário', fontweight='bold')
        self.ax_horario.set_xticks(range(0, 24, 2))
        self.ax_horario.grid(True, alpha=0.3)
        self.ax_horario.legend(loc='upper left', fontsize=8)
    
    def iniciar(self, intervalo=5000):
        """Inicia visualização com atualização automática"""
        print("🚀 Iniciando Visualizador 3D ML Avançado...")
        print("📊 Atualização a cada 5 segundos")
        print("🔄 Feche a janela para sair")
        print()
        
        # Animação
        anim = FuncAnimation(self.fig, self.atualizar_visualizacao, 
                           interval=intervalo, cache_frame_data=False)
        
        plt.show()

if __name__ == '__main__':
    visualizador = Visualizador3D()
    visualizador.iniciar()
