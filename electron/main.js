const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');
const util = require('util');

const execPromise = util.promisify(exec);

let mainWindow;
let botRunning = false;
let botInterval = null;
let cameraInterval = null;
let berserkerInterval = null;
let debuffInterval = null;
let lureInterval = null;
let lureLoopInterval = null;
let lureLoopRunning = false;
let clickCount = 0;
let config = {
  device: '',
  camera_reset: { enabled: false, x: 67, y: 146, interval: 8.0 },
  berserker: { enabled: false, x: 1500, y: 700, interval: 10.0 },
  debuff: { enabled: false, echoX: 1200, echoY: 800, weaponX: 1000, weaponY: 600, interval: 300 },
  lure: { enabled: false, x: 1728, y: 803, interval: 3.0 },
  clicks: [],
  joystick: {
    pattern: 'straight',
    centerX: 193,
    centerY: 903,
    radius: 60,
    duration: 100,
    pause: 0.2,
    loopEnabled: false,
    loopInterval: 3.0
  }
};

const configPath = path.join(__dirname, '..', 'bot_config.json');

// Funções auxiliares
function loadConfig() {
  try {
    if (fs.existsSync(configPath)) {
      const data = fs.readFileSync(configPath, 'utf8');
      config = JSON.parse(data);
      
      // Garantir que todas as propriedades necessárias existem
      if (!config.camera_reset) {
        config.camera_reset = { enabled: false, x: 67, y: 146, interval: 8.0 };
      }
      if (!config.debuff) {
        config.debuff = { enabled: false, echoX: 1200, echoY: 800, weaponX: 1000, weaponY: 600, interval: 300 };
      }
      if (!config.lure) {
        config.lure = { enabled: false, x: 1728, y: 803, interval: 3.0 };
      }
      if (!config.joystick) {
        config.joystick = {
          pattern: 'straight',
          centerX: 193,
          centerY: 903,
          radius: 60,
          duration: 100,
          pause: 0.2,
          loopEnabled: false,
          loopInterval: 3.0
        };
      }
    }
  } catch (error) {
    console.error('Erro ao carregar config:', error);
  }
}

function saveConfig() {
  try {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  } catch (error) {
    console.error('Erro ao salvar config:', error);
  }
}

async function adbCommand(command) {
  try {
    const devicePrefix = config.device ? `-s ${config.device}` : '';
    const { stdout, stderr } = await execPromise(`adb ${devicePrefix} ${command}`);
    if (stderr && !stderr.includes('daemon started')) {
      throw new Error(stderr);
    }
    return stdout.trim();
  } catch (error) {
    throw error;
  }
}

async function adbTap(x, y) {
  console.log(`[ADB] Executando tap em X:${x} Y:${y}`);
  await adbCommand(`shell input tap ${x} ${y}`);
  console.log(`[ADB] Tap executado em X:${x} Y:${y}`);
}

async function adbSwipe(x1, y1, x2, y2, duration = 100) {
  await adbCommand(`shell input swipe ${x1} ${y1} ${x2} ${y2} ${duration}`);
}

function sleep(seconds) {
  return new Promise(resolve => setTimeout(resolve, seconds * 1000));
}

// Funções do bot
async function performCameraReset() {
  if (config.camera_reset.enabled) {
    await adbTap(config.camera_reset.x, config.camera_reset.y);
  }
}

async function performBerserker() {
  if (config.berserker && config.berserker.enabled) {
    console.log('[Berserker] Executando tap em X:', config.berserker.x, 'Y:', config.berserker.y);
    await adbTap(config.berserker.x, config.berserker.y);
  }
}

async function performDebuff() {
  if (config.debuff && config.debuff.enabled) {
    console.log('[Debuff] Clicando no echo...');
    await adbTap(config.debuff.echoX, config.debuff.echoY);
    const delay = config.debuff.delay || 3; // Usa o delay configurado ou 3 segundos como padrão
    await sleep(delay);
    console.log('[Debuff] Voltando para arma...');
    await adbTap(config.debuff.weaponX, config.debuff.weaponY);
    console.log('[Debuff] Ciclo completo');
  }
}

async function performLure() {
  if (config.lure.enabled) {
    await adbTap(config.lure.x, config.lure.y);
  }
}

