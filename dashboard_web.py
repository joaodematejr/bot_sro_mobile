#!/usr/bin/env python3
"""
Dashboard Web em Tempo Real
Monitora bot via navegador com atualização automática
"""

from flask import Flask, render_template, jsonify, make_response
from flask_socketio import SocketIO
import json
import threading
import time
from pathlib import Path
from datetime import datetime
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bot_sro_secret'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Desabilita cache
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, cors_allowed_origins="*")

class DashboardMonitor:
    """Monitora dados do bot em tempo real"""
    
    def __init__(self):
        self.analytics_folder = Path("analytics_data")
        self.ml_folder = Path("ml_models")
        
        self.dados_cache = {
            'metricas_atuais': {},
            'historico_xp': [],
            'historico_kills': [],
            'modelo_ml': {},
            'alertas': []
        }
        
        self.rodando = False
    
    def carregar_ultima_metrica(self) -> dict:
        """Carrega última métrica salva"""
        if not self.analytics_folder.exists():
            return {}
        
        try:
            # Lista arquivos de métricas
            arquivos = sorted(self.analytics_folder.glob("metrics_*.json"))
            
            if not arquivos:
                return {}
            
            # Pega o mais recente
            ultimo = arquivos[-1]
            
            with open(ultimo, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar métrica: {e}")
            return {}
    
    def carregar_historico(self, limite: int = 50) -> list:
        """Carrega histórico de métricas"""
        if not self.analytics_folder.exists():
            return []
        
        try:
            arquivos = sorted(self.analytics_folder.glob("metrics_*.json"))[-limite:]
            
            historico = []
            for arquivo in arquivos:
                with open(arquivo, 'r') as f:
                    data = json.load(f)
                    stats = data.get('statistics', {})
                    xp_data = stats.get('xp', {})
                    combat_data = stats.get('combat', {})
                    session_data = stats.get('session', {})
                    
                    historico.append({
                        'timestamp': session_data.get('start', ''),
                        'xp_total': xp_data.get('current', 0),
                        'kills_total': combat_data.get('kills', 0),
                        'xp_por_minuto': xp_data.get('xp_per_minute', 0)
                    })
            
            return historico
        except Exception as e:
            print(f"⚠️ Erro ao carregar histórico: {e}")
            return []
    
    def atualizar_dados(self):
        """Atualiza dados do cache"""
        # Métricas atuais
        self.dados_cache['metricas_atuais'] = self.carregar_ultima_metrica()
        
        # Histórico
        historico = self.carregar_historico()
        if historico:
            self.dados_cache['historico_xp'] = [
                {'x': h['timestamp'], 'y': h['xp_total']}
                for h in historico
            ]
            self.dados_cache['historico_kills'] = [
                {'x': h['timestamp'], 'y': h['kills_total']}
                for h in historico
            ]
        
        # Modelo ML
        try:
            modelo_path = self.ml_folder / "training_metrics.json"
            if modelo_path.exists():
                with open(modelo_path, 'r') as f:
                    self.dados_cache['modelo_ml'] = json.load(f)
        except:
            pass
        
        # Gera alertas
        self.gerar_alertas()
    
    def gerar_alertas(self):
        """Gera alertas baseado nas métricas"""
        alertas = []
        
        metricas = self.dados_cache['metricas_atuais']
        
        if not metricas:
            return
        
        # Extrai estatísticas corretamente
        stats = metricas.get('statistics', {})
        xp_data = stats.get('xp', {})
        combat_data = stats.get('combat', {})
        
        # Alerta de XP baixo
        xp_min = xp_data.get('xp_per_minute', 0)
        if xp_min > 0 and xp_min < 0.5:
            alertas.append({
                'tipo': 'warning',
                'mensagem': f'XP/min baixo: {xp_min:.2f}%/min',
                'timestamp': datetime.now().isoformat()
            })
        
        # Alerta de mortes
        mortes = combat_data.get('deaths', 0)
        if mortes > 3:
            alertas.append({
                'tipo': 'danger',
                'mensagem': f'Muitas mortes: {mortes}',
                'timestamp': datetime.now().isoformat()
            })
        
        # Alerta de kills altos
        kills = combat_data.get('kills', 0)
        kills_min = combat_data.get('kills_per_minute', 0)
        
        if kills_min > 2.5:
            alertas.append({
                'tipo': 'success',
                'mensagem': f'Excelente farming: {kills_min:.2f} kills/min!',
                'timestamp': datetime.now().isoformat()
            })
        
        self.dados_cache['alertas'] = alertas[-10:]  # Últimos 10
    
    def loop_atualizacao(self):
        """Loop de atualização contínua"""
        while self.rodando:
            self.atualizar_dados()
            
            # Emite atualização via WebSocket
            socketio.emit('atualizacao', self.dados_cache)
            
            time.sleep(5)  # Atualiza a cada 5 segundos
    
    def iniciar(self):
        """Inicia monitoramento"""
        self.rodando = True
        thread = threading.Thread(target=self.loop_atualizacao, daemon=True)
        thread.start()
    
    def parar(self):
        """Para monitoramento"""
        self.rodando = False


# Instância global
monitor = DashboardMonitor()


@app.route('/')
def index():
    """Página principal"""
    response = make_response(render_template('dashboard_sro.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/api/metricas')
def api_metricas():
    """API REST para métricas"""
    return jsonify(monitor.dados_cache)


@app.route('/api/status')
def api_status():
    """Status do bot"""
    metricas = monitor.dados_cache.get('metricas_atuais', {})
    stats = metricas.get('statistics', {})
    session_data = stats.get('session', {})
    
    return jsonify({
        'online': bool(metricas),
        'uptime': session_data.get('elapsed', '0:00:00'),
        'ultima_atualizacao': datetime.now().isoformat()
    })


@socketio.on('connect')
def handle_connect():
    """Cliente conectou"""
    print('🔌 Cliente conectado ao dashboard')
    socketio.emit('atualizacao', monitor.dados_cache)


@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectou"""
    print('🔌 Cliente desconectado')


def criar_html_dashboard():
    """Cria arquivo HTML do dashboard"""
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bot SRO - Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --sro-bg: #0b0f1a;
            --sro-bg-soft: #131a27;
            --sro-panel: #1e2a3a;
            --sro-gold: #d4af37;
            --sro-gold-soft: rgba(212, 175, 55, 0.15);
            --sro-text: #e6e6e6;
            --sro-danger: #c0392b;
            --sro-warning: #e67e22;
            --sro-success: #27ae60;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--sro-bg);
            color: var(--sro-text);
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            color: var(--sro-gold);
            text-shadow: 0 0 8px rgba(212,175,55,0.25);
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: var(--sro-bg-soft);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.35);
            border: 1px solid rgba(212,175,55,0.25);
        }
        
        .card h2 {
            margin-bottom: 15px;
            font-size: 1.3em;
            opacity: 0.9;
        }
        
        .metric {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
            color: var(--sro-gold);
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.7;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        
        .alerta {
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.06);
        }
        
        .alerta.success { border-left: 4px solid var(--sro-success); }
        .alerta.warning { border-left: 4px solid var(--sro-warning); }
        .alerta.danger  { border-left: 4px solid var(--sro-danger); }
        
        .status-online {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: var(--sro-success);
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Bot SRO Mobile - Dashboard</h1>
        
        <div class="grid">
            <!-- Status -->
            <div class="card">
                <h2><span class="status-online"></span>Status</h2>
                <div class="metric" id="uptime">--:--:--</div>
                <div class="metric-label">Tempo ativo</div>
            </div>
            
            <!-- XP -->
            <div class="card">
                <h2>💰 Experiência</h2>
                <div class="metric" id="xp-total">0%</div>
                <div class="metric-label"><span id="xp-min">0</span>%/min</div>
            </div>
            
            <!-- Kills -->
            <div class="card">
                <h2>⚔️ Combate</h2>
                <div class="metric" id="kills">0</div>
                <div class="metric-label"><span id="kills-min">0</span> kills/min</div>
            </div>
            
            <!-- Eficiência -->
            <div class="card">
                <h2>📊 Eficiência</h2>
                <div class="metric" id="score">0</div>
                <div class="metric-label">Score geral</div>
            </div>
        </div>
        
        <!-- Gráficos -->
        <div class="grid">
            <div class="card">
                <h2>📈 Histórico de XP</h2>
                <div class="chart-container">
                    <canvas id="chart-xp"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>⚔️ Histórico de Kills</h2>
                <div class="chart-container">
                    <canvas id="chart-kills"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Alertas -->
        <div class="card">
            <h2>🔔 Alertas</h2>
            <div id="alertas">
                <p style="opacity: 0.5;">Nenhum alerta</p>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        
        // Gráficos
        const ctxXP = document.getElementById('chart-xp').getContext('2d');
        const chartXP = new Chart(ctxXP, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'XP Total',
                    data: [],
                    borderColor: '#d4af37',
                    backgroundColor: 'rgba(212, 175, 55, 0.12)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { type: 'time', display: false },
                    y: { beginAtZero: true }
                },
                plugins: { legend: { display: false } }
            }
        });
        
        const ctxKills = document.getElementById('chart-kills').getContext('2d');
        const chartKills = new Chart(ctxKills, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Kills Total',
                    data: [],
                    borderColor: '#e67e22',
                    backgroundColor: 'rgba(230, 126, 34, 0.12)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { type: 'time', display: false },
                    y: { beginAtZero: true }
                },
                plugins: { legend: { display: false } }
            }
        });
        
        // Atualização via WebSocket
        socket.on('atualizacao', function(dados) {
            console.log('📥 Dados recebidos', dados);
            const metricas = dados.metricas_atuais || {};
            const stats = metricas.statistics || {};
            const xp = stats.xp || {};
            const combat = stats.combat || {};
            const session = stats.session || {};

            // Atualiza métricas (usando estrutura aninhada)
            if (session.elapsed) {
                // elapsed já vem como string HH:MM:SS em muitos casos
                document.getElementById('uptime').textContent = session.elapsed;
            } else if (session.duration_seconds !== undefined) {
                const dur = Number(session.duration_seconds) || 0;
                const h = Math.floor(dur / 3600);
                const m = Math.floor((dur % 3600) / 60);
                const s = Math.floor(dur % 60);
                document.getElementById('uptime').textContent = 
                    `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
            } else {
                // Fallback: se houver histórico, calcula uptime aproximado
                const hist = dados.historico_xp || [];
                if (hist.length > 1) {
                    try {
                        const t0 = new Date(hist[0].x).getTime();
                        const t1 = new Date(hist[hist.length-1].x).getTime();
                        const dur = Math.max(0, (t1 - t0) / 1000);
                        const h = Math.floor(dur / 3600);
                        const m = Math.floor((dur % 3600) / 60);
                        const s = Math.floor(dur % 60);
                        document.getElementById('uptime').textContent = 
                            `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
                    } catch (e) { console.warn('Uptime fallback falhou', e); }
                }
            }

            if (xp.current !== undefined) {
                const val = Number(xp.current) || 0;
                document.getElementById('xp-total').textContent = val.toFixed(2) + '%';
            } else if (dados.historico_xp && dados.historico_xp.length) {
                const ultimo = dados.historico_xp[dados.historico_xp.length-1];
                const val = Number(ultimo.y) || 0;
                document.getElementById('xp-total').textContent = val.toFixed(2) + '%';
            }

            if (xp.xp_per_minute !== undefined) {
                const val = Number(xp.xp_per_minute) || 0;
                document.getElementById('xp-min').textContent = val.toFixed(2);
            } else if (dados.historico_xp && dados.historico_xp.length > 1) {
                const a = dados.historico_xp;
                const t0 = new Date(a[0].x).getTime();
                const t1 = new Date(a[a.length-1].x).getTime();
                const dv = Number(a[a.length-1].y) - Number(a[0].y);
                const mins = Math.max(1, (t1 - t0) / 60000);
                const val = dv / mins;
                document.getElementById('xp-min').textContent = val.toFixed(2);
            }

            if (combat.kills !== undefined) {
                document.getElementById('kills').textContent = Number(combat.kills) || 0;
            } else if (dados.historico_kills && dados.historico_kills.length) {
                const ultimo = dados.historico_kills[dados.historico_kills.length-1];
                document.getElementById('kills').textContent = Number(ultimo.y) || 0;
            }

            if (combat.kills_per_minute !== undefined) {
                const val = Number(combat.kills_per_minute) || 0;
                document.getElementById('kills-min').textContent = val.toFixed(1);
            } else if (dados.historico_kills && dados.historico_kills.length > 1) {
                const b = dados.historico_kills;
                const t0 = new Date(b[0].x).getTime();
                const t1 = new Date(b[b.length-1].x).getTime();
                const dv = Number(b[b.length-1].y) - Number(b[0].y);
                const mins = Math.max(1, (t1 - t0) / 60000);
                const val = dv / mins;
                document.getElementById('kills-min').textContent = val.toFixed(1);
            }
            
            // Atualiza gráficos
            if (dados.historico_xp) {
                chartXP.data.datasets[0].data = dados.historico_xp;
                chartXP.update();
            }
            
            if (dados.historico_kills) {
                chartKills.data.datasets[0].data = dados.historico_kills;
                chartKills.update();
            }
            
            // Alertas
            if (dados.alertas && dados.alertas.length > 0) {
                const alertasHTML = dados.alertas.map(a => 
                    `<div class="alerta ${a.tipo}">${a.mensagem}</div>`
                ).join('');
                document.getElementById('alertas').innerHTML = alertasHTML;
            }
        });
        
        console.log('📊 Dashboard conectado!');
    </script>
</body>
</html>
"""
    
    # Cria pasta templates
    Path("templates").mkdir(exist_ok=True)
    
    with open("templates/dashboard.html", 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == "__main__":
    print("🌐 INICIANDO DASHBOARD WEB")
    print("="*70)
    
    # Cria HTML
    criar_html_dashboard()
    print("✅ Template HTML criado")
    
    # Inicia monitor
    monitor.iniciar()
    print("✅ Monitor iniciado")
    
    print("\n🌐 Dashboard disponível em:")
    print("   http://localhost:5000")
    print("\n   Abra no navegador para visualizar em tempo real!")
    print("\n   Pressione Ctrl+C para parar\n")
    
    # Inicia servidor Flask (suporta PORT via ambiente)
    import os
    porta = int(os.environ.get('PORT', '5000'))
    try:
        socketio.run(app, host='0.0.0.0', port=porta, debug=False)
    except OSError:
        # Tenta porta alternativa se a padrão estiver em uso
        porta_alt = porta + 1
        print(f"⚠️ Porta {porta} em uso, tentando {porta_alt}...")
        socketio.run(app, host='0.0.0.0', port=porta_alt, debug=False)
