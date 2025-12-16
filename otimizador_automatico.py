#!/usr/bin/env python3
"""
Otimizador Automático - Aplica ajustes de forma inteligente
Integra Auto-Calibração + A/B Testing + Predição
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from auto_calibracao import AutoCalibracao
except ImportError:
    print("❌ auto_calibracao.py não encontrado!")
    exit(1)

try:
    from ab_testing import ABTesting
except ImportError:
    ABTesting = None

try:
    from predicao_eventos import PredicaoEventos
except ImportError:
    PredicaoEventos = None


class OtimizadorAutomatico:
    """
    Sistema completo de otimização automática
    """
    
    def __init__(self, modo: str = 'conservador'):
        """
        Args:
            modo: 'conservador', 'agressivo', 'automatico'
        """
        self.modo = modo
        self.calibrador = AutoCalibracao()
        self.ab_testing = ABTesting() if ABTesting else None
        self.predicao = PredicaoEventos() if PredicaoEventos else None
        
        self.log_file = Path("ml_models/otimizacao_log.json")
        self.historico_otimizacoes = []
        
        self._carregar_historico()
    
    def _carregar_historico(self):
        """Carrega histórico de otimizações"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.historico_otimizacoes = data.get('otimizacoes', [])
            except Exception as e:
                print(f"⚠️ Erro ao carregar histórico: {e}")
    
    def _salvar_historico(self):
        """Salva histórico"""
        try:
            self.log_file.parent.mkdir(exist_ok=True)
            
            data = {
                'otimizacoes': self.historico_otimizacoes[-100:],
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar histórico: {e}")
    
    def analisar_e_otimizar(self, metricas: Dict[str, Any], aplicar: bool = True) -> Dict[str, Any]:
        """
        Analisa sessão e aplica otimizações
        
        Args:
            metricas: Métricas da sessão
            aplicar: Se True, aplica ajustes automaticamente
        
        Returns:
            Resultado da otimização
        """
        print("🔍 ANALISANDO PERFORMANCE...")
        print("="*70)
        
        # 1. Análise com Auto-Calibração
        resultado = self.calibrador.analisar_sessao(metricas)
        
        if resultado.get('status') == 'sessao_muito_curta':
            print("⚠️  Sessão muito curta para análise (mínimo 6 minutos)")
            return resultado
        
        # Exibe análise
        print(f"\n📊 SCORE GERAL: {resultado['score_geral']:.1f}/100")
        
        # Classifica performance
        score = resultado['score_geral']
        if score >= 85:
            classificacao = "🚀 EXCELENTE"
            cor = '\033[92m'  # Verde
        elif score >= 70:
            classificacao = "✅ BOM"
            cor = '\033[94m'  # Azul
        elif score >= 50:
            classificacao = "⚠️  REGULAR"
            cor = '\033[93m'  # Amarelo
        else:
            classificacao = "❌ RUIM"
            cor = '\033[91m'  # Vermelho
        
        reset = '\033[0m'
        print(f"{cor}{classificacao}{reset}")
        
        # 2. Mostra problemas
        if resultado.get('problemas'):
            print(f"\n⚠️  PROBLEMAS DETECTADOS ({len(resultado['problemas'])}):")
            for prob in resultado['problemas']:
                print(f"  • {prob['tipo']}: {prob['valor_atual']:.2f} (meta: {prob['meta']})")
        else:
            print("\n✅ Nenhum problema detectado!")
        
        # 3. Mostra ajustes sugeridos
        ajustes = resultado.get('ajustes_sugeridos', [])
        
        if ajustes:
            print(f"\n💡 AJUSTES SUGERIDOS ({len(ajustes)}):")
            for ajuste in ajustes:
                print(f"  • {ajuste['parametro']}: {ajuste['acao']}")
                print(f"    ↳ {ajuste['razao']}")
        else:
            print("\n✅ Configuração ótima! Nenhum ajuste necessário.")
        
        # 4. Decide se aplica
        if aplicar and ajustes:
            print("\n⚙️  APLICANDO AJUSTES AUTOMATICAMENTE...")
            
            # Verifica modo
            if self.modo == 'conservador':
                # Aplica apenas se score < 60
                if score < 60:
                    resultado_aplicacao = self.calibrador.aplicar_ajustes_automaticos(ajustes)
                    self._exibir_resultado_aplicacao(resultado_aplicacao)
                else:
                    print("   ℹ️  Modo conservador: Score aceitável, mantendo config atual")
            
            elif self.modo == 'agressivo':
                # Sempre aplica se houver ajustes
                resultado_aplicacao = self.calibrador.aplicar_ajustes_automaticos(ajustes)
                self._exibir_resultado_aplicacao(resultado_aplicacao)
            
            else:  # automático
                # Aplica se score < 70
                if score < 70:
                    resultado_aplicacao = self.calibrador.aplicar_ajustes_automaticos(ajustes)
                    self._exibir_resultado_aplicacao(resultado_aplicacao)
                else:
                    print("   ℹ️  Score bom, mantendo config atual")
        
        # 5. Registra no histórico
        self.historico_otimizacoes.append({
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'problemas': len(resultado.get('problemas', [])),
            'ajustes_aplicados': len(ajustes) if aplicar else 0,
            'metricas': metricas
        })
        self._salvar_historico()
        
        print("\n" + "="*70)
        
        return resultado
    
    def _exibir_resultado_aplicacao(self, resultado: Dict[str, Any]):
        """Exibe resultado da aplicação de ajustes"""
        if resultado.get('status') == 'ajustes_aplicados':
            ajustes = resultado.get('ajustes', {})
            
            if ajustes:
                print(f"   ✅ {len(ajustes)} ajuste(s) aplicado(s):")
                
                for param, info in ajustes.items():
                    print(f"\n   • {param}:")
                    print(f"     {info['valor_anterior']} → {info['valor_novo']}")
                    print(f"     Razão: {info['razao']}")
            else:
                print("   ℹ️  Nenhum ajuste necessário")
        else:
            print(f"   ❌ Erro ao aplicar: {resultado.get('erro', 'Desconhecido')}")
    
    def relatorio_completo(self) -> str:
        """Gera relatório completo de otimizações"""
        if not self.historico_otimizacoes:
            return "⚠️ Nenhuma otimização realizada ainda"
        
        # Pega últimas 10
        ultimas = self.historico_otimizacoes[-10:]
        
        relatorio = """
╔══════════════════════════════════════════════════════════════╗
║           📊 RELATÓRIO DE OTIMIZAÇÕES                        ║
╠══════════════════════════════════════════════════════════════╣
"""
        
        for i, opt in enumerate(ultimas, 1):
            timestamp = datetime.fromisoformat(opt['timestamp'])
            relatorio += f"""║
║  #{i:2d} - {timestamp.strftime('%d/%m/%Y %H:%M')}
║     Score: {opt['score']:.1f}/100
║     Problemas: {opt['problemas']}
║     Ajustes aplicados: {opt['ajustes_aplicados']}
"""
        
        relatorio += """║
╚══════════════════════════════════════════════════════════════╝
"""
        
        return relatorio
    
    def modo_interativo(self):
        """Modo interativo para testes"""
        print("🤖 OTIMIZADOR AUTOMÁTICO - MODO INTERATIVO")
        print("="*70)
        print(f"Modo atual: {self.modo}")
        print()
        
        # Simula métricas
        print("📝 Digite as métricas da sessão (ou Enter para exemplo):\n")
        
        try:
            duracao = input("  Duração (segundos) [3600]: ").strip()
            duracao = int(duracao) if duracao else 3600
            
            kills = input("  Kills [120]: ").strip()
            kills = int(kills) if kills else 120
            
            xp = input("  XP ganho (%) [45]: ").strip()
            xp = float(xp) if xp else 45.0
            
            mortes = input("  Mortes [1]: ").strip()
            mortes = int(mortes) if mortes else 1
            
            ocioso = input("  Tempo ocioso (segundos) [600]: ").strip()
            ocioso = int(ocioso) if ocioso else 600
        
        except KeyboardInterrupt:
            print("\n\n⏸️  Cancelado")
            return
        
        # Monta métricas
        metricas = {
            'duracao_segundos': duracao,
            'kills': kills,
            'xp_ganho': xp,
            'mortes': mortes,
            'tempo_ocioso': ocioso
        }
        
        print()
        
        # Analisa
        self.analisar_e_otimizar(metricas, aplicar=True)
        
        # Exibe relatório
        print("\n" + self.calibrador.relatorio_otimizacao())


def exemplo_uso_basico():
    """Exemplo de uso básico"""
    print("📚 EXEMPLO DE USO BÁSICO\n")
    
    # Cria otimizador
    otimizador = OtimizadorAutomatico(modo='automatico')
    
    # Métricas de exemplo (após 1h de farming)
    metricas = {
        'duracao_segundos': 3600,  # 1 hora
        'kills': 120,
        'xp_ganho': 45.0,
        'mortes': 1,
        'tempo_ocioso': 600  # 10 minutos
    }
    
    # Analisa e otimiza
    resultado = otimizador.analisar_e_otimizar(metricas, aplicar=True)
    
    # Exibe relatório
    print("\n" + otimizador.relatorio_completo())


def exemplo_integracao_bot():
    """Exemplo de integração no bot principal"""
    codigo_exemplo = """
# No início do main.py
from otimizador_automatico import OtimizadorAutomatico

# Cria otimizador (modo automático)
otimizador = OtimizadorAutomatico(modo='automatico')

# No loop principal, a cada 1 hora
tempo_inicio_sessao = time.time()
metricas_sessao = {
    'kills': 0,
    'xp_ganho': 0,
    'mortes': 0,
    'tempo_ocioso': 0
}

while farming:
    # ... código de farming ...
    
    # Atualiza métricas
    metricas_sessao['kills'] += 1  # Após cada kill
    metricas_sessao['xp_ganho'] += xp_atual  # XP detectado
    
    # A cada 1 hora
    tempo_atual = time.time()
    if (tempo_atual - tempo_inicio_sessao) >= 3600:
        # Prepara métricas
        metricas_sessao['duracao_segundos'] = tempo_atual - tempo_inicio_sessao
        
        # Otimiza automaticamente
        otimizador.analisar_e_otimizar(metricas_sessao, aplicar=True)
        
        # Reseta para próxima sessão
        tempo_inicio_sessao = tempo_atual
        metricas_sessao = {'kills': 0, 'xp_ganho': 0, 'mortes': 0, 'tempo_ocioso': 0}
"""
    
    print("📝 EXEMPLO DE INTEGRAÇÃO NO BOT:")
    print("="*70)
    print(codigo_exemplo)


if __name__ == "__main__":
    import sys
    
    print("🚀 OTIMIZADOR AUTOMÁTICO - Bot SRO Mobile")
    print("="*70)
    print()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == 'interativo':
            otimizador = OtimizadorAutomatico(modo='automatico')
            otimizador.modo_interativo()
        
        elif comando == 'exemplo':
            exemplo_uso_basico()
        
        elif comando == 'integracao':
            exemplo_integracao_bot()
        
        elif comando in ['conservador', 'agressivo', 'automatico']:
            print(f"Modo: {comando}")
            otimizador = OtimizadorAutomatico(modo=comando)
            otimizador.modo_interativo()
        
        else:
            print(f"❌ Comando inválido: {comando}")
    
    else:
        print("Uso:")
        print("  python3 otimizador_automatico.py interativo     # Modo interativo")
        print("  python3 otimizador_automatico.py exemplo        # Exemplo básico")
        print("  python3 otimizador_automatico.py integracao     # Ver integração")
        print("  python3 otimizador_automatico.py conservador    # Modo conservador")
        print("  python3 otimizador_automatico.py agressivo      # Modo agressivo")
        print()
        print("Modos de otimização:")
        print("  • conservador: Só ajusta se score < 60 (mais seguro)")
        print("  • automatico:  Ajusta se score < 70 (recomendado)")
        print("  • agressivo:   Sempre ajusta quando possível (experimental)")
        print()
        
        # Executa exemplo por padrão
        exemplo_uso_basico()
