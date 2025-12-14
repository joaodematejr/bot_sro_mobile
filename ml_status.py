#!/usr/bin/env python3
"""
Status e gerenciamento de modelos ML
Mostra progresso de coleta de dados e permite treinar modelos manualmente
"""

from ai_modules import MLPredictor
import os
from pathlib import Path

def show_status():
    """Mostra status do treinamento ML"""
    print("=" * 60)
    print("  📊 STATUS DE MACHINE LEARNING")
    print("=" * 60)
    
    # Inicializa MLPredictor
    ml = MLPredictor()
    
    # Obtém status
    status = ml.get_training_status()
    
    print(f"\n📁 Pasta de modelos: {status['model_folder']}")
    
    # Verifica arquivos existentes
    model_folder = Path(status['model_folder'])
    if model_folder.exists():
        models = [
            ("modelo_sklearn.pkl", "RandomForest (densidade)"),
            ("modelo_ultra.pkl", "KMeans (clustering)"),
            ("modelo_ultra_adb.pkl", "Modelo completo"),
            ("ml_avancado_modelo.pkl", "Modelo avançado"),
            ("density_model.pkl", "Densidade (interno)"),
            ("cluster_model.pkl", "Cluster (interno)"),
            ("scaler.pkl", "Normalizador"),
            ("training_data.json", "Dados de treino")
        ]
        
        print(f"\n📦 Arquivos de modelo:")
        for filename, description in models:
            filepath = model_folder / filename
            if filepath.exists():
                size = os.path.getsize(filepath)
                size_kb = size / 1024
                print(f"  ✓ {filename:<30} ({size_kb:>6.1f} KB) - {description}")
            else:
                print(f"  ✗ {filename:<30} (não existe)")
    
    print(f"\n🧠 Dados de treino:")
    print(f"  • Amostras coletadas: {status['total_samples']}")
    print(f"  • Pode treinar: {'✓ Sim' if status['can_train'] else '✗ Não (mínimo 10)'}")
    
    if status['total_samples'] > 0:
        print(f"\n⏭️  Próximos marcos:")
        if status['samples_to_next_backup'] > 0:
            print(f"  • Backup automático: {status['samples_to_next_backup']} amostras faltando")
        if status['samples_to_next_train'] > 0:
            print(f"  • Treino automático: {status['samples_to_next_train']} amostras faltando")
        
        # Progresso visual
        total = status['total_samples']
        next_milestone = ((total // 50) + 1) * 50
        progress = (total % 50) / 50 * 100
        
        bar_width = 40
        filled = int(bar_width * progress / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        print(f"\n📈 Progresso até próximo backup ({total}/{next_milestone}):")
        print(f"  [{bar}] {progress:.1f}%")
    
    print(f"\n🎯 Marcos de treinamento:")
    print(f"  •  10 amostras: Treinamento mínimo habilitado")
    print(f"  •  50 amostras: Backup automático de dados")
    print(f"  • 100 amostras: Treino automático + salvamento de modelos")
    print(f"  • 200 amostras: 2º treino automático")
    
    return ml, status

def train_models(ml):
    """Treina modelos manualmente"""
    print("\n" + "=" * 60)
    print("  🤖 TREINAMENTO MANUAL DE MODELOS")
    print("=" * 60)
    
    if ml.force_train():
        print("\n✅ Modelos treinados com sucesso!")
        print("\nArquivos salvos:")
        print("  • modelo_sklearn.pkl")
        print("  • modelo_ultra.pkl")
        print("  • modelo_ultra_adb.pkl")
        print("  • ml_avancado_modelo.pkl")
    else:
        print("\n✗ Falha no treinamento")

def main():
    ml, status = show_status()
    
    if status['total_samples'] >= 10:
        print("\n" + "=" * 60)
        response = input("\n💡 Deseja treinar os modelos agora? (s/N): ")
        
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            train_models(ml)
        else:
            print("\n💡 Dica: Os modelos serão treinados automaticamente")
            print("   quando atingir 100 amostras durante o farming.")
    else:
        needed = 10 - status['total_samples']
        print(f"\n💡 Colete mais {needed} amostra(s) para habilitar treinamento")
        print("   Execute o farming com IA habilitada para coletar dados.")
    
    print("\n")

if __name__ == "__main__":
    main()
