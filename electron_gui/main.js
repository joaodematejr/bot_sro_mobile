const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

let mainWindow;
let botProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 700,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

ipcMain.handle('load-config', async () => {
  const configPath = path.join(__dirname, '../config_farming_adb.json');
  return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
});

ipcMain.handle('save-config', async (event, config) => {
  const configPath = path.join(__dirname, '../config_farming_adb.json');
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  return true;
});

ipcMain.handle('start-bot', (event) => {
  if (botProcess) return false;
  botProcess = spawn('python3', ['../main.py'], { cwd: path.join(__dirname, '..') });
  botProcess.stdout.on('data', (data) => {
    mainWindow.webContents.send('bot-log', data.toString());
  });
  botProcess.stderr.on('data', (data) => {
    mainWindow.webContents.send('bot-log', data.toString());
  });
  botProcess.on('close', (code) => {
    mainWindow.webContents.send('bot-log', `Bot finalizado (código ${code})`);
    botProcess = null;
  });
  return true;
});

ipcMain.handle('stop-bot', () => {
  if (botProcess) {
    botProcess.kill();
    botProcess = null;
    return true;
  }
  return false;
});
