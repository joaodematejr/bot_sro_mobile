import sys
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("Pacote ultralytics não encontrado. Instale com: pip install ultralytics")
    sys.exit(1)

ROOT = Path(__file__).parent.resolve()
DATA_YAML = ROOT / 'dataset_yolo/data.yaml'
PREV_MODEL = ROOT / 'runs/detect/train/weights/best.pt'

if not DATA_YAML.exists():
    print(f"Arquivo data.yaml não encontrado: {DATA_YAML}")
    sys.exit(1)
if not PREV_MODEL.exists():
    print(f"Modelo anterior não encontrado: {PREV_MODEL}")
    sys.exit(1)

print(f"Treinamento incremental usando modelo: {PREV_MODEL}")
print(f"Dataset: {DATA_YAML}")

model = YOLO(str(PREV_MODEL))
results = model.train(data=str(DATA_YAML), epochs=10, imgsz=640)
print("Treinamento incremental finalizado!")
print("Novo modelo salvo em:", results.save_dir)
