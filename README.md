# 🎮 Bot SRO Mobile - Sistema de Automação via ADB

Bot automatizado simples para Silkroad Origin Mobile usando controle ADB (Android Debug Bridge). Sistema focado em cliques automáticos configuráveis com suporte a movimentação via joystick virtual.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Troubleshooting](#-troubleshooting)

## ⚡ Funcionalidades

### 🤖 Automação Principal

- ✅ **Cliques Automáticos** - Sequência configurável de cliques com intervalos individuais
- ✅ **Reset de Câmera em Paralelo** - Thread dedicada para manter visão ideal
- ✅ **Sistema de Lure** - Cliques automáticos paralelos para atrair inimigos
- 🕹️ **Movimentação via Joystick** - Controle de movimento usando joystick virtual
- 🎯 **Lure com Joystick** - Sequência de movimentos em quadrado (frente → esquerda → trás → direita)
- 📍 **Pointer Location** - Ativar/desativar exibição de coordenadas na tela

### 🔧 Funcionalidades Técnicas

- 🔌 **Conexão ADB** - Conecta automaticamente ao dispositivo Android via WiFi
- 📱 **Comandos ADB** - Execução de comandos `adb shell input tap` e `input swipe`
- 🧵 **Threading** - Threads paralelas para camera reset e lure
- ⚙️ **Configuração JSON** - Todos os parâmetros em arquivo externo editável
- 🎮 **Controle de Joystick** - Sistema completo para movimentação direcional

### 🕹️ Sistema de Joystick

O bot suporta dois modos de movimentação via joystick:

#### Modo Contínuo
- Movimento sustentado em uma direção por duração configurável (padrão: 4000ms)
- Ideal para deslocamentos longos

#### Modo com Passos
- Movimento intervalado com pausas entre passos
- Parâmetros configuráveis:
  - `step_duration`: Duração de cada passo (padrão: 500ms)
  - `step_interval`: Pausa entre passos (padrão: 0.3s)
  - `steps_per_direction`: Quantidade de passos por direção (padrão: 4)
- Cria efeito de caminhada mais natural
- Usado na sequência de Lure automática

## 📋 Requisitos

### Sistema Operacional
- ✅ Linux (testado em Ubuntu/Debian)
- ✅ Windows (com WSL ou ADB nativo)
- ✅ macOS

### Software
- 🔧 **ADB (Android Debug Bridge)** - Ferramenta de linha de comando para Android
- 🐍 **Python 3.7+** - Linguagem de programação

### Hardware
- 📱 **Dispositivo Android** - Com depuração USB ativada
- 🌐 **Conexão de Rede** - WiFi para conexão ADB wireless

## 🔧 Instalação

### 1. Instalar ADB

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install adb
```

#### macOS
```bash
brew install android-platform-tools
```

#### Windows
Baixe o [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools) e adicione ao PATH.

### 2. Clonar o Repositório
```bash
git clone https://github.com/joaodematejr/bot_sro_mobile.git
cd bot_sro_mobile
```

### 3. Preparar Ambiente (Opcional)
```bash
# Criar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows
```

## 🖥️ Interface Gráfica (Electron)

Além da versão em linha de comando, este projeto inclui uma interface gráfica baseada em Electron para facilitar a configuração e o controle do bot.

### Requisitos adicionais
- Node.js (recomendado 16+)
- npm (gerenciador de pacotes)
- ADB instalado e funcionando no sistema

### Instalar dependências da GUI
No diretório do projeto, execute:

```bash
# Instala dependências Node (uma vez)
npm install
```

Ou use o script de inicialização disponibilizado:

```bash
./start_gui.sh
```

### Executar a interface (desenvolvimento)

```bash
# Inicia a interface Electron (abertura da janela GUI)
npm start
```

### Observações
- A interface salva as configurações no `localStorage` do Electron (não em `bot_config.json`).
- Se alterar arquivos em `electron/`, reinicie a aplicação para recarregar o `preload.js` e o processo principal.
- Para empacotar a aplicação (opcional), adicione e configure uma ferramenta como `electron-builder` ou `electron-forge`.


## ⚙️ Configuração

### 1. Ativar Depuração USB no Android

1. Vá em **Configurações** → **Sobre o telefone**
2. Toque 7 vezes em **Número da compilação**
3. Volte e acesse **Opções do desenvolvedor**
4. Ative **Depuração USB**
5. Ative **Depuração USB via rede**

### 2. Conectar via ADB WiFi

```bash
# Conectar via USB primeiro
adb tcpip 5555

# Desconectar USB e conectar via WiFi
adb connect <IP_DO_DISPOSITIVO>:5555
```

### 3. Configurar bot_config.json

O arquivo `bot_config.json` contém todas as configurações do bot:

```json
{
  "device": "192.168.240.112:5555",
  "camera_reset": {
    "enabled": true,
    "x": 67,
    "y": 146,
    "interval": 8.0,
    "description": "Resetar Camera"
  },
  "lure": {
    "enabled": false,
    "x": 1728,
    "y": 803,
    "interval": 3.0,
    "description": "Lure"
  },
  "joystick": {
    "center_x": 248,
    "center_y": 789,
    "duration": 4000,
    "step_duration": 500,
    "step_interval": 0.3,
    "steps_per_direction": 4,
    "cycle_interval": 5,
    "forward": {"x": 246, "y": 697},
    "backward": {"x": 243, "y": 869},
    "left": {"x": 334, "y": 787},
    "right": {"x": 164, "y": 790}
  },
  "clicks": [
    {
      "x": 1833,
      "y": 540,
      "interval": 2.0,
      "description": "Skill 1"
    }
  ]
}
```

#### Parâmetros Principais

- **device**: Endereço IP:porta do dispositivo Android
- **camera_reset**: Configuração para reset automático de câmera
  - `enabled`: Habilita/desabilita a função
  - `x`, `y`: Coordenadas do botão de reset
  - `interval`: Intervalo entre resets em segundos
- **lure**: Configuração para cliques automáticos de atração
  - `enabled`: Habilita/desabilita a função
  - `x`, `y`: Coordenadas do botão de lure
  - `interval`: Intervalo entre cliques em segundos
- **joystick**: Configuração do joystick virtual
  - `center_x`, `center_y`: Centro do joystick
  - `duration`: Duração padrão de movimento contínuo (ms)
  - `step_duration`: Duração de cada passo (ms)
  - `step_interval`: Pausa entre passos (segundos)
  - `steps_per_direction`: Número de passos por direção
  - `cycle_interval`: Pausa entre ciclos completos (segundos)
  - Direções: `forward`, `backward`, `left`, `right`
- **clicks**: Lista de cliques sequenciais
  - `x`, `y`: Coordenadas do clique
  - `interval`: Tempo de espera após este clique (segundos)
  - `description`: Descrição do botão/ação

## 🚀 Uso

### Executar o Bot

```bash
python3 simple_bot.py
```

### Menu Principal

```
==================================================
BOT SIMPLES ADB - MENU
==================================================
1 - Iniciar Bot (cliques automáticos)
2 - Ativar Pointer Location (mostrar coordenadas)
3 - Desativar Pointer Location
4 - Habilitar/Desabilitar Lure
5 - Lure com Joystick (frente → esquerda → trás → direita)
6 - Sair
==================================================
```

### Opções do Menu

#### 1. Iniciar Bot
- Executa a sequência de cliques configurada em `bot_config.json`
- Se `camera_reset.enabled = true`, inicia thread paralela para reset de câmera
- Se `lure.enabled = true`, inicia thread paralela para cliques de lure
- **Pressione Ctrl+C para parar**

#### 2. Ativar Pointer Location
- Ativa a exibição de coordenadas na tela do Android
- Útil para descobrir as coordenadas de botões para configurar no JSON
- Execute: `adb shell settings put system pointer_location 1`

#### 3. Desativar Pointer Location
- Remove a exibição de coordenadas da tela

#### 4. Habilitar/Desabilitar Lure
- Alterna o estado de `lure.enabled` no arquivo de configuração
- Mudança será aplicada na próxima execução do bot

#### 5. Lure com Joystick
- Executa movimento em quadrado usando o joystick virtual
- Sequência: frente → esquerda → trás → direita
- Usa modo com passos intervalados para movimento mais natural
- Loop infinito até pressionar Ctrl+C

#### 6. Sair
- Desconecta do dispositivo e encerra o programa

### Descobrindo Coordenadas

1. Ative o Pointer Location (opção 2 do menu)
2. Toque nos botões desejados na tela
3. Observe as coordenadas no topo da tela
4. Anote os valores X e Y
5. Adicione ao `bot_config.json`
6. Desative o Pointer Location (opção 3)

### Exemplo de Uso

```bash
# 1. Conectar ao dispositivo
python3 simple_bot.py

# 2. Ativar Pointer Location
Escolha: 2

# 3. Anotar coordenadas tocando nos botões

# 4. Desativar Pointer Location
Escolha: 3

# 5. Editar bot_config.json com as coordenadas

# 6. Iniciar o bot
Escolha: 1

# Bot executará:
# - Sequência de cliques configurada
# - Camera reset em paralelo (se habilitado)
# - Lure em paralelo (se habilitado)
```

## 📁 Estrutura do Projeto

```
bot_sro_mobile/
├── simple_bot.py          # Script principal do bot
├── bot_config.json        # Arquivo de configuração
├── README.md              # Este arquivo
├── requirements.txt       # Dependências Python (vazio)
└── __init__.py           # Módulo Python
```

### Classe Principal: `SimpleBotADB`

```python
class SimpleBotADB:
    def __init__(self, device_address: str)
    def check_adb() -> bool
    def connect() -> bool
    def disconnect() -> bool
    def tap(x: int, y: int) -> bool
    def click_loop(x: int, y: int, interval: float, max_clicks: int)
    def click_sequence(positions: list, interval: float, repeat: int)
    def enable_pointer_location() -> bool
    def disable_pointer_location() -> bool
    def move_joystick(start_x, start_y, end_x, end_y, duration, direction) -> bool
    def move_joystick_forward(start_x, start_y, end_x, end_y, duration) -> bool
    def lure_with_joystick(joystick_config: dict, duration: int, interval: float) -> bool
    def lure_with_joystick_steps(joystick_config: dict, step_duration: int, 
                                  step_interval: float, steps_per_direction: int) -> bool
```

## 🐛 Troubleshooting

### ADB não encontrado
```
✗ ADB não encontrado. Instale com: sudo apt install adb
```
**Solução**: Instale o ADB conforme instruções de instalação acima.

### Falha ao conectar
```
✗ Falha ao conectar: connection refused
```
**Possíveis causas**:
- Dispositivo não está na mesma rede WiFi
- IP do dispositivo mudou
- Depuração USB desativada
- Porta 5555 não está aberta

**Soluções**:
1. Verificar IP do dispositivo: **Configurações** → **Sobre** → **Status** → **Endereço IP**
2. Reconectar via USB: `adb tcpip 5555`
3. Verificar depuração USB está ativada
4. Reiniciar o servidor ADB: `adb kill-server && adb start-server`

### Cliques não funcionam
```
✗ Erro ao clicar: error: device offline
```
**Solução**: Reconectar ao dispositivo
```bash
adb disconnect
adb connect <IP_DO_DISPOSITIVO>:5555
```

### Coordenadas erradas
- Use o **Pointer Location** para descobrir coordenadas precisas
- Lembre-se que coordenadas podem variar entre dispositivos
- Teste cliques individuais antes de adicionar ao bot

### Bot não inicia threads paralelas
- Verifique se `camera_reset.enabled` está como `true` no JSON
- Verifique se `lure.enabled` está como `true` no JSON
- Certifique-se que o JSON está formatado corretamente

### Movimento do joystick não funciona
- Verifique as coordenadas do joystick no seu dispositivo
- Ajuste `center_x` e `center_y` para o centro do joystick
- Ajuste as coordenadas direcionais (forward, backward, left, right)
- Teste diferentes valores de `duration` e `step_duration`

## 🔒 Aviso Legal

Este bot é apenas para fins educacionais. O uso de bots em jogos online pode violar os Termos de Serviço e resultar em banimento da conta. Use por sua conta e risco.

## 📝 Licença

Este projeto é de código aberto. Sinta-se livre para usar, modificar e distribuir.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no GitHub.

---

**Desenvolvido com ❤️ para a comunidade SRO Mobile**
