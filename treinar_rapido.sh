#!/bin/bash
# Script rápido para treinar modelo com recompensas

echo "🎓 Iniciando treinamento com recompensas..."
echo ""

python3 -c "
from treinador_recompensas import TreinadorComRecompensas

treinador = TreinadorComRecompensas()
treinador.treinar_com_recompensas(usar_gradient_boosting=False)

print('\n✅ Treinamento concluído!')
print('   Modelo salvo em: ml_models/modelo_com_recompensas.pkl')
print('\n💡 Para usar no bot, o modelo já está integrado!')
"