async function performClicks() {
  // Verifica se clicks existe e é um array
  if (!config.clicks || !Array.isArray(config.clicks)) {
    return;
  }
  
  for (const click of config.clicks) {
    await adbTap(click.x, click.y);
    await sleep(click.interval || 2.0);
    clickCount++;
    if (mainWindow) {
      mainWindow.webContents.send('click-count', clickCount);
    }
  }
}

async function startBot() {
  if (botRunning) return;
  
  botRunning = true;
  clickCount = 0;
  
  console.log('[StartBot] Verificando game_start:', config.game_start);
  
  // Clica no botão de iniciar bot no jogo, se habilitado
  if (config.game_start && config.game_start.enabled) {
    console.log('[Game Start] Clicando no botão de iniciar bot no jogo...');
    await adbTap(config.game_start.x, config.game_start.y);
    await sleep(1); // Aguarda 1 segundo após clicar
  } else {
    console.log('[Game Start] Não habilitado ou não configurado');
  }
  
  // Camera reset interval
  if (config.camera_reset && config.camera_reset.enabled) {
    cameraInterval = setInterval(performCameraReset, config.camera_reset.interval * 1000);
  }

  // Berserker interval
  if (config.berserker && config.berserker.enabled) {
    berserkerInterval = setInterval(performBerserker, config.berserker.interval * 1000);
  }
  
  // Debuff interval - executa imediatamente e depois no intervalo
  if (config.debuff && config.debuff.enabled) {
    await performDebuff(); // Executa imediatamente
    debuffInterval = setInterval(performDebuff, config.debuff.interval * 1000);
  }
  
  // Lure interval
  if (config.lure && config.lure.enabled) {
    lureInterval = setInterval(performLure, config.lure.interval * 1000);
  }
  
  // Main click loop
  botInterval = setInterval(async () => {
    if (botRunning) {
      await performClicks();
    }
  }, 1000);
}

function stopBot() {
  botRunning = false;
  if (botInterval) {
    clearInterval(botInterval);
    botInterval = null;
  }
  if (cameraInterval) {
    clearInterval(cameraInterval);
    cameraInterval = null;
  }
  if (debuffInterval) {
    clearInterval(debuffInterval);
    debuffInterval = null;
  }
  if (berserkerInterval) {
    clearInterval(berserkerInterval);
    berserkerInterval = null;
  }
  if (lureInterval) {
    clearInterval(lureInterval);
    lureInterval = null;
  }
  if (lureLoopInterval) {
    clearInterval(lureLoopInterval);
    lureLoopInterval = null;
  }
}

// IPC Handlers
ipcMain.handle('get-config', () => {
  loadConfig();
  return config;
});

ipcMain.handle('save-config', (event, newConfig) => {
  // Garantir que todas as propriedades necessárias existem
  if (!newConfig.camera_reset) {
    newConfig.camera_reset = { enabled: false, x: 67, y: 146, interval: 8.0 };
  }
  if (!newConfig.berserker) {
    newConfig.berserker = { enabled: false, x: 1500, y: 700, interval: 10.0 };
  }
  if (!newConfig.debuff) {
    newConfig.debuff = { enabled: false, echoX: 1200, echoY: 800, weaponX: 1000, weaponY: 600, interval: 300 };
  }
  if (!newConfig.lure) {
    newConfig.lure = { enabled: false, x: 1728, y: 803, interval: 3.0 };
  }
  if (!newConfig.joystick) {
    newConfig.joystick = {
      pattern: 'straight',
      centerX: 193,
      centerY: 903,
      radius: 60,
      duration: 100,
      pause: 0.2,
      loopEnabled: false,
      loopInterval: 3.0
    };
  }
  config = newConfig;
  saveConfig();
  return { success: true };
});

