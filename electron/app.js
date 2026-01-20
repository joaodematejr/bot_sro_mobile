// Estado global
let botRunning = false;
let clickCount = 0;
let startTime = null;
let timerInterval = null;
let lureLoopRunning = false;
let config = {
    device: '',
    game_start: { enabled: false, x: 1728, y: 803 },
    camera_reset: { enabled: false, x: 67, y: 146, interval: 8.0 },
    berserker: { enabled: false, x: 1500, y: 700, interval: 10.0 },
    debuff: { 
        enabled: false, 
        echoX: 1200, 
        echoY: 800, 
        weaponX: 1000, 
        weaponY: 600,
        delay: 3,
        interval: 300 
    },
    joystick: {
        pattern: 'straight',
        centerX: 193,
        centerY: 903,
        radius: 60,
        duration: 100,
        pause: 0.2,
        movementInterval: 0.5,
        repetitions: 1,
        loopEnabled: false
    }
};

// Elementos DOM
const elements = {
    deviceAddress: document.getElementById('device-address'),
    btnConnect: document.getElementById('btn-connect'),
    btnDisconnect: document.getElementById('btn-disconnect'),
    btnPointerOn: document.getElementById('btn-pointer-on'),
    btnPointerOff: document.getElementById('btn-pointer-off'),
    gameStartEnabled: document.getElementById('game-start-enabled'),
    gameStartX: document.getElementById('game-start-x'),
    gameStartY: document.getElementById('game-start-y'),
    cameraEnabled: document.getElementById('camera-enabled'),
    cameraX: document.getElementById('camera-x'),
    cameraY: document.getElementById('camera-y'),
    cameraInterval: document.getElementById('camera-interval'),    berserkerEnabled: document.getElementById('berserker-enabled'),
    berserkerX: document.getElementById('berserker-x'),
    berserkerY: document.getElementById('berserker-y'),
    berserkerInterval: document.getElementById('berserker-interval'),    berserkerEnabled: document.getElementById('berserker-enabled'),
    berserkerX: document.getElementById('berserker-x'),
    berserkerY: document.getElementById('berserker-y'),
    berserkerInterval: document.getElementById('berserker-interval'),
    debuffEnabled: document.getElementById('debuff-enabled'),
    debuffEchoX: document.getElementById('debuff-echo-x'),
    debuffEchoY: document.getElementById('debuff-echo-y'),
    debuffWeaponX: document.getElementById('debuff-weapon-x'),
    debuffWeaponY: document.getElementById('debuff-weapon-y'),
    debuffDelay: document.getElementById('debuff-delay'),
    debuffInterval: document.getElementById('debuff-interval'),
    debuffIntervalUnit: document.getElementById('debuff-interval-unit'),
    btnSaveConfig: document.getElementById('btn-save-config'),
    btnStartBot: document.getElementById('btn-start-bot'),
    btnStopBot: document.getElementById('btn-stop-bot'),
    botStatusText: document.getElementById('bot-status-text'),
    runtime: document.getElementById('runtime'),
    logContent: document.getElementById('log-content'),
    btnClearLog: document.getElementById('btn-clear-log'),
    connectionStatus: document.getElementById('connection-status'),
    // Lure tab elements
    patternStraight: document.getElementById('pattern-straight-radio'),
    patternSquare: document.getElementById('pattern-square-radio'),
    joystickCenterX: document.getElementById('joystick-center-x'),
    joystickCenterY: document.getElementById('joystick-center-y'),
    joystickRadius: document.getElementById('joystick-radius'),
    joystickDuration: document.getElementById('joystick-duration'),
    joystickPause: document.getElementById('joystick-pause'),
    joystickMovementInterval: document.getElementById('joystick-movement-interval'),
    joystickRepetitions: document.getElementById('joystick-repetitions'),
    btnExecuteLure: document.getElementById('btn-execute-lure'),
    btnSaveLureConfig: document.getElementById('btn-save-lure-config'),
    patternDescription: document.getElementById('pattern-description'),
    lureLoopEnabled: document.getElementById('lure-loop-enabled'),
    btnStartLureLoop: document.getElementById('btn-start-lure-loop'),
    btnStopLureLoop: document.getElementById('btn-stop-lure-loop'),
    loopStatusBadge: document.getElementById('loop-status-badge')
};

// Funções de Log
function addLog(message, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    elements.logContent.appendChild(entry);
    elements.logContent.scrollTop = elements.logContent.scrollHeight;
}

