#!/bin/bash
# Instala dependências para o visualizador de métricas

echo "📦 Instalando matplotlib para visualização de métricas..."
pip3 install matplotlib --user

echo ""
echo "✅ Instalação completa!"
echo ""
echo "🚀 Para usar o visualizador:"
echo "   1. Rode o bot: python3 bot_ultra_adb.py"
echo "   2. Em outro terminal: python3 visualizador_metricas.py"
echo ""
echo "📊 Os gráficos serão atualizados a cada 2 segundos!"
