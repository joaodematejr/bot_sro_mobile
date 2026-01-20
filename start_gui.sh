#!/bin/bash

echo "🎮 Bot SRO Mobile - Inicialização"
echo "=================================="
echo ""

# Verifica se ADB está instalado
if ! command -v adb &> /dev/null; then
    echo "❌ ADB não encontrado!"
    echo "   Instale com: sudo apt install adb"
    exit 1
fi

# Verifica se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado!"
    echo "   Instale com: sudo apt install nodejs npm"
    exit 1
fi

# Verifica se as dependências do Node estão instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências do Node.js..."
    npm install
fi

echo "✅ Tudo pronto!"
echo "🚀 Iniciando interface gráfica..."
echo ""

# Inicia aplicação Electron
npm start