// Carrega configuração do localStorage
function loadConfig() {
    console.log('[LoadConfig] Iniciando carregamento...');
    const savedConfig = localStorage.getItem('botConfig');
    console.log('[LoadConfig] savedConfig raw:', savedConfig);
    
    if (savedConfig) {
        config = JSON.parse(savedConfig);
        
        // Garantir que campos novos existem (para compatibilidade com versões antigas)
        if (!config.game_start) {
            config.game_start = { enabled: false, x: 1728, y: 803 };
        }
        if (!config.camera_reset) {
            config.camera_reset = { enabled: false, x: 67, y: 146, interval: 8.0 };
        }
        if (!config.berserker) {
            config.berserker = { enabled: false, x: 1500, y: 700, interval: 10.0 };
        }
        if (!config.debuff) {
            config.debuff = { enabled: false, echoX: 1200, echoY: 800, weaponX: 1000, weaponY: 600, delay: 3, interval: 300 };
        } else if (!config.debuff.delay) {
            config.debuff.delay = 3; // Adiciona delay se não existir
        }
        if (!config.joystick) {
            config.joystick = {
                pattern: 'straight',
                centerX: 193,
                centerY: 903,
                radius: 60,
                duration: 100,
                pause: 0.2,
                movementInterval: 0.5,
                repetitions: 1,
                loopEnabled: false
            };
        }
        
        console.log('[LoadConfig] Configuração carregada do localStorage:', config);
        console.log('[LoadConfig] Device:', config.device);
    } else {
        // Config padrão
        config = {
            device: '',
            game_start: { enabled: false, x: 1728, y: 803 },
            camera_reset: { enabled: false, x: 67, y: 146, interval: 8.0 },
            berserker: { enabled: false, x: 1500, y: 700, interval: 10.0 },
            debuff: { enabled: false, echoX: 1200, echoY: 800, weaponX: 1000, weaponY: 600, delay: 3, interval: 300 },
            joystick: {
                pattern: 'straight',
                centerX: 193,
                centerY: 903,
                radius: 60,
                duration: 100,
                pause: 0.2,
                movementInterval: 0.5,
                repetitions: 1,
                loopEnabled: false
            }
        };
        console.log('[LoadConfig] Nenhuma configuração salva, usando padrão');
    }
    updateUIFromConfig();
    addLog('Configuração carregada', 'success');
}

// Atualiza UI com a configuração
function updateUIFromConfig() {
    console.log('[UpdateUI] Atualizando UI com config.device:', config.device);
    elements.deviceAddress.value = config.device || '';
    console.log('[UpdateUI] deviceAddress.value definido como:', elements.deviceAddress.value);
    
    // Game start config
    elements.gameStartEnabled.checked = config.game_start?.enabled || false;
    elements.gameStartX.value = config.game_start?.x || 1728;
    elements.gameStartY.value = config.game_start?.y || 803;
    
    elements.cameraEnabled.checked = config.camera_reset?.enabled || false;
    elements.cameraX.value = config.camera_reset?.x || 67;
    elements.cameraY.value = config.camera_reset?.y || 146;
    elements.cameraInterval.value = config.camera_reset?.interval || 8.0;
    
    elements.berserkerEnabled.checked = config.berserker?.enabled || false;
    elements.berserkerX.value = config.berserker?.x || 1500;
    elements.berserkerY.value = config.berserker?.y || 700;
    elements.berserkerInterval.value = config.berserker?.interval || 10.0;
    
    // Debuff config
    console.log('Carregando config.debuff:', config.debuff);
    elements.debuffEnabled.checked = config.debuff?.enabled || false;
    elements.debuffEchoX.value = config.debuff?.echoX || 1200;
    elements.debuffEchoY.value = config.debuff?.echoY || 800;
    elements.debuffWeaponX.value = config.debuff?.weaponX || 1000;
    elements.debuffWeaponY.value = config.debuff?.weaponY || 600;
    elements.debuffDelay.value = config.debuff?.delay || 3;
    const debuffIntervalSeconds = config.debuff?.interval || 300;
    if (debuffIntervalSeconds >= 60) {
        elements.debuffInterval.value = debuffIntervalSeconds / 60;
        elements.debuffIntervalUnit.value = 'minutes';
    } else {
        elements.debuffInterval.value = debuffIntervalSeconds;
        elements.debuffIntervalUnit.value = 'seconds';
    }
    
    // Joystick config
    if (config.joystick?.pattern === 'square') {
        elements.patternSquare.checked = true;
    } else {
        elements.patternStraight.checked = true;
    }
    elements.joystickCenterX.value = config.joystick?.centerX || 193;
    elements.joystickCenterY.value = config.joystick?.centerY || 903;
    elements.joystickRadius.value = config.joystick?.radius || 60;
    elements.joystickDuration.value = config.joystick?.duration || 100;
    elements.joystickPause.value = config.joystick?.pause || 0.2;
    elements.joystickMovementInterval.value = config.joystick?.movementInterval || 0.5;
    elements.joystickRepetitions.value = config.joystick?.repetitions || 1;
    elements.lureLoopEnabled.checked = config.joystick?.loopEnabled || false;
    
    // Atualiza botões do loop
    elements.btnStartLureLoop.disabled = !elements.lureLoopEnabled.checked;
    
    updatePatternDescription();
}

