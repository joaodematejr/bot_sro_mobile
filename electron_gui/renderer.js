window.addEventListener('DOMContentLoaded', async () => {
  const form = document.getElementById('config-form');
  const saveBtn = document.getElementById('save-btn');
  const startBtn = document.getElementById('start-btn');
  const stopBtn = document.getElementById('stop-btn');
  const logsDiv = document.getElementById('logs');

  let config = await window.api.loadConfig();
  renderForm(config);

  saveBtn.onclick = async () => {
    const newConfig = {};
    for (const el of form.elements) {
      if (!el.name) continue;
      if (el.type === 'number') newConfig[el.name] = Number(el.value);
      else if (el.type === 'checkbox') newConfig[el.name] = el.checked;
      else newConfig[el.name] = el.value;
    }
    await window.api.saveConfig(newConfig);
    alert('Configuração salva!');
  };

  startBtn.onclick = async () => {
    logsDiv.innerText = '';
    await window.api.startBot();
  };

  stopBtn.onclick = async () => {
    await window.api.stopBot();
  };

  window.api.onBotLog((log) => {
    logsDiv.innerText += log;
    logsDiv.scrollTop = logsDiv.scrollHeight;
  });

  function renderForm(cfg) {
    form.innerHTML = '';
    for (const key in cfg) {
      if (typeof cfg[key] === 'object') continue;
      const label = document.createElement('label');
      label.innerText = key;
      const input = document.createElement('input');
      input.name = key;
      input.value = cfg[key];
      if (typeof cfg[key] === 'number') input.type = 'number';
      else if (typeof cfg[key] === 'boolean') input.type = 'checkbox', input.checked = cfg[key];
      else input.type = 'text';
      label.appendChild(input);
      form.appendChild(label);
    }
  }
});
