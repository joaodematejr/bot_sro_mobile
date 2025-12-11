#!/usr/bin/env python3
"""
Guia Visual de Métricas de Aprendizado ML
"""

print("""
╔══════════════════════════════════════════════════════════════════╗
║           📊 COMO MEDIR O APRENDIZADO DO ML                      ║
╚══════════════════════════════════════════════════════════════════╝

🎯 MÉTRICA #1: CONFIANÇA DO MODELO
   
   Barra de Progresso: [████████░░░░] 0-100%
   
   • 0-30%   → 🟥 Aprendendo (colete dados)
   • 30-60%  → 🟨 Funcional (otimizando)
   • 60-90%  → 🟩 Bom (resultados visíveis)
   • 90-100% → 🟦 Excelente (máximo desempenho)

📈 MÉTRICA #2: GANHO DE PERFORMANCE
   
   Compara primeiras 20 rotas vs últimas 20:
   
   Antes ML:  2,450 exp/min
   Depois ML: 3,280 exp/min
   Ganho:     +830 exp/min (+33.9%) ✅

💡 MÉTRICA #3: COBERTURA DO MAPA
   
   Exploração: 15.5% do mapa
   
   • <10%   → Explore mais áreas
   • 10-25% → Cobertura razoável
   • >25%   → Excelente cobertura

🗺️ MÉTRICA #4: DENSIDADE DESCOBERTA
   
   Melhor área: (450, 350) - 3,280 exp/min
   Pior área:   (200, 150) - 1,450 exp/min
   
   Variância alta = ML tem muito a otimizar
   Variância baixa = Áreas similares

⚔️ MÉTRICA #5: OTIMIZAÇÃO DE SKILLS
   
   Skills analisadas: 4
   Combos aprendidos: 15
   
   Skill mais eficiente: Skill 2 (35.5)

╔══════════════════════════════════════════════════════════════════╗
║                    🚀 COMO USAR                                   ║
╚══════════════════════════════════════════════════════════════════╝

1️⃣  RELATÓRIO RÁPIDO (texto no console)

    python3 metricas_aprendizado.py
    
    Escolha opção: 1
    
    Mostra:
    ✓ Confiança do modelo
    ✓ Dados coletados
    ✓ Melhor área descoberta
    ✓ Ganho com ML
    ✓ Recomendações

2️⃣  VISUALIZAÇÃO GRÁFICA (4 gráficos)

    python3 metricas_aprendizado.py
    
    Escolha opção: 2
    
    Mostra:
    📊 Evolução de Performance (EXP/min ao longo do tempo)
    📈 Distribuição de Densidade (histograma)
    🗺️ Progresso de Exploração (áreas descobertas)
    🎯 Confiança do Modelo (evolução)

3️⃣  MONITORAMENTO CONTÍNUO

    while true; do
        python3 metricas_aprendizado.py <<< "1"
        sleep 300  # A cada 5 minutos
    done

╔══════════════════════════════════════════════════════════════════╗
║              📊 INTERPRETANDO OS RESULTADOS                       ║
╚══════════════════════════════════════════════════════════════════╝

✅ SINAIS DE BOM APRENDIZADO:

   • Confiança > 60%
   • Ganho ML > +15%
   • Exploração > 15%
   • Média móvel de EXP crescente
   • Variância de densidade alta (encontrou áreas boas e ruins)

⚠️  SINAIS DE PROBLEMA:

   • Confiança estagnada < 30%
   • Ganho ML negativo
   • Exploração < 5% após 1 hora
   • EXP decrescente
   • Densidade média muito baixa

🔧 AÇÕES CORRETIVAS:

   Problema: Ganho negativo
   → Aguarde mais dados (mín. 50 rotas)
   → ML ainda aprendendo padrões
   
   Problema: Baixa exploração
   → Aumente raio_busca_area no config
   → Deixe modo exploração mais tempo
   
   Problema: Confiança estagnada
   → Verifique se bot está salvando dados
   → Confira arquivo ml_avancado_dados.json

╔══════════════════════════════════════════════════════════════════╗
║                  ⏱️ TIMELINE ESPERADA                             ║
╚══════════════════════════════════════════════════════════════════╝

0-20 min:  Coleta inicial, confiança 0-30%
           → Ainda explorando aleatoriamente

20-40 min: Primeiro treinamento, confiança 30-50%
           → ML começa a recomendar áreas

40-90 min: Otimização ativa, confiança 50-80%
           → Ganho visível de +15-30%

90+ min:   Máximo desempenho, confiança 80-100%
           → Ganho de +30-50%
           → Bot vai direto para melhores áreas

╔══════════════════════════════════════════════════════════════════╗
║                  💾 ARQUIVOS MONITORADOS                          ║
╚══════════════════════════════════════════════════════════════════╝

ml_avancado_dados.json
   └─ Histórico completo de aprendizado
   └─ Rotas, skills, combos, horários
   └─ Densidade de cada área

ml_avancado_modelo.pkl
   └─ Modelos ML treinados
   └─ Gradient Boosting + Random Forest

metricas_bot.json
   └─ Métricas gerais do bot
   └─ EXP, combates, tempo

╔══════════════════════════════════════════════════════════════════╗
║                    ✨ DICA PROFISSIONAL                           ║
╚══════════════════════════════════════════════════════════════════╝

Execute em 2 terminais simultaneamente:

Terminal 1: python3 bot_ultra_adb.py
Terminal 2: watch -n 300 'python3 metricas_aprendizado.py <<< "1"'

Assim você vê o bot farmando E as métricas atualizando! 🚀
""")