// Salva configuração
async function saveConfig() {
    config.device = elements.deviceAddress.value;
    
    console.log('[SaveConfig] Lendo elementos do DOM:');
    console.log('  gameStartEnabled.checked:', elements.gameStartEnabled.checked);
    console.log('  gameStartX.value:', elements.gameStartX.value);
    console.log('  gameStartY.value:', elements.gameStartY.value);
    
    config.game_start = {
        enabled: elements.gameStartEnabled.checked,
        x: parseInt(elements.gameStartX.value),
        y: parseInt(elements.gameStartY.value)
    };
    
    console.log('[SaveConfig] config.game_start montado:', config.game_start);
    
    config.camera_reset = {
        enabled: elements.cameraEnabled.checked,
        x: parseInt(elements.cameraX.value),
        y: parseInt(elements.cameraY.value),
        interval: parseFloat(elements.cameraInterval.value)
    };
    
    config.berserker = {
        enabled: elements.berserkerEnabled.checked,
        x: parseInt(elements.berserkerX.value),
        y: parseInt(elements.berserkerY.value),
        interval: parseFloat(elements.berserkerInterval.value)
    };
    
    // Converte intervalo de debuff para segundos
    const debuffIntervalValue = parseFloat(elements.debuffInterval.value);
    const debuffIntervalUnit = elements.debuffIntervalUnit.value;
    const debuffIntervalSeconds = debuffIntervalUnit === 'minutes' ? debuffIntervalValue * 60 : debuffIntervalValue;
    
    config.debuff = {
        enabled: elements.debuffEnabled.checked,
        echoX: parseInt(elements.debuffEchoX.value),
        echoY: parseInt(elements.debuffEchoY.value),
        weaponX: parseInt(elements.debuffWeaponX.value),
        weaponY: parseInt(elements.debuffWeaponY.value),
        delay: parseFloat(elements.debuffDelay.value),
        interval: debuffIntervalSeconds
    };
    
    console.log('Salvando config no localStorage:', config);
    
    config.joystick = {
        pattern: elements.patternSquare.checked ? 'square' : 'straight',
        centerX: parseInt(elements.joystickCenterX.value),
        centerY: parseInt(elements.joystickCenterY.value),
        radius: parseInt(elements.joystickRadius.value),
        duration: parseInt(elements.joystickDuration.value),
        pause: parseFloat(elements.joystickPause.value),
        movementInterval: parseFloat(elements.joystickMovementInterval.value),
        repetitions: parseInt(elements.joystickRepetitions.value),
        loopEnabled: elements.lureLoopEnabled.checked
    };
    
    console.log('Salvando config no localStorage:', config);
    console.log('game_start:', config.game_start);
    console.log('camera_reset:', config.camera_reset);
    
    // Salva no localStorage
    localStorage.setItem('botConfig', JSON.stringify(config));
    addLog('Configuração salva com sucesso!', 'success');
}

// Conecta ao dispositivo
async function connect() {
    const result = await window.api.connect(elements.deviceAddress.value);
    if (result.success) {
        addLog('Conectado ao dispositivo', 'success');
        updateConnectionStatus(true);
        elements.btnConnect.disabled = true;
        elements.btnDisconnect.disabled = false;
    } else {
        addLog(`Falha ao conectar: ${result.error}`, 'error');
    }
}

