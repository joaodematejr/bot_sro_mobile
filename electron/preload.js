const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  connect: (device) => ipcRenderer.invoke('connect', device),
  disconnect: () => ipcRenderer.invoke('disconnect'),
  getDevices: () => ipcRenderer.invoke('get-devices'),
  togglePointer: (enable) => ipcRenderer.invoke('pointer', enable),
  startBot: (config) => ipcRenderer.invoke('start-bot', config),
  stopBot: (config) => ipcRenderer.invoke('stop-bot', config),
  lureJoystick: () => ipcRenderer.invoke('lure-joystick'),
  executeLurePattern: (joystickConfig) => ipcRenderer.invoke('execute-lure-pattern', joystickConfig),
  startLureLoop: (joystickConfig) => ipcRenderer.invoke('start-lure-loop', joystickConfig),
  stopLureLoop: () => ipcRenderer.invoke('stop-lure-loop'),
  getBotStatus: () => ipcRenderer.invoke('get-bot-status'),
  
  // Event listeners
  onClickCount: (callback) => {
    ipcRenderer.on('click-count', (event, count) => callback(count));
  }
});
