#!/usr/bin/env python3
"""
Sistema de Notificações Multi-Plataforma
Envia alertas via Telegram, Discord, Email ou notificação desktop
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import subprocess
import os

class SistemaNotificacoes:
    """
    Sistema completo de notificações
    Suporta: Telegram, Discord, Email, Desktop
    """
    
    def __init__(self):
        self.config_file = Path("notificacoes_config.json")
        self.config = self._carregar_config()
        
        # Histórico de notificações
        self.historico = []
    
    def _carregar_config(self) -> Dict[str, Any]:
        """Carrega configuração de notificações"""
        config_padrao = {
            'telegram': {
                'ativo': False,
                'token': '',
                'chat_id': ''
            },
            'discord': {
                'ativo': False,
                'webhook_url': ''
            },
            'email': {
                'ativo': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'usuario': '',
                'senha': '',
                'destinatario': ''
            },
            'desktop': {
                'ativo': True  # Padrão ativo
            },
            'filtros': {
                'nivel_minimo': 'info',  # debug, info, warning, error, critical
                'enviar_kills': False,
                'enviar_level_up': True,
                'enviar_morte': True,
                'enviar_erro': True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_salva = json.load(f)
                    # Merge com padrão
                    for key, value in config_salva.items():
                        if key in config_padrao:
                            config_padrao[key].update(value)
                    return config_padrao
            except Exception as e:
                print(f"⚠️ Erro ao carregar config: {e}")
        
        # Salva config padrão
        self._salvar_config(config_padrao)
        return config_padrao
    
    def _salvar_config(self, config: Dict[str, Any]):
        """Salva configuração"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar config: {e}")
    
    def _deve_enviar(self, tipo: str, nivel: str) -> bool:
        """Verifica se deve enviar notificação"""
        filtros = self.config['filtros']
        
        # Verifica tipo específico
        tipo_config = f'enviar_{tipo}'
        if tipo_config in filtros and not filtros[tipo_config]:
            return False
        
        # Verifica nível
        niveis = ['debug', 'info', 'warning', 'error', 'critical']
        nivel_min = filtros.get('nivel_minimo', 'info')
        
        if nivel not in niveis or nivel_min not in niveis:
            return True
        
        return niveis.index(nivel) >= niveis.index(nivel_min)
    
    def enviar_telegram(self, mensagem: str) -> bool:
        """Envia mensagem via Telegram"""
        config = self.config['telegram']
        
        if not config['ativo']:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{config['token']}/sendMessage"
            
            data = {
                'chat_id': config['chat_id'],
                'text': mensagem,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Erro ao enviar Telegram: {e}")
            return False
    
    def enviar_discord(self, mensagem: str) -> bool:
        """Envia mensagem via Discord webhook"""
        config = self.config['discord']
        
        if not config['ativo']:
            return False
        
        try:
            data = {
                'content': mensagem,
                'username': 'Bot SRO'
            }
            
            response = requests.post(
                config['webhook_url'],
                json=data,
                timeout=10
            )
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Erro ao enviar Discord: {e}")
            return False
    
    def enviar_desktop(self, titulo: str, mensagem: str) -> bool:
        """Envia notificação desktop"""
        config = self.config['desktop']
        
        if not config['ativo']:
            return False
        
        try:
            # Linux
            subprocess.run([
                'notify-send',
                titulo,
                mensagem,
                '--icon=dialog-information'
            ], check=False)
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar notificação desktop: {e}")
            return False
    
    def notificar(
        self,
        mensagem: str,
        tipo: str = 'info',
        nivel: str = 'info',
        titulo: str = 'Bot SRO'
    ):
        """
        Envia notificação para todos os canais ativos
        
        Args:
            mensagem: Texto da mensagem
            tipo: Tipo (kills, level_up, morte, erro)
            nivel: Nível (debug, info, warning, error, critical)
            titulo: Título da notificação
        """
        # Verifica se deve enviar
        if not self._deve_enviar(tipo, nivel):
            return
        
        # Formata mensagem com emoji
        emojis = {
            'debug': '🔍',
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨'
        }
        
        emoji = emojis.get(nivel, 'ℹ️')
        mensagem_formatada = f"{emoji} {mensagem}"
        
        # Envia para cada canal
        enviados = []
        
        if self.config['telegram']['ativo']:
            if self.enviar_telegram(mensagem_formatada):
                enviados.append('Telegram')
        
        if self.config['discord']['ativo']:
            if self.enviar_discord(mensagem_formatada):
                enviados.append('Discord')
        
        if self.config['desktop']['ativo']:
            if self.enviar_desktop(titulo, mensagem):
                enviados.append('Desktop')
        
        # Registra histórico
        self.historico.append({
            'timestamp': datetime.now().isoformat(),
            'tipo': tipo,
            'nivel': nivel,
            'mensagem': mensagem,
            'canais': enviados
        })
    
    def notificar_kill(self, numero: int):
        """Notificação de kill milestone"""
        if numero % 100 == 0:  # A cada 100 kills
            self.notificar(
                f"🎯 {numero} kills alcançados!",
                tipo='kills',
                nivel='info'
            )
    
    def notificar_level_up(self, level: int):
        """Notificação de level up"""
        self.notificar(
            f"🎉 LEVEL UP! Agora você é level {level}!",
            tipo='level_up',
            nivel='warning',
            titulo='🎉 Level UP!'
        )
    
    def notificar_morte(self):
        """Notificação de morte"""
        self.notificar(
            f"💀 Você morreu! Hora: {datetime.now().strftime('%H:%M:%S')}",
            tipo='morte',
            nivel='error',
            titulo='💀 Morte'
        )
    
    def notificar_erro(self, erro: str):
        """Notificação de erro"""
        self.notificar(
            f"❌ Erro no bot: {erro}",
            tipo='erro',
            nivel='critical',
            titulo='❌ Erro Crítico'
        )
    
    def notificar_pausa_longa(self, duracao_minutos: int):
        """Notificação de pausa longa (bot parado)"""
        self.notificar(
            f"⏸️ Bot pausado por {duracao_minutos} minutos",
            tipo='info',
            nivel='warning'
        )
    
    def notificar_sessao_completa(self, metricas: Dict[str, Any]):
        """Notificação de fim de sessão com resumo"""
        duracao = metricas.get('duracao_total', 0) / 3600
        
        mensagem = f"""
📊 <b>SESSÃO CONCLUÍDA</b>

⏱️ Duração: {duracao:.1f}h
⚔️ Kills: {metricas.get('kills_total', 0)}
💰 XP: {metricas.get('xp_total', 0):.2f}%
💀 Mortes: {metricas.get('mortes', 0)}
📈 XP/min: {metricas.get('xp_por_minuto', 0):.2f}%
"""
        
        self.notificar(
            mensagem,
            tipo='info',
            nivel='info',
            titulo='📊 Sessão Concluída'
        )
    
    def configurar_telegram(self, token: str, chat_id: str):
        """Configura Telegram"""
        self.config['telegram']['token'] = token
        self.config['telegram']['chat_id'] = chat_id
        self.config['telegram']['ativo'] = True
        self._salvar_config(self.config)
        print("✅ Telegram configurado!")
    
    def configurar_discord(self, webhook_url: str):
        """Configura Discord"""
        self.config['discord']['webhook_url'] = webhook_url
        self.config['discord']['ativo'] = True
        self._salvar_config(self.config)
        print("✅ Discord configurado!")
    
    def testar_notificacoes(self):
        """Testa todas as notificações"""
        print("🧪 TESTANDO NOTIFICAÇÕES")
        print("="*70)
        
        self.notificar(
            "Teste de notificação - Bot funcionando!",
            tipo='info',
            nivel='info',
            titulo='🧪 Teste'
        )
        
        print("\n✅ Notificações enviadas!")
        print(f"   Canais ativos: ", end="")
        
        ativos = []
        if self.config['telegram']['ativo']:
            ativos.append('Telegram')
        if self.config['discord']['ativo']:
            ativos.append('Discord')
        if self.config['desktop']['ativo']:
            ativos.append('Desktop')
        
        print(", ".join(ativos) if ativos else "Nenhum")


if __name__ == "__main__":
    print("🔔 SISTEMA DE NOTIFICAÇÕES")
    print("="*70)
    
    notif = SistemaNotificacoes()
    
    print("\n📱 Configuração atual:")
    print(f"  Telegram: {'✅' if notif.config['telegram']['ativo'] else '❌'}")
    print(f"  Discord:  {'✅' if notif.config['discord']['ativo'] else '❌'}")
    print(f"  Desktop:  {'✅' if notif.config['desktop']['ativo'] else '❌'}")
    
    print("\n💡 Para configurar Telegram:")
    print("   1. Fale com @BotFather no Telegram")
    print("   2. Crie um bot e pegue o token")
    print("   3. Fale com @userinfobot para pegar seu chat_id")
    print("   4. Execute:")
    print('      notif.configurar_telegram("SEU_TOKEN", "SEU_CHAT_ID")')
    
    print("\n💡 Para configurar Discord:")
    print("   1. Vá em Configurações do Servidor > Integrações > Webhooks")
    print("   2. Crie um webhook e copie a URL")
    print("   3. Execute:")
    print('      notif.configurar_discord("SUA_WEBHOOK_URL")')
    
    print("\n🧪 Testando notificações...")
    notif.testar_notificacoes()