// Desconecta do dispositivo
async function disconnect() {
    const result = await window.api.disconnect();
    if (result.success) {
        addLog('Desconectado do dispositivo', 'info');
        updateConnectionStatus(false);
        elements.btnConnect.disabled = false;
        elements.btnDisconnect.disabled = true;
    }
}

// Atualiza status de conexão
function updateConnectionStatus(connected) {
    const badge = elements.connectionStatus;
    const icon = badge.querySelector('.bi-circle-fill');
    const text = badge.querySelector('.status-text');
    
    if (connected) {
        icon.classList.remove('text-danger');
        icon.classList.add('text-success');
        text.textContent = 'Conectado';
        badge.classList.add('connected');
    } else {
        icon.classList.remove('text-success');
        icon.classList.add('text-danger');
        text.textContent = 'Desconectado';
        badge.classList.remove('connected');
    }
}

// Pointer Location
async function togglePointer(enable) {
    const result = await window.api.togglePointer(enable);
    if (result.success) {
        addLog(`Pointer Location ${enable ? 'ativado' : 'desativado'}`, 'info');
    }
}

// Inicia bot
async function startBot() {
    saveConfig(); // Salva no localStorage
    
    // Recarrega a config do localStorage para garantir que está atualizada
    const savedConfig = localStorage.getItem('botConfig');
    if (savedConfig) {
        config = JSON.parse(savedConfig);
    }
    
    console.log('[StartBot] Enviando config para main.js:', config);
    console.log('[StartBot] game_start:', config.game_start);
    console.log('[StartBot] camera_reset:', config.camera_reset);
    
    // Envia a config atual para o main process
    const result = await window.api.startBot(config);
    if (result.success) {
        botRunning = true;
        startTime = Date.now();
        startTimer();
        elements.btnStartBot.disabled = true;
        elements.btnStopBot.disabled = false;
        elements.botStatusText.textContent = 'Executando';
        elements.botStatusText.classList.remove('text-danger');
        elements.botStatusText.classList.add('text-success');
        addLog('Bot iniciado!', 'success');
    } else {
        addLog(`Erro ao iniciar bot: ${result.error}`, 'error');
    }
}

// Para bot
async function stopBot() {
    // Recarrega a config do localStorage
    const savedConfig = localStorage.getItem('botConfig');
    if (savedConfig) {
        config = JSON.parse(savedConfig);
    }
    
    const result = await window.api.stopBot(config);
    if (result.success) {
        botRunning = false;
        stopTimer();
        elements.btnStartBot.disabled = false;
        elements.btnStopBot.disabled = true;
        elements.botStatusText.textContent = 'Parado';
        elements.botStatusText.classList.remove('text-success');
        elements.botStatusText.classList.add('text-danger');
        addLog('Bot parado', 'warning');
    }
}

