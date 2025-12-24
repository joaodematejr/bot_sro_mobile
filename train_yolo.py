
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
IMAGES_DIR = ROOT / 'dataset_yolo/images/train'
LABELS_DIR = ROOT / 'dataset_yolo/labels/train'
DATA_YAML = ROOT / 'dataset_yolo/data.yaml'
CLASSES_PATH = LABELS_DIR.parent / 'classes.txt'

def gerar_data_yaml():
    if not CLASSES_PATH.exists():
        print(f"Arquivo de classes não encontrado: {CLASSES_PATH}")
        sys.exit(1)
    with open(CLASSES_PATH, 'r') as f:
        names = [line.strip() for line in f if line.strip()]
    data = {
        'train': str(IMAGES_DIR.resolve()),
        'val': str(IMAGES_DIR.resolve()),
        'nc': len(names),
        'names': names
    }
    with open(DATA_YAML, 'w') as f:
        yaml.dump(data, f)
    print(f"Arquivo data.yaml gerado em: {DATA_YAML}")

def main():
    gerar_data_yaml()
    print("Iniciando treinamento YOLO via API Ultralytics...")
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Pacote ultralytics não encontrado. Instale com: pip install ultralytics")
        sys.exit(1)
    model = YOLO('yolov5s.pt')
    results = model.train(data=str(DATA_YAML), epochs=50, imgsz=640)
    print("Treinamento finalizado!")

if __name__ == "__main__":
    main()
