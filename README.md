# 🎮 Bot Ultra ADB - Silkroad Origin Mobile

Bot automatizado para farming em Silkroad Origin Mobile usando controle ADB (Android Debug Bridge). Sistema completo com inteligência artificial, detecção de inimigos via minimapa, tracking de XP e múltiplas funcionalidades automáticas.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Calibração](#-calibração)
- [Estrutura do Projeto](#-estrutura-do-projeto)

## ⚡ Funcionalidades

### 🤖 Automação Principal
- **Auto-Skills**: Usa skills automaticamente em rotação
- **Auto-Loot**: Coleta loot automaticamente após combates
- **Auto-Potion**: Usa potion quando HP está baixo
- **Reset Câmera**: Ajusta câmera automaticamente para trás do personagem
- **Anti-AFK**: Movimentos aleatórios para evitar desconexão
- **Rotação de Áreas**: Troca de área de farming automaticamente

### 🛡️ Sistema de Proteção Inteligente
- **Detecção de Inimigos Perigosos**: Identifica inimigos como "Giant", "Boss", "Elite" e "Champion" via OCR
- **Fuga Automática**: Bot foge automaticamente ao detectar inimigos perigosos
- **Notificações do Sistema**: Alertas visuais e sonoros quando detecta ameaças
- **Gerenciamento de Imagens**: Mantém apenas as 100 imagens mais recentes de treinamento
- **Análise de Dificuldade**: Monitora perda de vida e evita áreas muito fortes

### 🧠 Inteligência Artificial

#### Machine Learning (Scikit-learn)
- **RandomForestRegressor**: Prevê densidade de inimigos baseado em posição e hora
- **KMeans Clustering**: Identifica áreas de alta concentração de combates
- **StandardScaler**: Normalização de features para melhor performance
- **Aprendizado Contínuo**: Modelo treinado automaticamente durante farming

#### Computer Vision (OpenCV)
- **Análise de Minimapa**: Detecta inimigos via `cv2.inRange()` em pixels vermelhos
- **Divisão em 8 Setores**: Divide minimapa em direções (N/NE/E/SE/S/SW/W/NW)
- **Contagem de Densidade**: Calcula número de inimigos por setor
- **Movimento Inteligente**: Move automaticamente para direção com mais inimigos
- **Detecção de Combate**: Compara frames com `imagehash` para identificar ação
- **OCR com Tesseract**: Lê XP% e outros textos via `pytesseract`
- **Detecção de Nomes**: OCR para identificar nomes de inimigos perigosos na tela
- **Preprocessamento de Imagem**: Threshold, resize e filtros para melhorar precisão do OCR

#### Algoritmo de Decisão
1. **Prioridade 0 - Segurança**: Verifica inimigos perigosos e foge se necessário
2. **Prioridade 1 - Minimapa**: Se detectar inimigos, move para setor com maior densidade
3. **Prioridade 2 - ML**: Usa RandomForest para prever melhor direção baseado em histórico
4. **Prioridade 3 - Exploração**: Algoritmo inteligente que retorna a áreas produtivas

### 📊 Analytics
- **Tracking de XP**: Lê XP atual via OCR
- **Detector de EXP Ganho**: Detecta quantidade exata de EXP após cada combate
- **Previsão de Level**: Calcula tempo estimado para atingir 100% de XP
- **Estatísticas**: Combates, mortes, potions, skills, loots, XP/min
- **Histórico**: Salva dados de farming para análise
- **Exportação de Métricas**: Gera arquivo JSON com estatísticas detalhadas

### 🔔 Sistema de Notificações
- **Alertas de Perigo**: Notificação do sistema quando detecta inimigos perigosos
- **Urgência Crítica**: Notificações com alta prioridade e som
- **Informações Detalhadas**: Nome do inimigo e status da fuga
- **Notificações Não Bloqueantes**: Bot continua funcionando mesmo se notificação falhar

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

### Sistema
```bash
android-tools-adb
tesseract-ocr
tesseract-ocr-por
libnotify-bin  # Para notificações do sistema
```

## 🚀 Instalação

### 1. Clone o repositório
```bash
cd ~/Área\ de\ Trabalho
git clone <repo-url> Python
cd Python
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

O bot gera automaticamente um arquivo de configuração com valores padrão. Principais parâmetros:

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

- **Velocidade**: `velocidade_movimento` (ms)
- **Intervalo Skills**: `intervalo_skills` (ms)
- **Threshold HP**: `threshold_hp` (0.0-1.0)
- **Reset Câmera**: `intervalo_reset_camera` (segundos)

## 🎯 Uso

### Menu Principal
```bash
python3 bot_ultra_adb.py
```

Opções:
1. **Iniciar farming (infinito)** - Roda continuamente
2. **Treinar por N ciclos** - Roda número específico de ciclos
3. **Calibrar joystick/skills** - Instruções de calibração
4. **Ver estatísticas** - Mostra stats do último farming
5. **Sair**

### Execução Rápida
```bash
# Farming infinito
python3 bot_ultra_adb.py
# Escolha opção 1

# Farming com 50 ciclos
python3 bot_ultra_adb.py
# Escolha opção 2, digite 50
```

### Interromper
Pressione `Ctrl+C` para parar o bot com segurança. As estatísticas serão salvas automaticamente.

## 🎮 Calibração

### Calibrador Interativo
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
Python/
├── bot_ultra_adb.py              # Bot principal
├── detector_exp.py               # Detector de EXP ganho via OCR
├── ml_avancado.py                # Sistema ML avançado
├── metricas_aprendizado.py       # Análise de métricas ML
├── visualizador_metricas.py      # Visualizador de estatísticas
├── visualizador_3d_ml.py         # Visualizador 3D de densidade
├── dashboard_ml.py               # Dashboard completo ML
├── calibrador_interativo.py      # Ferramenta de calibração
├── config_farming_adb.json       # Configuração (gerado automaticamente)
├── modelo_ultra_adb.pkl          # Modelo ML treinado (gerado)
├── farming_data.json             # Dados históricos (gerado)
├── metricas_bot.json             # Métricas exportadas (gerado)
├── ml_avancado_dados.json        # Dados ML avançado (gerado)
├── treino_ml/                    # Pasta com imagens de treino
├── requirements.txt              # Dependências Python
└── README.md                     # Esta documentação
```

### Arquivos Principais

#### `bot_ultra_adb.py`
Bot completo com três classes principais:

- **ConfiguracaoADB**: Gerencia configurações e auto-detecção de resolução
- **ADBController**: Controla input via ADB (tap, swipe, screenshot)
- **BotUltraADB**: Lógica principal do bot (farming, ML, detecção)

#### `calibrador_interativo.py`
Ferramenta interativa para descobrir coordenadas da tela. Digite X e Y, o script clica no dispositivo.

#### `config_farming_adb.json`
Arquivo JSON com todas as configurações. Editável manualmente ou via script.

## 🔧 Troubleshooting

### Bot não se move
1. Verifique coordenadas do joystick no config
2. Teste movimento manual: `adb shell input swipe 288 868 361 868 1500`
3. Use `calibrador_interativo.py` para encontrar posição correta

### Skills não funcionam
1. Calibre posições das skills
2. Teste: `adb shell input tap X Y` na posição de cada skill
3. Ajuste `posicoes_skills` no config

### XP não é lido
1. Verifique se `tesseract-ocr` está instalado
2. Ajuste região `posicao_xp_bar` no config
3. Desative temporariamente: `"usar_ocr_xp": false`

### Minimapa não detecta inimigos
1. Calibre `posicao_minimapa`
2. Ajuste `cor_inimigo_minimapa` (padrão vermelho: [255, 0, 0])
3. Aumente tolerância de cor (editando código se necessário)

### Inimigos perigosos não são detectados
1. Calibre `regiao_nome_inimigo` para capturar onde o nome aparece
2. Adicione mais nomes à lista `inimigos_para_fugir` no config
3. Verifique se `tesseract-ocr` está instalado corretamente
4. Teste OCR manualmente com screenshot da região

### Notificações não aparecem
1. Instale `libnotify-bin`: `sudo apt-get install libnotify-bin`
2. Teste manualmente: `notify-send "Teste" "Mensagem de teste"`
3. Verifique configurações de notificação do sistema

### Dispositivo não conecta
```bash
# Reinicie ADB
adb kill-server
adb start-server

# Reconecte
adb connect 192.168.240.112:5555

# Verifique
adb devices
```

## 📊 Estatísticas

O bot mostra estatísticas a cada 10 ciclos:

```
📊 ESTATÍSTICAS (15.3 min):
  ⚔️  Combates: 45
  💀 Mortes: 0
  🧪 Potions: 3
  💥 Skills: 135
  💰 Loots: 42
  🗺️  Áreas: 2

  📊 XP ATUAL: 67.85%
  📈 Ganho: +2.35% (desde início)
  ⚡ Taxa: 0.154% XP/min
  🎯 Para 100%: 3h 28min
  🕒 Previsão: 18:45
  
  💰 EXP Ganho: +125,450
  📊 Total: 2,345,670
```

### Notificações de Alerta

Quando inimigos perigosos são detectados:

```
🚨 ALERTA: Giant DETECTADO!
Inimigo perigoso 'Giant' está próximo! Fugindo agora...
```

A notificação aparece no sistema com:
- ⚠️ Ícone de alerta
- 🔊 Som de notificação (se habilitado)
- ⏱️ Duração de 10 segundos
- 🔴 Urgência crítica

## 🤝 Contribuindo

Sugestões e melhorias são bem-vindas! Abra issues ou pull requests.

## ⚠️ Aviso Legal

Este bot é para fins educacionais. Use por sua conta e risco. O uso de bots pode violar os termos de serviço do jogo.

## 📝 Licença

MIT License - Use livremente!

---

**Desenvolvido com ❤️ para automação Android via ADB**
