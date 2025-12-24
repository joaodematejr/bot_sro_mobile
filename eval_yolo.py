import sys
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("Pacote ultralytics não encontrado. Instale com: pip install ultralytics")
    sys.exit(1)

ROOT = Path(__file__).parent.resolve()
MODEL_PATH = ROOT / 'runs/detect/train/weights/best.pt'
DATA_YAML = ROOT / 'dataset_yolo/data.yaml'

if not MODEL_PATH.exists():
    print(f"Modelo não encontrado: {MODEL_PATH}")
    sys.exit(1)
if not DATA_YAML.exists():
    print(f"Arquivo data.yaml não encontrado: {DATA_YAML}")
    sys.exit(1)

print(f"Avaliando modelo: {MODEL_PATH}")
print(f"Usando dataset: {DATA_YAML}")

model = YOLO(str(MODEL_PATH))
results = model.val(data=str(DATA_YAML), imgsz=640, split='val')

# Exibe métricas principais
metrics = results.metrics if hasattr(results, 'metrics') else None
if metrics:
    print("\nMétricas de avaliação:")
    for k, v in metrics.items():
        print(f"{k}: {v}")
else:
    print("Avaliação concluída. Veja detalhes nos arquivos de saída.")
