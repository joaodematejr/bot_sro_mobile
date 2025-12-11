#!/usr/bin/env python3
"""
Sistema de Métricas de Aprendizado ML
Monitora e visualiza o progresso do treinamento
"""

import json
import time
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class MetricasAprendizado:
    def __init__(self, arquivo_ml='ml_avancado_dados.json'):
        self.arquivo_ml = arquivo_ml
        
        # Histórico de métricas
        self.historico_score = []  # Score do modelo ao longo do tempo
        self.historico_predicoes = []  # Qualidade das previsões
        self.historico_decisoes = []  # Decisões tomadas pelo ML vs aleatório
        
        # Métricas de performance
        self.exp_antes_ml = []  # EXP/hora antes do ML
        self.exp_depois_ml = []  # EXP/hora depois do ML
        self.acertos_predicao = []  # % de acerto nas previsões
        
        # Setup plot
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(16, 10))
        
    def calcular_metricas_atuais(self):
        """Calcula métricas atuais do sistema ML"""
        if not os.path.exists(self.arquivo_ml):
            return None
        
        try:
            with open(self.arquivo_ml, 'r') as f:
                dados = json.load(f)
        except:
            return None
        
        metricas = {
            'timestamp': datetime.now(),
            'total_dados': 0,
            'areas_mapeadas': 0,
            'skills_analisadas': 0,
            'combos_aprendidos': 0,
            'horarios_analisados': 0,
            'densidade_media': 0,
            'variancia_densidade': 0,
            'melhor_area': None,
            'pior_area': None,
            'skill_mais_eficiente': None,
            'melhor_horario': None,
            'taxa_exploracao': 0,  # % do mapa explorado
            'confianca_modelo': 0,  # Quão confiante está o ML
        }
        
        # Rotas
        rotas = dados.get('historico_rotas', [])
        metricas['total_dados'] = len(rotas)
        
        if rotas:
            exp_mins = [r.get('exp_por_minuto', 0) for r in rotas if r.get('exp_por_minuto', 0) > 0]
            if exp_mins:
                metricas['densidade_media'] = np.mean(exp_mins)
                metricas['variancia_densidade'] = np.std(exp_mins)
        
        # Áreas
        densidade = dados.get('densidade_mobs', {})
        metricas['areas_mapeadas'] = len(densidade)
        
        if densidade:
            # Encontra melhor e pior área
            areas_com_densidade = []
            for coord_str, info in densidade.items():
                if info['tempo_total'] > 0:
                    dens = (info['exp_total'] / info['tempo_total']) * 60
                    coords = tuple(map(int, coord_str.split(',')))
                    areas_com_densidade.append({
                        'coords': coords,
                        'densidade': dens,
                        'combates': info['combates']
                    })
            
            if areas_com_densidade:
                areas_com_densidade.sort(key=lambda x: x['densidade'], reverse=True)
                metricas['melhor_area'] = areas_com_densidade[0]
                metricas['pior_area'] = areas_com_densidade[-1]
                
                # Taxa de exploração (assumindo mapa 1000x1000, grid 50x50)
                max_areas = (1000 // 50) ** 2  # 400 áreas possíveis
                metricas['taxa_exploracao'] = (len(densidade) / max_areas) * 100
        
        # Skills
        skills = dados.get('historico_skills', {})
        metricas['skills_analisadas'] = len(skills)
        
        if skills:
            skills_eficiencia = []
            for skill_id, registros in skills.items():
                if len(registros) >= 3:
                    eficiencias = [r.get('eficiencia', 0) for r in registros]
                    skills_eficiencia.append({
                        'skill_id': skill_id,
                        'eficiencia_media': np.mean(eficiencias),
                        'usos': len(registros)
                    })
            
            if skills_eficiencia:
                skills_eficiencia.sort(key=lambda x: x['eficiencia_media'], reverse=True)
                metricas['skill_mais_eficiente'] = skills_eficiencia[0]
        
        # Combos
        combos = dados.get('combos_eficientes', [])
        metricas['combos_aprendidos'] = len(combos)
        
        # Horários
        performance_hora = dados.get('performance_por_hora', {})
        metricas['horarios_analisados'] = len(performance_hora)
        
        if performance_hora:
            # Encontra melhor horário
            medias_hora = {}
            for hora, valores in performance_hora.items():
                if len(valores) >= 3:
                    medias_hora[int(hora)] = np.mean(valores)
            
            if medias_hora:
                melhor_h = max(medias_hora.items(), key=lambda x: x[1])
                metricas['melhor_horario'] = {
                    'hora': melhor_h[0],
                    'exp_min': melhor_h[1]
                }
        
        # Confiança do modelo (baseado em quantidade de dados)
        # Mais dados = maior confiança (máximo 100%)
        confianca = min(100, (metricas['total_dados'] / 200) * 100)
        metricas['confianca_modelo'] = confianca
        
        return metricas
    
    def calcular_ganho_ml(self):
        """Calcula ganho de performance com ML"""
        if not os.path.exists(self.arquivo_ml):
            return None
        
        try:
            with open(self.arquivo_ml, 'r') as f:
                dados = json.load(f)
        except:
            return None
        
        rotas = dados.get('historico_rotas', [])
        if len(rotas) < 40:  # Precisa de dados suficientes
            return None
        
        # Separa primeiros 20 (antes ML treinar) e últimos 20 (depois ML)
        primeiros = rotas[:20]
        ultimos = rotas[-20:]
        
        exp_antes = [r.get('exp_por_minuto', 0) for r in primeiros if r.get('exp_por_minuto', 0) > 0]
        exp_depois = [r.get('exp_por_minuto', 0) for r in ultimos if r.get('exp_por_minuto', 0) > 0]
        
        if not exp_antes or not exp_depois:
            return None
        
        media_antes = np.mean(exp_antes)
        media_depois = np.mean(exp_depois)
        
        ganho_percentual = ((media_depois - media_antes) / media_antes) * 100
        
        return {
            'exp_min_antes': media_antes,
            'exp_min_depois': media_depois,
            'ganho_absoluto': media_depois - media_antes,
            'ganho_percentual': ganho_percentual,
            'melhoria': media_depois > media_antes
        }
    
    def gerar_relatorio_texto(self):
        """Gera relatório textual do aprendizado"""
        metricas = self.calcular_metricas_atuais()
        ganho = self.calcular_ganho_ml()
        
        print("\n" + "="*70)
        print("📊 RELATÓRIO DE APRENDIZADO ML")
        print("="*70)
        print(f"\n🕐 Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        if not metricas:
            print("\n⚠️  Ainda não há dados suficientes.")
            print("   Execute o bot para começar a coletar dados!")
            return
        
        print(f"\n📈 PROGRESSO DO TREINAMENTO:")
        print(f"   • Dados coletados: {metricas['total_dados']} rotas")
        print(f"   • Áreas mapeadas: {metricas['areas_mapeadas']}")
        print(f"   • Skills analisadas: {metricas['skills_analisadas']}")
        print(f"   • Combos aprendidos: {metricas['combos_aprendidos']}")
        print(f"   • Horários analisados: {metricas['horarios_analisados']}")
        
        # Barra de progresso
        confianca = metricas['confianca_modelo']
        barra_total = 40
        barra_preenchida = int((confianca / 100) * barra_total)
        barra = '█' * barra_preenchida + '░' * (barra_total - barra_preenchida)
        print(f"\n🎯 CONFIANÇA DO MODELO: [{barra}] {confianca:.1f}%")
        
        if confianca < 30:
            print("   ⚠️  Modelo ainda aprendendo - Colete mais dados")
        elif confianca < 60:
            print("   📚 Aprendizado em progresso - Continue coletando")
        elif confianca < 90:
            print("   ✅ Modelo funcional - Otimizações ativas")
        else:
            print("   🏆 Modelo bem treinado - Máxima eficiência!")
        
        print(f"\n🗺️  MAPEAMENTO:")
        print(f"   • Exploração: {metricas['taxa_exploracao']:.1f}% do mapa")
        
        if metricas['densidade_media'] > 0:
            print(f"   • Densidade média: {metricas['densidade_media']:.1f} exp/min")
            print(f"   • Variância: ±{metricas['variancia_densidade']:.1f}")
        
        if metricas['melhor_area']:
            coords = metricas['melhor_area']['coords']
            dens = metricas['melhor_area']['densidade']
            comb = metricas['melhor_area']['combates']
            print(f"\n🏆 MELHOR ÁREA DESCOBERTA:")
            print(f"   • Coordenadas: ({coords[0]}, {coords[1]})")
            print(f"   • Densidade: {dens:.1f} exp/min")
            print(f"   • Combates: {comb}")
        
        if metricas['skill_mais_eficiente']:
            skill = metricas['skill_mais_eficiente']
            print(f"\n⚔️  SKILL MAIS EFICIENTE:")
            print(f"   • Skill ID: {skill['skill_id']}")
            print(f"   • Eficiência: {skill['eficiencia_media']:.2f}")
            print(f"   • Usos: {skill['usos']}")
        
        if metricas['melhor_horario']:
            hora = metricas['melhor_horario']
            print(f"\n⏰ MELHOR HORÁRIO:")
            print(f"   • Hora: {hora['hora']}:00")
            print(f"   • Performance: {hora['exp_min']:.1f} exp/min")
        
        # Ganho com ML
        if ganho:
            print(f"\n💰 GANHO COM ML:")
            print(f"   • Antes ML: {ganho['exp_min_antes']:.1f} exp/min")
            print(f"   • Depois ML: {ganho['exp_min_depois']:.1f} exp/min")
            print(f"   • Ganho: {ganho['ganho_absoluto']:+.1f} exp/min ({ganho['ganho_percentual']:+.1f}%)")
            
            if ganho['melhoria']:
                print(f"   ✅ MELHORIA DETECTADA!")
            else:
                print(f"   ⚠️  Ainda estabilizando...")
        else:
            print(f"\n💰 GANHO COM ML:")
            print(f"   ⏳ Aguardando mais dados (mín. 40 rotas)")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        if metricas['total_dados'] < 20:
            print(f"   • Continue farmando para coletar dados iniciais")
        elif metricas['total_dados'] < 50:
            print(f"   • ML começando a otimizar - Aguarde resultados")
        elif metricas['areas_mapeadas'] < 10:
            print(f"   • Explore mais áreas para melhor cobertura")
        elif metricas['taxa_exploracao'] < 20:
            print(f"   • Expanda área de farming para mais dados")
        else:
            print(f"   • Sistema otimizado! Continue farmando")
            if metricas['melhor_area']:
                coords = metricas['melhor_area']['coords']
                print(f"   • Foque na área ({coords[0]}, {coords[1]}) para máximo EXP")
        
        print("\n" + "="*70)
    
    def visualizar_evolucao(self):
        """Cria gráficos de evolução do aprendizado"""
        metricas = self.calcular_metricas_atuais()
        
        if not metricas or metricas['total_dados'] < 10:
            print("⚠️  Dados insuficientes para visualização")
            print("   Execute o bot para coletar mais dados!")
            return
        
        # Carrega dados
        with open(self.arquivo_ml, 'r') as f:
            dados = json.load(f)
        
        rotas = dados.get('historico_rotas', [])
        
        # Cria subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('📊 Evolução do Aprendizado ML', fontsize=16, fontweight='bold')
        
        # 1. EXP/min ao longo do tempo
        exp_mins = [r.get('exp_por_minuto', 0) for r in rotas]
        indices = list(range(len(exp_mins)))
        
        ax1.plot(indices, exp_mins, 'c-', alpha=0.3, linewidth=1)
        # Média móvel (janela de 10)
        if len(exp_mins) >= 10:
            media_movel = np.convolve(exp_mins, np.ones(10)/10, mode='valid')
            ax1.plot(range(9, len(exp_mins)), media_movel, 'lime', linewidth=2, label='Média Móvel')
        
        ax1.axhline(metricas['densidade_media'], color='yellow', linestyle='--', 
                   linewidth=1, alpha=0.7, label=f"Média: {metricas['densidade_media']:.1f}")
        ax1.set_xlabel('Combates')
        ax1.set_ylabel('EXP/min')
        ax1.set_title('🚀 Evolução de Performance')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Distribuição de densidade por área
        densidade_vals = []
        densidade_dict = dados.get('densidade_mobs', {})
        for info in densidade_dict.values():
            if info['tempo_total'] > 0:
                dens = (info['exp_total'] / info['tempo_total']) * 60
                densidade_vals.append(dens)
        
        if densidade_vals:
            ax2.hist(densidade_vals, bins=20, color='cyan', alpha=0.7, edgecolor='white')
            ax2.axvline(np.mean(densidade_vals), color='lime', linestyle='--', 
                       linewidth=2, label=f'Média: {np.mean(densidade_vals):.1f}')
            ax2.set_xlabel('EXP/min')
            ax2.set_ylabel('Quantidade de Áreas')
            ax2.set_title('📊 Distribuição de Densidade')
            ax2.legend()
            ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Progresso de exploração
        areas_ao_tempo = []
        areas_vistas = set()
        for rota in rotas:
            x, y = rota.get('x', 0), rota.get('y', 0)
            coord = (int(x // 50) * 50, int(y // 50) * 50)
            areas_vistas.add(coord)
            areas_ao_tempo.append(len(areas_vistas))
        
        ax3.plot(areas_ao_tempo, 'c-', linewidth=2)
        ax3.fill_between(range(len(areas_ao_tempo)), areas_ao_tempo, alpha=0.3)
        ax3.set_xlabel('Combates')
        ax3.set_ylabel('Áreas Únicas Descobertas')
        ax3.set_title('🗺️ Progresso de Exploração')
        ax3.grid(True, alpha=0.3)
        
        # 4. Confiança do modelo ao longo do tempo
        confianca_tempo = []
        for i in range(1, len(rotas) + 1):
            conf = min(100, (i / 200) * 100)
            confianca_tempo.append(conf)
        
        ax4.plot(confianca_tempo, 'lime', linewidth=2)
        ax4.fill_between(range(len(confianca_tempo)), confianca_tempo, alpha=0.3, color='lime')
        ax4.axhline(30, color='red', linestyle='--', alpha=0.5, label='Mínimo')
        ax4.axhline(60, color='yellow', linestyle='--', alpha=0.5, label='Funcional')
        ax4.axhline(90, color='green', linestyle='--', alpha=0.5, label='Ótimo')
        ax4.set_xlabel('Combates')
        ax4.set_ylabel('Confiança (%)')
        ax4.set_title('🎯 Confiança do Modelo')
        ax4.set_ylim(0, 105)
        ax4.legend(loc='lower right')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

def main():
    metricas = MetricasAprendizado()
    
    print("\n🤖 SISTEMA DE MÉTRICAS DE APRENDIZADO ML")
    print("="*70)
    print("\nOpções:")
    print("  1. Relatório Textual")
    print("  2. Visualização Gráfica")
    print("  3. Ambos")
    print()
    
    escolha = input("Escolha (1/2/3) [3]: ").strip() or "3"
    
    if escolha in ["1", "3"]:
        metricas.gerar_relatorio_texto()
    
    if escolha in ["2", "3"]:
        print("\n📊 Gerando visualizações...")
        metricas.visualizar_evolucao()

if __name__ == '__main__':
    main()