// Timer
function startTimer() {
    timerInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const hours = Math.floor(elapsed / 3600000);
        const minutes = Math.floor((elapsed % 3600000) / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        elements.runtime.textContent = 
            `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// Atualiza descrição do padrão de movimento
function updatePatternDescription() {
    const pattern = elements.patternSquare.checked ? 'square' : 'straight';
    if (pattern === 'square') {
        elements.patternDescription.innerHTML = '<strong>Quadrado:</strong> Movimento em 4 direções (cima, direita, baixo, esquerda) formando um padrão quadrado completo.';
    } else {
        elements.patternDescription.innerHTML = '<strong>Linha Reta:</strong> Movimento de ida e volta - vai para frente e retorna para trás.';
    }
}

// Executa movimento de lure
async function executeLure() {
    const pattern = elements.patternSquare.checked ? 'square' : 'straight';
    const joystickConfig = {
        centerX: parseInt(elements.joystickCenterX.value),
        centerY: parseInt(elements.joystickCenterY.value),
        radius: parseInt(elements.joystickRadius.value),
        duration: parseInt(elements.joystickDuration.value),
        pause: parseFloat(elements.joystickPause.value),
        movementInterval: parseFloat(elements.joystickMovementInterval.value),
        repetitions: parseInt(elements.joystickRepetitions.value),
        pattern: pattern
    };
    
    const result = await window.api.executeLurePattern(joystickConfig);
    if (result.success) {
        addLog(`Movimento ${pattern === 'square' ? 'Quadrado' : 'Linha Reta'} executado com sucesso!`, 'success');
    } else {
        addLog(`Erro ao executar movimento: ${result.error}`, 'error');
    }
}

// Inicia loop de lure
async function startLureLoop() {
    if (lureLoopRunning) return;
    
    await saveConfig();
    const pattern = elements.patternSquare.checked ? 'square' : 'straight';
    const joystickConfig = {
        centerX: parseInt(elements.joystickCenterX.value),
        centerY: parseInt(elements.joystickCenterY.value),
        radius: parseInt(elements.joystickRadius.value),
        duration: parseInt(elements.joystickDuration.value),
        pause: parseFloat(elements.joystickPause.value),
        movementInterval: parseFloat(elements.joystickMovementInterval.value),
        repetitions: parseInt(elements.joystickRepetitions.value),
        pattern: pattern
    };
    
    const result = await window.api.startLureLoop(joystickConfig);
    if (result.success) {
        lureLoopRunning = true;
        elements.btnStartLureLoop.disabled = true;
        elements.btnStopLureLoop.disabled = false;
        elements.loopStatusBadge.textContent = 'Loop Ativo';
        elements.loopStatusBadge.classList.remove('bg-secondary', 'bg-danger');
        elements.loopStatusBadge.classList.add('bg-success');
        
        addLog(`Loop de lure iniciado (padrão: ${pattern === 'square' ? 'Quadrado' : 'Linha Reta'})`, 'success');
    } else {
        addLog(`Erro ao iniciar loop: ${result.error}`, 'error');
    }
}

// Para loop de lure
async function stopLureLoop() {
    const result = await window.api.stopLureLoop();
    if (result.success) {
        lureLoopRunning = false;
        elements.btnStartLureLoop.disabled = false;
        elements.btnStopLureLoop.disabled = true;
        elements.loopStatusBadge.textContent = 'Loop Parado';
        elements.loopStatusBadge.classList.remove('bg-success', 'bg-secondary');
        elements.loopStatusBadge.classList.add('bg-danger');
        addLog('Loop de lure parado', 'warning');
    }
}

// Event Listeners
elements.btnConnect.addEventListener('click', connect);
elements.btnDisconnect.addEventListener('click', disconnect);
elements.btnPointerOn.addEventListener('click', () => togglePointer(true));
elements.btnPointerOff.addEventListener('click', () => togglePointer(false));
elements.btnSaveConfig.addEventListener('click', saveConfig);
elements.btnStartBot.addEventListener('click', startBot);
elements.btnStopBot.addEventListener('click', stopBot);
elements.btnClearLog.addEventListener('click', () => {
    elements.logContent.innerHTML = '';
    addLog('Console limpo', 'info');
});

// Event listeners para aba de lure
elements.patternStraight.addEventListener('change', updatePatternDescription);
elements.patternSquare.addEventListener('change', updatePatternDescription);
elements.btnExecuteLure.addEventListener('click', executeLure);
elements.btnSaveLureConfig.addEventListener('click', saveConfig);
elements.btnStartLureLoop.addEventListener('click', startLureLoop);
elements.btnStopLureLoop.addEventListener('click', stopLureLoop);

// Toggle do loop enabled
elements.lureLoopEnabled.addEventListener('change', () => {
    const enabled = elements.lureLoopEnabled.checked;
    elements.btnStartLureLoop.disabled = !enabled;
    
    if (enabled) {
        elements.loopStatusBadge.textContent = 'Loop Habilitado';
        elements.loopStatusBadge.classList.remove('bg-secondary', 'bg-danger');
        elements.loopStatusBadge.classList.add('bg-info');
    } else {
        elements.loopStatusBadge.textContent = 'Loop Desativado';
        elements.loopStatusBadge.classList.remove('bg-info', 'bg-success', 'bg-danger');
        elements.loopStatusBadge.classList.add('bg-secondary');
        if (lureLoopRunning) {
            stopLureLoop();
        }
    }
});

elements.btnSaveLureConfig.addEventListener('click', saveConfig);

// Clique nos cards de padrão
document.getElementById('pattern-straight').addEventListener('click', () => {
    elements.patternStraight.checked = true;
    updatePatternDescription();
});
document.getElementById('pattern-square').addEventListener('click', () => {
    elements.patternSquare.checked = true;
    updatePatternDescription();
});

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    addLog('Interface iniciada', 'success');
    loadConfig();
});

// Listener para contagem de cliques do processo principal
window.api.onClickCount((count) => {
    clickCount = count;
    elements.clickCountElem.textContent = count;
});
