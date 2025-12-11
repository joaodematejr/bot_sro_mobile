#!/usr/bin/env python3
"""
Visualizador de Métricas do Bot Ultra
Mostra gráficos em tempo real do desempenho do farming
"""

import json
import os
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from collections import deque
import numpy as np

class VisualizadorMetricas:
    def __init__(self, arquivo_metricas='metricas_bot.json'):
        self.arquivo = arquivo_metricas
        self.historico_xp = deque(maxlen=100)
        self.historico_combates = deque(maxlen=100)
        self.historico_mortes = deque(maxlen=100)
        self.historico_xp_min = deque(maxlen=100)
        self.historico_exp_real = deque(maxlen=100)  # EXP real ganho
        self.timestamps = deque(maxlen=100)
        
        # Configuração da figura
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('📊 Bot Ultra - Métricas em Tempo Real', fontsize=16, fontweight='bold')
        
        # Grid de layouts
        gs = GridSpec(3, 3, figure=self.fig, hspace=0.3, wspace=0.3)
        
        # Gráficos
        self.ax_xp = self.fig.add_subplot(gs[0, :2])  # XP Progress (grande)
        self.ax_combates = self.fig.add_subplot(gs[1, 0])  # Combates
        self.ax_mortes = self.fig.add_subplot(gs[1, 1])  # Mortes
        self.ax_xp_min = self.fig.add_subplot(gs[1, 2])  # XP/min
        self.ax_skills = self.fig.add_subplot(gs[2, 0])  # Skills
        self.ax_eficiencia = self.fig.add_subplot(gs[2, 1])  # Eficiência
        self.ax_stats = self.fig.add_subplot(gs[0, 2])  # Stats resumo
        self.ax_mapa_calor = self.fig.add_subplot(gs[2, 2])  # Mapa de calor
        
        # Remove eixos do painel de stats
        self.ax_stats.axis('off')
        
        # Cores
        self.cor_xp = '#00ff88'
        self.cor_combate = '#ff6b6b'
        self.cor_morte = '#ff4444'
        self.cor_skill = '#4ecdc4'
        self.cor_eficiencia = '#ffd93d'
        
    def ler_metricas(self):
        """Lê arquivo de métricas"""
        try:
            if os.path.exists(self.arquivo):
                with open(self.arquivo, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao ler métricas: {e}")
        return None
    
    def atualizar_graficos(self, frame):
        """Atualiza todos os gráficos"""
        metricas = self.ler_metricas()
        if not metricas:
            return
        
        # Adiciona timestamp
        agora = datetime.now()
        self.timestamps.append(agora)
        
        # Adiciona dados
        self.historico_xp.append(metricas.get('xp_porcentagem', 0))
        self.historico_combates.append(metricas.get('combates_vencidos', 0))
        self.historico_mortes.append(metricas.get('mortes', 0))
        self.historico_xp_min.append(metricas.get('xp_por_minuto', 0))
        self.historico_exp_real.append(metricas.get('exp_total_ganho', 0))
        
        # Limpa gráficos
        self.ax_xp.clear()
        self.ax_combates.clear()
        self.ax_mortes.clear()
        self.ax_xp_min.clear()
        self.ax_skills.clear()
        self.ax_eficiencia.clear()
        self.ax_stats.clear()
        self.ax_mapa_calor.clear()
        
        # 1. Gráfico de XP (Principal)
        if len(self.historico_xp) > 1:
            self.ax_xp.plot(list(self.historico_xp), color=self.cor_xp, linewidth=2, marker='o', markersize=3)
            self.ax_xp.fill_between(range(len(self.historico_xp)), self.historico_xp, alpha=0.3, color=self.cor_xp)
            self.ax_xp.set_title(f'📈 Progresso XP: {metricas.get("xp_porcentagem", 0):.2f}%', fontsize=14, fontweight='bold')
            self.ax_xp.set_ylabel('XP %')
            self.ax_xp.grid(True, alpha=0.3)
            self.ax_xp.set_ylim([0, 100])
            
            # Linha de meta (100%)
            self.ax_xp.axhline(y=100, color='gold', linestyle='--', linewidth=2, label='Meta: Level 100')
            self.ax_xp.legend()
        
        # 2. Gráfico de Combates
        if len(self.historico_combates) > 1:
            self.ax_combates.bar(range(len(self.historico_combates)), self.historico_combates, color=self.cor_combate, alpha=0.7)
            self.ax_combates.set_title(f'⚔️ Combates: {metricas.get("combates_vencidos", 0)}', fontsize=12, fontweight='bold')
            self.ax_combates.set_ylabel('Total')
            self.ax_combates.grid(True, alpha=0.3)
        
        # 3. Gráfico de Mortes
        if len(self.historico_mortes) > 1:
            self.ax_mortes.plot(list(self.historico_mortes), color=self.cor_morte, linewidth=2, marker='x', markersize=5)
            self.ax_mortes.set_title(f'💀 Mortes: {metricas.get("mortes", 0)}', fontsize=12, fontweight='bold')
            self.ax_mortes.set_ylabel('Total')
            self.ax_mortes.grid(True, alpha=0.3)
        
        # 4. Gráfico de XP/min
        if len(self.historico_xp_min) > 1:
            self.ax_xp_min.plot(list(self.historico_xp_min), color=self.cor_eficiencia, linewidth=2, marker='s', markersize=3)
            self.ax_xp_min.fill_between(range(len(self.historico_xp_min)), self.historico_xp_min, alpha=0.3, color=self.cor_eficiencia)
            self.ax_xp_min.set_title(f'⚡ XP/min: {metricas.get("xp_por_minuto", 0):.2f}', fontsize=12, fontweight='bold')
            self.ax_xp_min.set_ylabel('XP/min')
            self.ax_xp_min.grid(True, alpha=0.3)
        
        # 5. Gráfico de Skills (Pizza)
        skills_usadas = metricas.get('skills_usadas', 0)
        combates = metricas.get('combates_vencidos', 1)
        skills_por_combate = skills_usadas / max(combates, 1)
        
        labels = ['Skills Usadas', 'Skills Restantes']
        valores = [skills_usadas % 100, 100 - (skills_usadas % 100)]
        cores = [self.cor_skill, '#333333']
        
        self.ax_skills.pie(valores, labels=labels, colors=cores, autopct='%1.1f%%', startangle=90)
        self.ax_skills.set_title(f'💥 Skills: {skills_usadas}\n({skills_por_combate:.1f}/combate)', fontsize=12, fontweight='bold')
        
        # 6. Gráfico de Eficiência (Taxa de Sobrevivência)
        total_encontros = combates + metricas.get('mortes', 0)
        taxa_sucesso = (combates / max(total_encontros, 1)) * 100
        
        self.ax_eficiencia.barh(['Sucesso', 'Morte'], [taxa_sucesso, 100 - taxa_sucesso], color=[self.cor_xp, self.cor_morte])
        self.ax_eficiencia.set_title(f'📊 Taxa de Sucesso: {taxa_sucesso:.1f}%', fontsize=12, fontweight='bold')
        self.ax_eficiencia.set_xlim([0, 100])
        self.ax_eficiencia.grid(True, alpha=0.3, axis='x')
        
        # 7. Painel de Stats (Texto)
        self.ax_stats.axis('off')
        tempo_decorrido = metricas.get('tempo_decorrido', '00:00:00')
        tempo_estimado = metricas.get('tempo_estimado_lvl_100', 'N/A')
        potions = metricas.get('potions_usadas', 0)
        loots = metricas.get('loots_coletados', 0)
        imagens = metricas.get('imagens_salvas', 0)
        
        # Dados de EXP real
        exp_total = metricas.get('exp_total_ganho', 0)
        exp_atual = metricas.get('exp_atual_level', 0)
        exp_necessario = metricas.get('exp_necessario_level', 1000000)
        porcentagem_level = metricas.get('porcentagem_level_atual', 0)
        tempo_proximo_level = metricas.get('tempo_proximo_level', 'N/A')
        data_proximo_level = metricas.get('data_proximo_level', 'N/A')
        media_exp = metricas.get('media_exp_por_combate', 0)
        
        stats_texto = f"""
╔══════════════════════════════╗
║     📊 ESTATÍSTICAS GERAIS     ║
╚══════════════════════════════╝

⏱️  Tempo Rodando: {tempo_decorrido}
🎯 Meta Level 100: {tempo_estimado}

⚔️  Combates: {combates}
💀 Mortes: {metricas.get('mortes', 0)}
💥 Skills: {skills_usadas}
🧪 Poções: {potions}
💰 Loots: {loots}

📸 Imagens ML: {imagens}

⚡ XP/min: {metricas.get('xp_por_minuto', 0):.2f}
📈 XP Atual: {metricas.get('xp_porcentagem', 0):.2f}%

💎 EXP REAL:
   Total: {exp_total:,}
   Level: {porcentagem_level:.1f}%
   Média: {media_exp:,}/cbt
   
📅 Próximo Level:
   {tempo_proximo_level}
   {data_proximo_level}
        """
        
        self.ax_stats.text(0.1, 0.5, stats_texto, fontsize=11, family='monospace',
                          verticalalignment='center', color='white',
                          bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))
        
        # 8. Mapa de Calor de Densidade ML
        if 'observacoes_ml' in metricas and len(metricas['observacoes_ml']) > 0:
            obs = metricas['observacoes_ml']
            # Cria grid 10x10 para mapa de calor
            grid_size = 10
            heatmap = np.zeros((grid_size, grid_size))
            
            for o in obs:
                x_idx = min(int((o['x'] % 1000) / 100), grid_size - 1)
                y_idx = min(int((o['y'] % 1000) / 100), grid_size - 1)
                heatmap[y_idx, x_idx] += o['densidade']
            
            im = self.ax_mapa_calor.imshow(heatmap, cmap='YlOrRd', interpolation='bilinear')
            self.ax_mapa_calor.set_title('🗺️ Mapa de Densidade', fontsize=12, fontweight='bold')
            self.ax_mapa_calor.set_xticks([])
            self.ax_mapa_calor.set_yticks([])
            plt.colorbar(im, ax=self.ax_mapa_calor, fraction=0.046, pad=0.04)
        else:
            self.ax_mapa_calor.text(0.5, 0.5, 'Coletando dados...', 
                                   ha='center', va='center', fontsize=12, color='gray')
            self.ax_mapa_calor.set_xticks([])
            self.ax_mapa_calor.set_yticks([])
    
    def iniciar(self):
        """Inicia visualização em tempo real"""
        ani = animation.FuncAnimation(self.fig, self.atualizar_graficos, interval=2000, cache_frame_data=False)
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    print("🚀 Iniciando Visualizador de Métricas...")
    print("📊 Atualizando a cada 2 segundos")
    print("❌ Feche a janela para sair\n")
    
    visualizador = VisualizadorMetricas()
    visualizador.iniciar()