ipcMain.handle('connect', async (event, device) => {
  try {
    config.device = device;
    
    // Verifica se é USB (sem :) ou WiFi (com :)
    if (device.includes(':')) {
      await adbCommand(`connect ${device}`);
    }
    
    // Verifica conexão
    const devices = await adbCommand('devices');
    if (devices.includes(device)) {
      saveConfig();
      return { success: true, message: 'Conectado ao dispositivo' };
    } else {
      throw new Error('Dispositivo não encontrado');
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('disconnect', async () => {
  try {
    stopBot();
    if (config.device.includes(':')) {
      await adbCommand(`disconnect ${config.device}`);
    }
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-devices', async () => {
  try {
    const output = await adbCommand('devices');
    const lines = output.split('\n').filter(line => line.includes('\tdevice'));
    const devices = lines.map(line => line.split('\t')[0]);
    return { success: true, devices };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('pointer', async (event, enable) => {
  try {
    const value = enable ? '1' : '0';
    await adbCommand(`shell settings put system pointer_location ${value}`);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('start-bot', async (event, newConfig) => {
  try {
    console.log('[IPC start-bot] Recebendo newConfig:', JSON.stringify(newConfig, null, 2));
    
    // Atualiza a config com os dados recebidos
    if (newConfig) {
      console.log('[IPC start-bot] game_start recebido:', newConfig.game_start);
      
      // Garantir que todas as propriedades necessárias existem
      if (!newConfig.game_start) {
        console.log('[IPC start-bot] game_start não existe, criando padrão');
        newConfig.game_start = { enabled: false, x: 1728, y: 803 };
      }
      if (!newConfig.camera_reset) {
        newConfig.camera_reset = { enabled: false, x: 67, y: 146, interval: 8.0 };
      }
      if (!newConfig.berserker) {
        newConfig.berserker = { enabled: false, x: 1500, y: 700, interval: 10.0 };
      }
      if (!newConfig.debuff) {
        newConfig.debuff = { enabled: false, echoX: 1200, echoY: 800, weaponX: 1000, weaponY: 600, interval: 300 };
      }
      if (!newConfig.lure) {
        newConfig.lure = { enabled: false, x: 1728, y: 803, interval: 3.0 };
      }
      if (!newConfig.clicks) {
        newConfig.clicks = [];
      }
      if (!newConfig.joystick) {
        newConfig.joystick = {
          pattern: 'straight',
          centerX: 193,
          centerY: 903,
          radius: 60,
          duration: 100,
          pause: 0.2,
          loopEnabled: false,
          loopInterval: 3.0
        };
      }
      config = newConfig;
      console.log('Config atualizada do localStorage - game_start:', config.game_start);
      console.log('Config atualizada do localStorage - debuff:', config.debuff);
    }
    await startBot();
    return { success: true };
  } catch (error) {
    stopBot();
    return { success: false, error: error.message };
  }
});

ipcMain.handle('stop-bot', async (event, newConfig) => {
  try {
    // Se game_start estiver habilitado, clica para desligar o bot no jogo
    if (newConfig && newConfig.game_start && newConfig.game_start.enabled) {
      console.log('[Stop Bot] Clicando para desligar bot no jogo em X:', newConfig.game_start.x, 'Y:', newConfig.game_start.y);
      await adbTap(newConfig.game_start.x, newConfig.game_start.y);
      // Aguarda um pouco para garantir que o clique foi processado
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    stopBot();
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('lure-joystick', async () => {
  try {
    const centerX = 193;
    const centerY = 903;
    const radius = 60;
    const swipeDuration = 100;
    
    // Sequence of movements
    const movements = [
      { x: centerX, y: centerY - radius, desc: 'cima' },
      { x: centerX + radius, y: centerY, desc: 'direita' },
      { x: centerX, y: centerY + radius, desc: 'baixo' },
      { x: centerX - radius, y: centerY, desc: 'esquerda' }
    ];
    
    for (const move of movements) {
      await adbSwipe(centerX, centerY, move.x, move.y, swipeDuration);
      await sleep(0.2);
    }
    
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('execute-lure-pattern', async (event, joystickConfig) => {
  try {
    const { centerX, centerY, radius, duration, pause, pattern, movementInterval = 0.5, repetitions = 1 } = joystickConfig;
    
    if (pattern === 'square') {
      // Movimento em quadrado: cima, direita, baixo, esquerda
      const movements = [
        { x: centerX, y: centerY - radius, desc: 'cima' },
        { x: centerX + radius, y: centerY, desc: 'direita' },
        { x: centerX, y: centerY + radius, desc: 'baixo' },
        { x: centerX - radius, y: centerY, desc: 'esquerda' }
      ];
      
      // Para cada direção, repete N vezes antes de ir para a próxima
      for (const move of movements) {
        for (let rep = 0; rep < repetitions; rep++) {
          await adbSwipe(centerX, centerY, move.x, move.y, duration);
          await sleep(pause);
          await sleep(movementInterval);
        }
      }
    } else {
      // Movimento em linha reta: vai para frente e volta para trás (eixo Y - vertical)
      // Repete N vezes conforme configurado
      for (let i = 0; i < repetitions; i++) {
        // Vai para frente (cima)
        await adbSwipe(centerX, centerY, centerX, centerY - radius, duration);
        await sleep(pause);
        await sleep(movementInterval);
      }
      for (let i = 0; i < repetitions; i++) {
        // Volta para trás (baixo)
        await adbSwipe(centerX, centerY, centerX, centerY + radius, duration);
        await sleep(pause);
        await sleep(movementInterval);
      }
    }
    
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Função auxiliar para executar padrão de lure
async function executeLureMovement(joystickConfig) {
  const { centerX, centerY, radius, duration, pause, pattern, movementInterval = 0.5, repetitions = 1 } = joystickConfig;
  
  if (pattern === 'square') {
    const movements = [
      { x: centerX, y: centerY - radius },
      { x: centerX + radius, y: centerY },
      { x: centerX, y: centerY + radius },
      { x: centerX - radius, y: centerY }
    ];
    
    // Para cada direção, repete N vezes antes de ir para a próxima
    for (const move of movements) {
      for (let rep = 0; rep < repetitions; rep++) {
        await adbSwipe(centerX, centerY, move.x, move.y, duration);
        await sleep(pause);
        await sleep(movementInterval);
      }
    }
  } else {
    // Linha reta: frente e trás com repetições
    for (let i = 0; i < repetitions; i++) {
      await adbSwipe(centerX, centerY, centerX, centerY - radius, duration);
      await sleep(pause);
      await sleep(movementInterval);
    }
    for (let i = 0; i < repetitions; i++) {
      await adbSwipe(centerX, centerY, centerX, centerY + radius, duration);
      await sleep(pause);
      await sleep(movementInterval);
    }
  }
}

ipcMain.handle('start-lure-loop', async (event, joystickConfig) => {
  try {
    // Para qualquer loop existente
    if (lureLoopInterval) {
      clearInterval(lureLoopInterval);
      lureLoopInterval = null;
    }
    
    lureLoopRunning = true;
    const pauseBetweenLoops = 2000; // 2 segundos de pausa entre cada ciclo completo
    
    console.log('[Loop Lure] Iniciando loop contínuo');
    
    // Função recursiva que espera cada execução terminar
    const runLoop = async () => {
      if (!lureLoopRunning) {
        console.log('[Loop Lure] Loop interrompido');
        return;
      }
      
      try {
        // Executa o movimento completo
        await executeLureMovement(joystickConfig);
        
        // Aguarda antes de iniciar o próximo ciclo
        if (lureLoopRunning) {
          await sleep(pauseBetweenLoops / 1000);
          // Agenda a próxima execução
          if (lureLoopRunning) {
            setImmediate(runLoop);
          }
        }
      } catch (error) {
        console.error('Erro no loop de lure:', error);
        if (lureLoopRunning) {
          await sleep(pauseBetweenLoops / 1000);
          setImmediate(runLoop);
        }
      }
    };
    
    // Inicia o loop
    runLoop();
    
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('stop-lure-loop', async () => {
  console.log('[Loop Lure] Comando de parada recebido');
  lureLoopRunning = false;
  lureLoopInterval = null;
  console.log('[Loop Lure] Loop parado');
  return { success: true };
});

ipcMain.handle('get-bot-status', () => {
  return {
    running: botRunning,
    clickCount: clickCount
  };
});

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png'),
    frame: true,
    backgroundColor: '#1a1a2e'
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  // Abre DevTools em modo de desenvolvimento
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', function () {
    stopBot();
    mainWindow = null;
  });
}

app.on('ready', () => {
  loadConfig();
  createWindow();
});

app.on('window-all-closed', function () {
  stopBot();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('quit', () => {
  stopBot();
});
