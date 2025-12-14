# 🎮 Bot SRO Mobile - Sistema Completo de Farming Inteligente

Bot automatizado ultra-avançado para Silkroad Origin Mobile usando controle ADB (Android Debug Bridge). Sistema completo com **Inteligência Artificial**, **Machine Learning**, **Computer Vision**, **Analytics Detalhado**, **Sistema de Recompensas**, **Treinamento com Feedback** e **Mapeamento de Hotspots**.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Sistemas Inteligentes](#-sistemas-inteligentes)
- [Sistemas Avançados de ML](#-sistemas-avançados-de-ml)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Uso](#-uso)
- [Analytics e Métricas](#-analytics-e-métricas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Troubleshooting](#-troubleshooting)

## ⚡ Funcionalidades

### 🤖 Automação Principal

- ✅ **Farming Infinito** - Loop automático de combate e loot
- ✅ **Sistema de Target** - Detecção e ataque automático de inimigos
- ✅ **Uso de Skills** - Rotação inteligente de habilidades
- ✅ **Coleta de Loot** - Pickup automático de itens
- ✅ **Reset de Câmera** - Mantém visão ideal
- ✅ **Movimentação Inteligente** - Exploração de áreas baseada em ML
- ✅ **Sistema de Recuperação** - Detecção e uso de potions

### 🛡️ Sistema de Proteção Inteligente

- 🚨 **Detecção de HP Baixo** - Monitora saúde via análise de pixel
- 🔔 **Notificações do Sistema** - Alertas visuais e sonoros
- ⚠️ **Detecção de Inimigos Perigosos** - OCR identifica bosses/elites
- 🏃 **Sistema de Fuga Automática** - Evita combates perigosos
- 💊 **Auto-Potion** - Uso automático de consumíveis

### 🧠 Inteligência Artificial

#### Machine Learning (Scikit-learn)

- 🎓 **RandomForest Regressor** - Predição de densidade de inimigos
- 🗺️ **KMeans Clustering** - Identificação de hotspots de farming
- 📊 **StandardScaler** - Normalização de features para melhor acurácia
- 💾 **Auto-Treinamento** - Treina automaticamente a cada 100 amostras
- 📈 **Múltiplos Modelos** - 4 formatos salvos (sklearn, ultra, ultra_adb, avancado)
- 🔄 **Treinamento Contínuo** - Melhora ao longo do tempo

#### Computer Vision (OpenCV)

- 🎨 **Detecção de Cores** - `cv2.inRange()` para identificar elementos por cor
- ⭕ **Detecção de Círculos** - `cv2.HoughCircles()` para encontrar inimigos no minimap
- 📝 **OCR de Coordenadas** - Lê posição X,Y do personagem via Tesseract
- 🗺️ **Análise de Minimap** - 8 setores com contagem de inimigos
- 🎯 **Detecção de Combate** - ImageHash para identificar estado de batalha
- 📊 **Análise de Densidade** - Heatmap de áreas com mais inimigos

#### Advanced Vision

- 🌈 **8 Cores Pré-configuradas** - Vermelho, azul, verde, amarelo, roxo, laranja, branco, preto
- 🔍 **Multi-Detecção** - Combina cor + círculo + OCR
- 📐 **Vetor de Movimento** - Calcula direção baseado em coordenadas
- ⚙️ **Configurável** - Todos os parâmetros ajustáveis via JSON

#### Algoritmo de Decisão

1. **Análise de Minimap** → Conta inimigos por setor
2. **Machine Learning** → Prevê densidade esperada
3. **Clustering** → Identifica área mais promissora
4. **Decisão de Movimento** → Move para direção ideal
5. **Feedback Loop** → Coleta dados para próximo treinamento

### 📊 Analytics Completo

#### Tracking de XP
- 📈 **XP Atual via OCR** - Lê porcentagem exata da barra de XP
- 💰 **Detecção de EXP Ganho** - OCR identifica quantidade exata após combate
- ⚡ **XP/min em Tempo Real** - Calcula taxa de ganho
- 🎯 **Previsão de Level** - Estima tempo para 100% baseado em XP/min
- 📊 **Histórico Completo** - Salva timeline de todo o progresso

#### Estatísticas de Combate
- ⚔️ **Kills Tracking** - Conta mortes de inimigos
- 💀 **Death Counter** - Registra mortes do personagem
- ⏱️ **Duração de Combate** - Tempo médio por batalha
- 📈 **Kills/min** - Taxa de abate
- 🎯 **Eficiência de Combate** - Análise completa de performance

#### Recursos e Consumíveis
- 💊 **Potions Usadas** - Conta HP/MP/Vigor
- 💥 **Skills Utilizadas** - Tracking por habilidade
- 💰 **Loot Coletado** - Histórico de itens
- 📊 **Taxa de Uso** - Consumo médio por tempo

#### Sistema de Sessões
- 🆔 **Session ID Único** - Cada farming tem identificador
- 💾 **Auto-Save** - Salva progresso automaticamente
- 📁 **Histórico Persistente** - Mantém dados de todas as sessões
- 📤 **Export JSON** - Gera arquivo com todas as métricas

### 🎓 Sistema de Métricas de Aprendizado ML

#### Monitoramento de Treinamento
- 📊 **Timeline de Amostras** - Histórico completo de coleta
- ⏱️ **Tempo de Treinamento** - Duração de cada treino
- 🎯 **Acurácia (R² Score)** - Qualidade do modelo
- 📈 **Curva de Aprendizado** - Visualização de progresso
- 🏆 **Milestones** - Metas (10, 50, 100, 200, 500, 1000+ amostras)

#### Análise de Performance
- 📈 **Tendências** - Detecta melhora/piora em XP/min, kills/min, duração combate
- 🔗 **Correlação ML-Performance** - Mede impacto real do ML na eficiência
- 💡 **Insights Automáticos** - Recomendações baseadas em dados
- 📊 **Dashboard Ao Vivo** - Visualização em tempo real do progresso
- 🎨 **Barras de Progresso** - Acompanhamento visual de metas

#### Exportação e Relatórios
- 📄 **Relatório Resumido** - Texto formatado com principais métricas
- 💾 **Export JSON Detalhado** - Todos os dados para análise externa
- 📊 **Métricas de Sessão** - Taxa de coleta, amostras/min
- 🎯 **Próximo Marco** - Mostra quantas amostras faltam para meta

### 🔔 Sistema de Notificações

- 🖥️ **Notificações do Sistema** - Via libnotify (Linux)
- 🚨 **Alertas de Perigo** - Quando detecta inimigos perigosos
- ⚠️ **Urgência Crítica** - Som + ícone de alerta
- ⏱️ **Duração Configurável** - 10s para alertas importantes

## 🎯 Sistemas Avançados de ML

### 💰 Sistema de Recompensas (`sistema_recompensas.py`)

Sistema de **Reinforcement Learning** que avalia qualidade das ações do bot em tempo real.

#### Pesos de Recompensas
- ✅ **Kill** = +10 pontos
- ✅ **Kill Rápido** (< 10s) = +5 pontos
- ✅ **Multi-Kill** (3+ em 30s) = +15 pontos
- ✅ **XP Ganho** = +1 por 0.01%
- ⚔️ **Sem Dano** = +2 pontos
- 🎯 **Mob Próximo** = +5 pontos
- 🏃 **Fuga Sucesso** = +8 pontos
- 💎 **Item Coletado** = +3 pontos
- 🗺️ **Área Boa** = +5 pontos
- 🔥 **AOE Eficiente** (3+ mobs) = +7 pontos
- ⚡ **Skill Eficiente** = +3 pontos

#### Penalidades
- ❌ **Morte** = -50 pontos
- ⚠️ **HP Crítico** (< 20%) = -10 pontos
- 🩹 **HP Baixo** (< 50%) = -5 pontos
- ⏱️ **Tempo Ocioso** = -2 pontos/min
- 📍 **Área Ruim** = -3 pontos
- 🚫 **Stuck** (sem movimento) = -8 pontos
- 💥 **Skill Desperdiçada** = -2 pontos

#### Funcionalidades
```python
# Registra estado e calcula recompensa
recompensa = sistema.registrar_estado({
    'hp_percent': 85,
    'mobs_nearby': 3,
    'xp_percent': 45.5,
    'in_combat': True,
    'kills_recent': 2
})

# Relatório completo ao finalizar
sistema.finalizar_sessao()  # Mostra melhores/piores ações
```

#### Saída
```
💰 Sistema de Recompensas - Relatório Final
============================================================
📊 Estatísticas da Sessão:
   Duração: 45.2 min
   Estados registrados: 542
   Recompensa total: +1,247.5
   Recompensa média: +2.30 por estado
   Melhor recompensa: +25.0
   Pior recompensa: -15.0

🏆 Melhores Ações:
   #1. Multi-kill + XP alto: +25.0
   #2. Kill rápido + sem dano: +17.0
   #3. AOE eficiente: +15.0

⚠️ Piores Ações:
   #1. HP crítico + área ruim: -15.0
   #2. Morte: -50.0
```

### 🎓 Treinador com Recompensas (`treinador_recompensas.py`)

Treina **RandomForest** usando recompensas como **sample weights** para aprendizado acelerado.

#### Características
- 🌲 **RandomForest**: 300 estimators, max_depth=20
- ⚡ **GradientBoosting**: 200 estimators, max_depth=8 (alternativa)
- 🎯 **Sample Weighting**: Ações com alta recompensa = maior peso no treino
- 📊 **Comparação**: Mostra melhora vs modelo anterior
- 🔍 **Feature Importance**: Identifica features mais relevantes

#### Uso
```bash
# Menu interativo
python3 treinador_recompensas.py

# Treinamento rápido
./treinar_rapido.sh
```

#### Saída
```
🎓 Treinando RandomForest com Recompensas...
============================================================
✅ Modelo treinado com 4,500 amostras
   Acurácia: 87.3%
   Tempo: 2.45s

📊 Comparação com Modelo Anterior:
   Modelo antigo: 82.1% acurácia
   Modelo novo: 87.3% acurácia
   Melhora: +5.2% ⬆️

🔍 Features Mais Importantes:
   1. enemy_count: 34.2%
   2. hour: 18.5%
   3. sector_N: 12.3%
```

### 🗺️ Mapeamento de Hotspots (`mapeamento_hotspots.py`)

Sistema que **identifica e ranqueia** as melhores áreas de farming automaticamente.

#### Grid de Mapeamento
- 📍 Grid **10x10** (100 células)
- 📊 Rastreia: XP/hora, Kills/min, Mortes, Densidade de mobs
- 🏆 Calcula **score de qualidade** por região
- 🎨 Gera **heatmaps visuais** com matplotlib

#### Cálculo de Score
```python
Score = XP/hora × 1000 × 0.5        # 50% peso
      + Kills/min × 20 × 0.3         # 30% peso
      + Mobs médios × 5 × 0.1        # 10% peso
      - Mortes/hora × 10 × 0.1       # 10% penalidade
```

#### Uso
```bash
# 1. Rodar bot (coleta dados automaticamente)
python3 main.py

# 2. Ver hotspots mapeados
./ver_hotspots.sh
# OU
python3 mapeamento_hotspots.py
```

#### Menu Interativo
```
🗺️  MAPEAMENTO DE HOTSPOTS
======================================
1. 📊 Ver relatório de hotspots
2. 🎨 Gerar heatmap (score)
3. 🎨 Gerar heatmap (XP)
4. 🎨 Gerar heatmap (Kills)
5. 🏆 Ver melhor hotspot
0. ❌ Voltar
```

#### Saída
```
🏆 TOP 3 HOTSPOTS:
----------------------------------------------------------------------
#1. auto_5,5
   Score: 127.45
   XP/hora: 0.0245%
   Kills/min: 3.2
   Mortes/hora: 0.0
   Mobs médios: 8.5
   Sessões: 3
   🌟🌟🌟 MELHOR HOTSPOT!

#2. auto_4,6
   Score: 98.30
   XP/hora: 0.0198%
   Kills/min: 2.8
   🌟🌟 Excelente!

#3. auto_6,5
   Score: 85.67
   XP/hora: 0.0176%
   Kills/min: 2.5
   🌟🌟 Excelente!
```

#### Heatmaps Gerados
- 📊 `heatmap_score_*.png` - Qualidade geral
- 💰 `heatmap_xp_*.png` - XP ganho
- ⚔️ `heatmap_kills_*.png` - Kills por região

### 🔍 Detector Visual Corrigido (`detector_corrigido.py`)

Detecção precisa de objetos **apenas no minimap**.

#### Melhorias
- ✅ **Crop do minimap**: Analisa região (150,150) → 200x200
- ✅ **HSV otimizado**: S≥200, V≥200 (cores vibrantes)
- ✅ **Auto-cleanup**: Mantém apenas 10 imagens debug
- ✅ **Blob detection**: min_area=20, max_area=500

#### Cores Detectadas
- 🔴 **Vermelho**: Inimigos (HSV: 0-10, 200-255, 200-255)
- 🔵 **Azul**: Aliados (HSV: 100-130, 180-255, 180-255)
- 🟡 **Amarelo**: Itens/NPCs (HSV: 20-30, 200-255, 200-255)

### 📊 Análise de Diversidade (`analisar_diversidade.py`)

Ferramenta de diagnóstico para qualidade dos dados de treino.

#### Métricas
- 🎯 **Unicidade**: % de amostras únicas
- 📊 **Variância**: Features com baixa variância
- 📏 **Distâncias**: Similaridade entre amostras
- 💡 **Recomendações**: Quantos clusters usar

#### Exemplo de Saída
```
📊 Análise de Diversidade - 4,300 amostras
============================================================
✅ Amostras únicas: 2,228 (51.8%)
⚠️  Features baixa variância: 44%
📏 Distância média: 3.45
💡 Recomendação: Use 5-10 clusters (não 3)
```


## 📦 Requisitos

### Sistema
- Linux (testado em Pop!_OS/Ubuntu)
- Python 3.10+
- Android Debug Bridge (ADB)
- Waydroid ou dispositivo Android conectado via rede

### Dependências Python
```bash
numpy>=1.23.0
pillow>=10.0.0
scikit-learn>=1.3.0
opencv-python>=4.8.0
imagehash>=4.3.0
pytesseract>=0.3.10
```

### Ferramentas do Sistema
```bash
android-tools-adb        # Controle Android
tesseract-ocr            # OCR para leitura de texto
tesseract-ocr-por        # Idioma português para OCR
libnotify-bin           # Notificações do sistema (Linux)
```

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <repo-url> bot_sro_mobile
cd bot_sro_mobile
```

### 2. Instale dependências do sistema
```bash
sudo apt-get update
sudo apt-get install -y android-tools-adb tesseract-ocr tesseract-ocr-por libnotify-bin
```

### 3. Instale dependências Python
```bash
pip3 install -r requirements.txt
```

### 4. Conecte ao dispositivo Android
```bash
# Para Waydroid
adb connect 192.168.240.112:5555

# Para dispositivo físico (encontre o IP nas configurações)
adb connect SEU_IP:5555

# Verifique conexão
adb devices
```

## ⚙️ Configuração

### Arquivo de Configuração (`config_farming_adb.json`)

O bot gera automaticamente um arquivo de configuração. Principais seções:

#### Configuração Básica
```json
{
  "adb_device": "192.168.240.112:5555",
  "screen_width": 1920,
  "screen_height": 993,
  
  "joystick_centro_x": 288,
  "joystick_centro_y": 868,
  "joystick_raio": 73,
  
  "posicoes_skills": [
    {"nome": "Skill 1", "x": 1632, "y": 744},
    {"nome": "Skill 2", "x": 1728, "y": 784},
    {"nome": "Skill 3", "x": 1536, "y": 784}
  ]
}
```

#### Configuração de IA
```json
{
  "ia_config": {
    "usar_ia": true,
    "usar_ml": true,
    "usar_advanced_vision": true,
    "intervalo_analise_ia": 5,
    "min_amostras_treino": 10
  },
  
  "advanced_vision": {
    "detect_colors_enabled": true,
    "detect_circles_enabled": true,
    "read_coords_enabled": true,
    "target_colors": ["vermelho", "azul", "amarelo"],
    "coord_region": {"x": 10, "y": 10, "width": 200, "height": 30}
  }
}
```

#### Configuração de Analytics
```json
{
  "analytics_config": {
    "enabled": true,
    "auto_save_interval": 300,
    "export_on_exit": true,
    "track_xp": true,
    "track_combat": true,
    "track_resources": true
  }
}
```
  "screen_width": 1920,
  "screen_height": 993,
  
  "joystick_centro_x": 288,
  "joystick_centro_y": 868,
  "joystick_raio": 73,
  
  "posicoes_skills": [
    {"nome": "Skill 1", "x": 1632, "y": 744},
    {"nome": "Skill 2", "x": 1728, "y": 784},
    {"nome": "Skill 3", "x": 1536, "y": 784}
  ],
  
  "posicao_botao_camera": {"x": 50, "y": 150},
  "intervalo_reset_camera": 1,
  
  "usar_minimapa": true,
  "posicao_minimapa": {"x": 50, "y": 50, "width": 200, "height": 200},
  
  "detectar_inimigos_perigosos": true,
  "inimigos_para_fugir": ["Giant", "Boss", "Elite", "Champion"],
  "regiao_nome_inimigo": {"x": 400, "y": 100, "largura": 600, "altura": 150},
  "intervalo_verificacao_inimigo": 2,
  
  "salvar_imagens_treino": true,
  "max_imagens_treino": 100
}
```

### Personalização



## 🎯 Uso

### Execução Principal
```bash
# Farming infinito com todas as funcionalidades
python3 main.py
```

O bot iniciará automaticamente com:
- ✅ IA e ML habilitados
- ✅ Analytics tracking XP, combate e recursos
- ✅ Advanced Vision (cores, círculos, OCR)
- ✅ Auto-save de métricas
- ✅ Notificações de alerta

### Interromper com Segurança
Pressione `Ctrl+C` para parar. O bot irá:
1. Salvar analytics automaticamente
2. Exportar métricas para JSON
3. Exibir relatório completo com:
   - Estatísticas de XP (ganho, taxa, tempo para level)
   - Estatísticas de combate (kills, kills/min, XP/kill)
   - Estatísticas de IA (análises, movimentos, detecções)
   - Caminho do arquivo de métricas exportado

### Exemplo de Output ao Parar
```
📊 Estatísticas:
  🎥 Resets de câmera: 145
  🎯 Targets totais: 287
  🔄 Ciclos de target: 95
  💰 Screenshots EXP ganho: 58

📈 Analytics:
  XP ganho: 2.35%
  XP/min: 0.0154%
  Tempo para level: 3h 28min
  Kills: 45
  Kills/min: 2.10
  XP médio/kill: 0.0523%

💰 Sistema de Recompensas - Relatório Final:
  Duração: 45.2 min
  Recompensa total: +1,247.5
  Melhor ação: Multi-kill + XP alto (+25.0)

🗺️  Hotspot Finalizado: auto_farming_area
  Score: 127.45
  XP/hora: 0.0245%
  Rank: #1 🌟🌟🌟

💾 Métricas exportadas: metrics_20251214_143052.json

🧠 Estatísticas de IA:
  🔍 Análises de minimap: 89
  🚶 Movimentos inteligentes: 12
  👹 Inimigos detectados: 234
  📊 Média por scan: 2.6
  🎓 Amostras ML coletadas: 89
```

## 🎓 Ferramentas de Treinamento

### Treinamento com Recompensas
```bash
# Menu interativo
python3 treinador_recompensas.py

# Treinamento rápido
./treinar_rapido.sh
```

**Opções:**
1. 🌲 **RandomForest** com recompensas (recomendado)
2. ⚡ **GradientBoosting** com recompensas (alternativa)
3. 🧪 **Testar modelo** (predição de ações)
4. 📊 **Comparar** com modelo anterior

### Visualização de Hotspots
```bash
# Menu de hotspots
./ver_hotspots.sh

# OU direto
python3 mapeamento_hotspots.py
```

**Opções:**
1. 📊 **Relatório** - Top 10 hotspots ranqueados
2. 🎨 **Heatmap Score** - Mapa de qualidade
3. 🎨 **Heatmap XP** - Mapa de XP ganho
4. 🎨 **Heatmap Kills** - Mapa de kills
5. 🏆 **Melhor hotspot** - Detalhes do #1

### Análise de Diversidade
```bash
# Diagnóstico dos dados de treino
python3 analisar_diversidade.py
```

**Mostra:**
- % de amostras únicas
- Features com baixa variância
- Recomendação de clusters
- Plano de coleta de dados

## 📊 Analytics e Métricas

### Visualizador de Analytics

```bash
# Menu interativo completo
python3 view_analytics.py
```

**Opções disponíveis:**
1. 📊 Ver sessão atual
2. 📁 Histórico de sessões
3. 💰 Análise de XP ganho
4. 💾 Exportar métricas
5. 📈 Análise de eficiência
6. 📄 Relatório completo
7. ❌ Sair

### Sistema de Métricas ML

```bash
# Dashboard único
python3 metricas_aprendizado.py

# Monitoramento contínuo (atualiza a cada 30s)
python3 metricas_aprendizado.py monitor

# Monitoramento com intervalo customizado (60s)
python3 metricas_aprendizado.py monitor 60
```

**Dashboard de Métricas ML:**
```
🧠 DASHBOARD DE APRENDIZADO ML
================================================================================

📊 PROGRESSO DE TREINAMENTO
--------------------------------------------------------------------------------
Total de amostras: 89
Trainings realizados: 0

Próximo marco: 100 amostras
[████████████████████████████████████░░░░] 89.0% (89/100)

📈 Sessão Atual:
  Amostras coletadas: 89
  Taxa de coleta: 1.23 amostras/min

🎯 TENDÊNCIAS DE PERFORMANCE
--------------------------------------------------------------------------------
XP/min: 📈 0.0154% (+8.3%)
Kills/min: 📈 2.10 (+12.1%)
Duração combate: 📈 14.2s (-5.7%)

🔗 Impacto do ML: +10.5%
   ✅ ML está melhorando a performance!
```

### Relatório de Aprendizado Completo

```bash
python3 relatorio_aprendizado.py
```

**Menu de Relatórios:**
1. 📄 Ver relatório completo
2. 💾 Exportar métricas (JSON)
3. 🤖 Status dos modelos ML
4. 📸 Estatísticas de imagens
5. 📈 Análise de progressão
6. 🎯 Impacto do ML
0. ❌ Sair

**Exemplo de Relatório:**
```
📊 RELATÓRIO DE MÉTRICAS DE APRENDIZADO
================================================================================

🤖 MODELOS DE MACHINE LEARNING
--------------------------------------------------------------------------------
✅ Modelos treinados: 4
  • modelo_sklearn.pkl (45.2 KB)
  • modelo_ultra.pkl (38.7 KB)
  • modelo_ultra_adb.pkl (92.1 KB)
  • ml_avancado_modelo.pkl (92.1 KB)

📊 Total de amostras coletadas: 89
🕐 Último treinamento: 14/12/2025 14:30
   (há 2 horas)

📸 DADOS DE TREINAMENTO
--------------------------------------------------------------------------------
Imagens de minimap: 89
Imagens de EXP gain: 58
Espaço total: 12.45 MB
Período de coleta: 3 dias

📈 PROGRESSÃO DE APRENDIZADO
--------------------------------------------------------------------------------
Total de sessões analisadas: 5
Tempo total de farming: 2:15:33
Sessões com ML ativo: 3

XP/min: 📈 Melhorando (+8.3%)
  Média: 0.0142%/min

Kills/min: 📈 Melhorando (+12.1%)
  Média: 2.05 kills/min

💡 RECOMENDAÇÕES
--------------------------------------------------------------------------------
  ✅ Dados suficientes! Execute force_train() para criar modelos
  ✅ ML melhorando performance significativamente!
```

### Detecção de XP Ganho

```bash
# Processa screenshots de EXP ganho
python3 xp_detector.py
```

Extrai valores exatos de XP de screenshots usando OCR otimizado.

### Status do Treinamento ML

```bash
python3 ml_status.py
```

Mostra:
- Amostras coletadas
- Progresso até próximo treino
- Modelos salvos
- Opção de treino manual

### Utilitários

```bash
# Limpa screenshots corrompidos
python3 clean_corrupted.py

# Testa método de screenshot
python3 test_screenshot.py
```

## 🎮 Calibração

### 📍 Método Rápido: Visualização de Coordenadas (RECOMENDADO)

**Ative a exibição de coordenadas na tela do dispositivo:**

```bash
# Ativar visualização de coordenadas (mostra X,Y no topo da tela ao tocar)
adb -s 192.168.240.112:5555 shell settings put system pointer_location 1

# Agora toque em qualquer lugar do jogo e veja as coordenadas aparecerem!
# Anote os valores X,Y de cada botão/região

# Desativar quando terminar a calibração
adb -s 192.168.240.112:5555 shell settings put system pointer_location 0
```

**Como usar:**
1. Execute o comando para ativar
2. Toque em cada botão/região do jogo (joystick, skills, loot, etc.)
3. As coordenadas aparecem em tempo real no topo da tela
4. Anote os valores X,Y e atualize `config_farming_adb.json`
5. Desative quando terminar

### Calibrador Interativo (Alternativo)
Use o calibrador para encontrar coordenadas precisas:

```bash
python3 calibrador_interativo.py
```

O script permite testar coordenadas digitando X e Y. Clica no dispositivo e você vê o resultado instantaneamente.

### Elementos para Calibrar

1. **Joystick** (canto inferior esquerdo)
   - Centro: onde o joystick está em repouso
   - Raio: distância máxima do arrasto

2. **Skills** (canto inferior direito)
   - Posição de cada botão de skill

3. **Botão de Câmera** (próximo ao level do personagem)
   - Ícone para resetar câmera

4. **Minimapa** (canto superior esquerdo)
   - Região onde aparecem os inimigos

5. **Barra de HP** (canto superior esquerdo)
   - Pixel para detectar HP baixo

6. **Barra de XP** (parte inferior da tela)
   - Região para OCR ler percentual de XP

7. **Região de Nome do Inimigo** (centro-superior da tela)
   - Área onde aparece o nome do inimigo durante combate
   - Usado para detectar inimigos perigosos (Giant, Boss, etc.)

### Calibrando Região de Nome do Inimigo

Para melhor detecção de inimigos perigosos:

1. Entre em combate com qualquer inimigo
2. Observe onde o nome aparece (geralmente centro-superior)
3. Tire um screenshot: `adb shell screencap -p > screenshot.png`
4. Meça as coordenadas da região do nome
5. Ajuste `regiao_nome_inimigo` no config

### Testando Coordenadas Manualmente
```bash
# Teste básico
adb -s 192.168.240.112:5555 shell input tap X Y

# Teste de movimento (joystick)
adb -s 192.168.240.112:5555 shell input swipe 288 868 361 868 1500
```

## 📁 Estrutura do Projeto

```
bot_sro_mobile/
├── main.py                          # ⭐ Script principal do bot
├── ai_modules.py                    # 🧠 Módulos de IA (ML + CV)
│   ├── MinimapVision                # Análise de minimap (8 setores)
│   ├── MLPredictor                  # Machine Learning (RF + KMeans)
│   ├── CombatDetector               # Detecção de combate (ImageHash)
│   ├── OCRReader                    # OCR para XP e texto
│   └── AdvancedVision               # Detecção avançada (cores + círculos)
│
├── analytics.py                     # 📊 Sistema de analytics completo
│   └── FarmingAnalytics             # XP, combate, recursos, previsões
│
├── xp_detector.py                   # 💰 Detector de EXP ganho (OCR)
│   └── XPGainDetector               # Extração de valores de XP
│
├── metricas_aprendizado.py          # 🎓 Sistema de métricas ML
│   └── MetricasAprendizadoML        # Tracking de treinamento e tendências
│
├── relatorio_aprendizado.py         # 📄 Relatórios de aprendizado
│   └── RelatorioAprendizado         # Análise completa de ML e progresso
│
├── view_analytics.py                # 📈 Visualizador de analytics
│   └── Menu interativo              # 7 opções de visualização
│
├── sistema_recompensas.py           # 💰 Sistema de Recompensas (RL)
│   └── SistemaRecompensas           # Avaliação de ações (reward/penalty)
│
├── treinador_recompensas.py         # 🎓 ML com Sample Weighting
│   └── TreinadorComRecompensas      # RandomForest + rewards
│
├── mapeamento_hotspots.py           # 🗺️ Mapeamento de Áreas
│   └── MapeadorHotspots             # Grid 10x10, scores, heatmaps
│
├── detector_corrigido.py            # 🔍 Detecção Visual Otimizada
│   └── DetectorVisualCorrigido      # Minimap-only, HSV ajustado
│
├── analisar_diversidade.py          # 📊 Análise de Dados
│   └── Diagnóstico de qualidade     # Unicidade, variância, clusters
│
├── limpar_imagens.py                # 🧹 Gerenciador de Imagens
│   └── Limpeza interativa           # Mantém N mais recentes
│
├── ml_status.py                     # 🔍 Status do ML
├── test_screenshot.py               # 🧪 Testa métodos de screenshot
├── clean_corrupted.py               # 🧹 Remove PNGs corrompidos
│
├── treinar_rapido.sh                # ⚡ Script de treino rápido
├── ver_hotspots.sh                  # 🗺️ Visualizador de hotspots
│
├── config_farming_adb.json          # ⚙️ Configuração principal
├── requirements.txt                 # 📦 Dependências Python
│
├── ml_models/                       # 🤖 Modelos e Dados
│   ├── modelo_sklearn.pkl           # RandomForest base
│   ├── modelo_com_recompensas.pkl   # RF com rewards
│   ├── training_data.json           # 4,500+ amostras
│   ├── rewards_history.json         # Histórico de recompensas
│   └── hotspots_map.json            # Mapa de hotspots
│
├── analytics_data/                  # 📊 Dados de analytics
│   ├── session_*.json               # Sessões de farming
│   └── heatmaps/                    # Mapas visuais de hotspots
│       ├── heatmap_score_*.png
│       ├── heatmap_xp_*.png
│       └── heatmap_kills_*.png
│
├── treino_ml/                       # 📸 Screenshots de treino (max: 10)
├── exp_ganho_treino/                # 💰 XP ganho (max: 10)
├── minimap_captures/                # 🗺️ Capturas minimap (max: 10)
├── debug_deteccao/                  # 🔍 Debug detector (max: 10)
│
└── README.md                        # 📖 Esta documentação
```

### Arquivos Principais

#### `main.py` (1635+ linhas)
**Bot completo com:**
- `Config`: Gerenciamento de configurações JSON
- `screenshot()`: Captura de tela via ADB (shell + pull)
- `start_infinite_farming()`: Loop principal de farming
- Integração: IA + ML + Analytics + Recompensas + Hotspots
- Signal handler com relatório final completo

#### `ai_modules.py` (1072+ linhas)
**Cinco módulos de IA:**
1. **MinimapVision**: Análise OpenCV do minimap
   - 8 setores direcionais
   - Contagem de inimigos por cor
   - Heatmap de densidade
   
2. **MLPredictor**: Machine Learning
   - RandomForest para predição de densidade
   - KMeans para clustering (2 clusters otimizado)
   - Auto-treino a cada 100 amostras
   - 4 formatos de modelo salvos
   - Integração com MetricasAprendizadoML
   
3. **CombatDetector**: Detecção de estado
   - ImageHash para identificar combate
   - Histórico de estados
   - Estatísticas de tempo em combate
   
4. **OCRReader**: Leitura de texto
   - Extração de XP da barra
   - Detecção de inimigos perigosos
   - Leitura de coordenadas
   
5. **AdvancedVision**: Computer Vision avançado
   - `detect_colors()`: cv2.inRange para 8 cores
   - `detect_circles()`: cv2.HoughCircles
   - `read_coordinates_ocr()`: OCR de posição
   - `get_movement_vector()`: Cálculo de direção

#### `analytics.py` (600+ linhas)
**FarmingAnalytics - Sistema completo:**
- `update_xp()`: Atualiza XP via OCR
- `add_xp_gain()`: Registra XP de combate
- `register_combat()`: Tracking de batalhas
- `get_xp_per_minute()`: Calcula taxa
- `predict_time_to_level()`: Estimativa para 100%
- `export_metrics()`: Salva JSON
- `generate_report()`: Relatório formatado

#### `metricas_aprendizado.py` (550+ linhas)
**MetricasAprendizadoML - Tracking de ML:**
- `register_sample_collected()`: Registra coleta
- `register_training_completed()`: Registra treino
- `register_performance_data()`: Tracking de performance
- `get_training_progress()`: Progresso atual
- `get_performance_trends()`: Análise de tendências
- `print_live_dashboard()`: Dashboard ao vivo
- `generate_summary_report()`: Relatório resumido

#### `xp_detector.py` (250+ linhas)
**XPGainDetector - OCR de EXP:**
- Preprocessamento: CLAHE, threshold, resize
- 4 regex patterns para parsing
- Batch processing de screenshots
- Estatísticas de valores detectados

#### `sistema_recompensas.py` (400+ linhas)
**SistemaRecompensas - Reinforcement Learning:**
- 15+ tipos de recompensas (kills, XP, combate, etc.)
- Penalidades (mortes, HP baixo, stuck)
- Histórico completo (1000 últimas ações)
- Relatório final com melhores/piores ações
- Salva em `ml_models/rewards_history.json`

#### `treinador_recompensas.py` (450+ linhas)
**TreinadorComRecompensas - ML com Feedback:**
- RandomForest com sample_weight baseado em rewards
- GradientBoosting como alternativa
- Comparação com modelo anterior
- Feature importance analysis
- Menu interativo com 4 opções

#### `mapeamento_hotspots.py` (550+ linhas)
**MapeadorHotspots - Spatial Analysis:**
- Grid 10x10 para 1000x1000 coordenadas
- Rastreamento: XP/hora, Kills/min, Mortes, Mobs
- Cálculo de score de qualidade
- Ranking automático de regiões
- Geração de heatmaps com matplotlib
- Salva em `ml_models/hotspots_map.json`

#### `detector_corrigido.py` (293 linhas)
**DetectorVisualCorrigido - CV Otimizado:**
- Crop minimap: região (150,150) → 200x200
- HSV ajustado: S≥200, V≥200 (cores vibrantes)
- Blob detection: min=20, max=500, circularity≥0.5
- Auto-cleanup: mantém 10 imagens debug
- 3 cores: Vermelho (inimigos), Azul (aliados), Amarelo (itens)

#### `analisar_diversidade.py` (235 linhas)
**Diagnóstico de Dados:**
- Calcula % de amostras únicas
- Identifica features de baixa variância
- Análise de distâncias entre amostras
- Recomendação de clusters otimizada
- Plano de coleta de dados diversificados

## 🔧 Troubleshooting

### Screenshot Corrupto (arquivo "data" em vez de PNG)

**Problema:** Screenshots salvos como "data" sem extensão ou corrompidos.

**Causa:** Método `exec-out screencap -p` falha em alguns dispositivos.

**Solução:** O bot já usa método corrigido (shell + pull):
```python
# Método automático no main.py
adb shell screencap -p /sdcard/temp_screenshot.png
adb pull /sdcard/temp_screenshot.png ./local.png
adb shell rm /sdcard/temp_screenshot.png
```

**Limpeza de arquivos corrompidos:**
```bash
python3 clean_corrupted.py
```

### Modelos ML não estão sendo salvos

**Problema:** Pasta `ml_models/` vazia após coleta de amostras.

**Solução:**
```bash
# Verifique quantas amostras foram coletadas
python3 ml_status.py

# Se tiver 100+ amostras, force o treino
python3 -c "from ai_modules import MLPredictor; ml = MLPredictor(); ml.force_train()"

# Ou continue o bot - treina automaticamente a cada 100 amostras
```

### Analytics não registra XP

**Problema:** XP/min sempre 0.000% no relatório.

**Causas e Soluções:**
1. **OCR não detecta XP:**
   - Ajuste `posicao_xp_bar` no config
   - Verifique se tesseract está instalado: `tesseract --version`
   
2. **Região incorreta:**
   ```bash
   # Tire screenshot e verifique região
   adb shell screencap -p > test.png
   # Ajuste coord_region no config
   ```

3. **Padrão não reconhecido:**
   - Analytics espera formato "XX.XX%"
   - Verifique regex patterns em `analytics.py`

### XP Gain Detector retorna None

**Problema:** `xp_detector.detect_xp_from_image()` retorna sempre None.

**Solução:**
```bash
# Teste manualmente
python3 xp_detector.py

# Verifique screenshots em exp_ganho_treino/
ls -lh exp_ganho_treino/

# Se estiverem corrompidos, limpe e recapture
python3 clean_corrupted.py
```

### IA não move o personagem

**Problema:** Bot detecta inimigos mas não usa movimento inteligente.

**Causas e Soluções:**
1. **IA desabilitada:**
   ```json
   // config_farming_adb.json
   "ia_config": {
     "usar_ia": true,
     "usar_ml": true
   }
   ```

2. **Dados insuficientes:**
   - ML precisa de 10+ amostras para funcionar
   - Continue farming para coletar dados

3. **Threshold muito alto:**
   - Ajuste `movement_threshold` no código

### Advanced Vision não detecta

**Problema:** Cores, círculos ou coordenadas não são detectados.

**Soluções:**
```json
// config_farming_adb.json
"advanced_vision_config": {
  "detect_colors_enabled": true,
  "detect_circles_enabled": true,
  "read_coords_enabled": true
}
```

### KMeans Convergência Warning

**Problema:** `ConvergenceWarning: Number of distinct clusters (1) found smaller than n_clusters (3)`

**Solução:** Já corrigido! Reduzido de 3 → 2 clusters em `ai_modules.py`:
```python
# Otimizado para 51.8% dados únicos
self.cluster_model = KMeans(n_clusters=2, random_state=42, n_init=10)
```

**Se quiser ajustar manualmente:**
```bash
# Analise diversidade primeiro
python3 analisar_diversidade.py

# Use recomendação de clusters sugerida
```

### Detector contando objetos errados

**Problema:** "77 objetos vermelhos" quando há apenas 8 visíveis.

**Causa:** Detector analisando tela inteira em vez de apenas minimap.

**Solução:** Use `detector_corrigido.py` (já integrado):
```python
# Analisa APENAS minimap (150,150 → 200x200)
detector = DetectorVisualCorrigido()
resultado = detector.detectar_objetos_reais(screenshot, crop_minimap=True)
```

**Soluções:**

**Para cores:**
```json
// Ajuste ranges HSV no config
"color_ranges": {
  "vermelho": {
    "lower": [0, 100, 100],
    "upper": [10, 255, 255]
  }
}
```

**Para círculos:**
```json
// Ajuste parâmetros HoughCircles
"circle_detection": {
  "dp": 1.2,
  "minDist": 20,
  "param1": 50,
  "param2": 30,
  "minRadius": 5,
  "maxRadius": 50
}
```

**Para coordenadas:**
```json
// Ajuste região de leitura
"coord_region": {
  "x": 10,
  "y": 10,
  "width": 200,
  "height": 30
}
```

### Métricas ML não aparecem

**Problema:** Dashboard vazio ou sem dados.

**Solução:**
```bash
# Verifique se arquivo existe
ls -lh ml_models/training_metrics.json

# Se não existir, inicie bot para gerar
python3 main.py

# Após coletar algumas amostras, veja métricas
python3 metricas_aprendizado.py
```

### Notificações não aparecem (Linux)

**Problema:** Alertas não mostram no sistema.

**Solução:**
```bash
# Instale libnotify
sudo apt-get install libnotify-bin

# Teste manualmente
notify-send "Teste" "Mensagem de teste"

# Se não funcionar, verifique gerenciador de notificações
# Para GNOME: Settings > Notifications
# Para KDE: System Settings > Notifications
```

### Bot não se move

**Problema:** Personagem parado mesmo com bot rodando.

**Soluções:**
1. **Calibre joystick:**
   ```bash
   # Ative visualização de coordenadas
   adb shell settings put system pointer_location 1
   
   # Toque no joystick e anote centro
   # Atualize config_farming_adb.json
   
   # Desative
   adb shell settings put system pointer_location 0
   ```

2. **Teste movimento manual:**
   ```bash
   # Teste swipe do joystick
   adb shell input swipe 288 868 361 868 1500
   ```

### Skills não funcionam

**Problema:** Habilidades não são usadas.

**Solução:**
```bash
# Ative pointer_location
adb shell settings put system pointer_location 1

# Toque em cada botão de skill
# Anote coordenadas X,Y

# Atualize config
"posicoes_skills": [
  {"nome": "Skill 1", "x": 1632, "y": 744},
  {"nome": "Skill 2", "x": 1728, "y": 784}
]

# Teste
adb shell input tap 1632 744
```

### Dispositivo não conecta via ADB

**Problema:** `adb devices` mostra vazio ou "offline".

**Solução:**
```bash
# Reinicie servidor ADB
adb kill-server
adb start-server

# Reconecte
adb connect 192.168.240.112:5555

# Verifique
adb devices

# Se continuar offline:
# 1. Verifique IP do dispositivo
# 2. Teste ping: ping 192.168.240.112
# 3. Reative ADB no dispositivo
# 4. Para Waydroid: waydroid session stop && waydroid session start
```

### Erros de importação

**Problema:** `ModuleNotFoundError` ao executar scripts.

**Solução:**
```bash
# Reinstale dependências
pip3 install -r requirements.txt

# Ou instale individualmente
pip3 install numpy pillow scikit-learn opencv-python imagehash pytesseract

# Verifique instalação
python3 -c "import cv2, sklearn, PIL, imagehash; print('OK')"
```

### Performance ruim / Bot lento

**Soluções:**

1. **Reduza intervalo de análise IA:**
   ```json
   "ia_config": {
     "intervalo_analise_ia": 10  // Aumentar de 5 para 10
   }
   ```

2. **Desabilite features não essenciais:**
   ```json
   "advanced_vision": {
     "detect_colors_enabled": false,  // Desabilitar se não usar
     "detect_circles_enabled": false
   }
   ```

3. **Reduza frequência de screenshots:**
   - Bot captura a cada ciclo, considere pular alguns

### Análise de Logs

O bot imprime informações úteis durante execução:

```
🧠 ML: 10 amostras coletadas
🧠 ML: 20 amostras coletadas
...
🤖 Treinando modelos com 100 amostras...
✅ Modelos ML treinados com 100 amostras!
   ⏱️ Tempo de treino: 2.45s
```

**Problemas comuns nos logs:**

- `⚠️ Dados insuficientes para treino (5/10 mínimo)` → Continue coletando
- `✗ Erro ao treinar modelos: ...` → Verifique dependências scikit-learn
- `⚠️ Nenhum modelo encontrado` → Normal no início, treine com 100+ amostras
- `📉 XP/min caindo` → Verifique área de farming ou configurações

## 📊 Estatísticas e Relatórios

### Durante Execução (Display Ao Vivo)

O bot exibe informações em tempo real durante o farming:

```
🔄 [Ciclo 45] Farming...
  ⚔️  Combate: ativa | 🎯 Target: mob_01 | 📍 Pos: (1250,450)
  💚 HP: OK | 💙 MP: OK | ⚡ Vigor: 85%
  📈 XP: 67.85% (+2.35%) | 📈0.0154/min
  👹 Inimigos detectados: N:3 E:2 S:1 W:0
  🧠 ML: 89 amostras | Density: 2.3 | Cluster: 1
```

### Ao Parar (Ctrl+C)

Relatório completo com todas as estatísticas:

```
⏹️  FARMING INTERROMPIDO
================================================================================

📊 Estatísticas:
  🎥 Resets de câmera: 145
  🎯 Targets totais: 287
  🔄 Ciclos de target: 95
  😈 Demon ativado: 12 vezes
  📸 Screenshots EXP barra: 95
  💰 Screenshots EXP ganho: 58

📈 Analytics:
  XP ganho: 2.35%
  XP/min: 0.0154%
  Tempo para level: 3h 28min
  Kills: 45
  Kills/min: 2.10
  XP médio/kill: 0.0523%

💾 Métricas exportadas: metrics_20251214_143052.json

🧠 Estatísticas de IA:
  🔍 Análises de minimap: 89
  🚶 Movimentos inteligentes: 12
  👹 Inimigos detectados: 234
  📊 Média por scan: 2.6
  ⚔️  Combate detectado: 78.5% do tempo
  🎓 Amostras ML coletadas: 89
```

### Arquivo JSON Exportado

Estrutura completa de `metrics_*.json`:

```json
{
  "session_info": {
    "session_id": "session_20251214_140000",
    "start_time": "2025-12-14T14:00:00",
    "end_time": "2025-12-14T15:30:00",
    "duration": "1:30:00"
  },
  
  "statistics": {
    "xp": {
      "initial": 65.50,
      "current": 67.85,
      "gained": 2.35,
      "xp_per_minute": 0.0154,
      "time_to_level": "3:28:00",
      "avg_xp_per_kill": 0.0523
    },
    
    "combat": {
      "kills": 45,
      "deaths": 1,
      "kills_per_minute": 2.10,
      "avg_combat_duration": 14.2,
      "total_combats": 46
    },
    
    "resources": {
      "potions_used": {
        "hp": 5,
        "mp": 2,
        "vigor": 0
      },
      "skills_used": {
        "Skill 1": 45,
        "Skill 2": 45,
        "Skill 3": 45
      }
    }
  },
  
  "detailed_data": {
    "xp_history": [
      ["2025-12-14T14:00:00", 65.50],
      ["2025-12-14T14:05:00", 65.75],
      ...
    ],
    
    "xp_gains": [
      ["2025-12-14T14:02:30", 1250, "combat"],
      ["2025-12-14T14:05:15", 1180, "combat"],
      ...
    ],
    
    "combat_history": [
      ["2025-12-14T14:02:00", 12.5, true],
      ["2025-12-14T14:03:30", 14.2, true],
      ...
    ],
    
    "loot_collected": [
      ["2025-12-14T14:02:35", "Item Name", 1],
      ...
    ],
    
    "ai_detections": [
      ["2025-12-14T14:00:30", {"N": 3, "E": 2, "S": 1, "W": 0}],
      ...
    ]
  }
}
```

## 🎓 Guia de Uso Avançado

### Otimizando o Treinamento ML

**1. Coleta Eficiente de Amostras:**
```bash
# Rode em área com muitos inimigos
# IA coleta 1 amostra a cada 5s
# Meta: 100 amostras = ~8-10 minutos
```

**2. Forçar Treinamento Manual:**
```python
from ai_modules import MLPredictor

ml = MLPredictor()
print(f"Amostras: {len(ml.training_data)}")

if len(ml.training_data) >= 10:
    ml.force_train()
    print("✅ Modelos treinados!")
```

**3. Verificar Qualidade dos Modelos:**
```bash
# Veja relatório completo
python3 relatorio_aprendizado.py

# Menu → Opção 3: Status dos modelos ML
# Verifica: número de amostras, data do treino, tamanho dos arquivos
```

**4. Limpar e Reiniciar Treinamento:**
```bash
# Backup atual
mv ml_models ml_models_backup

# Novo treinamento
python3 main.py
# IA começará a coletar amostras do zero
```

### Analisando Eficiência de Farming

**1. Compare Sessões:**
```bash
python3 view_analytics.py
# Opção 2: Histórico de sessões
# Compare XP/min e kills/min entre sessões
```

**2. Identifique Melhor Área:**
```python
# Analytics salva posições e densidade
# Revise detailed_data.ai_detections no JSON
# Procure setores com mais detecções consistentes
```

**3. Calcule ROI de Potions:**
```python
# XP ganho / potions usadas
# Se ratio for baixo, ajuste threshold de HP
```

### Customizando Detecções

**1. Adicionar Nova Cor ao Advanced Vision:**
```json
"color_ranges": {
  "ciano": {
    "lower": [80, 100, 100],
    "upper": [100, 255, 255]
  }
},
"target_colors": ["vermelho", "azul", "ciano"]
```

**2. Ajustar Sensibilidade de Círculos:**
```json
// Menos círculos (mais rigoroso)
"param2": 40  // era 30

// Mais círculos (mais sensível)
"param2": 20
```

**3. OCR para Outros Elementos:**
```python
# Em ai_modules.py → OCRReader
def read_custom_element(self, img_path, region):
    img = cv2.imread(img_path)
    roi = img[region['y']:region['y']+region['height'],
              region['x']:region['x']+region['width']]
    
    text = pytesseract.image_to_string(roi)
    return text.strip()
```

### Automatizando Análises

**1. Script de Relatório Diário:**
```bash
#!/bin/bash
# daily_report.sh

python3 view_analytics.py << EOF
4
metricas_diarias_$(date +%Y%m%d).json
0
EOF

python3 relatorio_aprendizado.py << EOF
2
relatorio_ml_$(date +%Y%m%d).json
0
EOF
```

**2. Monitoramento Contínuo:**
```bash
# Terminal 1: Bot rodando
python3 main.py

# Terminal 2: Monitor de métricas ML (atualiza a cada 30s)
python3 metricas_aprendizado.py monitor 30
```

**3. Cronjob para Análise Noturna:**
```bash
crontab -e

# Adicione:
0 2 * * * cd /path/to/bot_sro_mobile && ./daily_report.sh
```

### Visualizando Hotspots

**1. Após Farm:**
```bash
./ver_hotspots.sh

# Ver top hotspots
# Opção 1: Relatório completo

# Gerar heatmaps
# Opção 2-4: Diferentes métricas
```

**2. Identificar Melhor Região:**
```bash
python3 mapeamento_hotspots.py

# Opção 5: Ver melhor hotspot
# Mostra região #1 com maior score
```

**3. Comparar Áreas:**
```python
# Analise heatmap_score_*.png
# Células com cores mais quentes = melhores áreas
# Círculos dourado/prata/bronze = top 3
```

## 🚀 Roadmap e Melhorias Futuras

### ✅ Implementado (Dezembro 2025)
- ✅ Sistema de Recompensas (Reinforcement Learning)
- ✅ Treinamento com Sample Weighting (Rewards)
- ✅ Mapeamento de Hotspots (Grid 10x10 + Heatmaps)
- ✅ Detector Visual Corrigido (Minimap-only)
- ✅ Análise de Diversidade de Dados
- ✅ Auto-cleanup de imagens (10 max)
- ✅ KMeans otimizado (2 clusters)

### 🔄 Em Desenvolvimento
- [ ] Interface gráfica (GUI) com PyQt5
- [ ] Detector de HP (OCR da barra de vida)
- [ ] Detector de Morte (tela preta/respawn)
- [ ] Auto-movimento para hotspots
- [ ] Telegram/Discord notifications
- [ ] Multi-account support

### 🎯 Melhorias de IA Planejadas
- [ ] Deep Learning com TensorFlow
- [ ] Q-Learning para decisões ótimas
- [ ] Reconhecimento de padrões de spawn
- [ ] Previsão de horários com mais inimigos
- [ ] Auto-ajuste de configurações baseado em performance
- [ ] Detector de items raros (OCR + CV)

### 📊 Analytics Futuro
- [ ] Gráficos interativos com plotly
- [ ] Comparação com outros players
- [ ] Benchmarks de eficiência
- [ ] Alertas de anomalias
- [ ] Exportação para Google Sheets
- [ ] Dashboard web em tempo real

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -am 'Adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

### Áreas que Precisam de Ajuda
- 🐛 Testes em diferentes dispositivos Android
- 📱 Suporte para outras resoluções de tela
- 🌍 Tradução da documentação
- 🎨 Melhoria de UX/UI
- 📊 Novos tipos de análises

## ⚠️ Aviso Legal

Este projeto é **apenas para fins educacionais** e demonstração de técnicas de automação, Machine Learning e Computer Vision.

**IMPORTANTE:**
- O uso de bots pode violar os **Termos de Serviço** do jogo
- Pode resultar em **banimento permanente** da conta
- Use por **sua conta e risco**
- Os desenvolvedores **não se responsabilizam** por qualquer consequência

**Recomendação:** Use apenas em contas de teste ou ambientes controlados.

## 📝 Licença

MIT License - Copyright (c) 2025

Permissão concedida para uso, cópia, modificação e distribuição deste software.

## 📞 Suporte e Contato

- 🐛 **Issues:** [GitHub Issues](https://github.com/joaodematejr/bot_sro_mobile/issues)
- 💬 **Discussões:** [GitHub Discussions](https://github.com/joaodematejr/bot_sro_mobile/discussions)
- 📧 **Email:** joaodematejr@example.com

## 🙏 Agradecimentos

- **OpenCV** - Computer Vision
- **Scikit-learn** - Machine Learning
- **Tesseract** - OCR Engine
- **Matplotlib** - Data Visualization
- **NumPy** - Numerical Computing
- **Python Community** - Ferramentas incríveis

---

## 📊 Estatísticas do Projeto

- 📝 **Linhas de Código**: 10,000+
- 🧠 **Módulos de IA**: 8 sistemas diferentes
- 🎓 **Amostras Treináveis**: 4,500+ coletadas
- 🗺️ **Células de Mapeamento**: 100 (grid 10x10)
- 💰 **Tipos de Recompensas**: 15+ configuradas
- 📊 **Métricas Rastreadas**: 30+ diferentes
- 🔧 **Ferramentas**: 15+ scripts auxiliares

---

**Desenvolvido com ❤️ e ☕ para automação Android avançada via ADB**

🌟 **Se este projeto te ajudou, deixe uma estrela!** 🌟
