import sys
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("Pacote ultralytics não encontrado. Instale com: pip install ultralytics")
    sys.exit(1)

ROOT = Path(__file__).parent.resolve()
MODEL_PATH = ROOT / 'runs/detect/train/weights/best.pt'
IMAGES_DIR = ROOT / 'dataset_yolo/images/train'
PRINTS_DIR = ROOT / 'prints_yolo'

if not MODEL_PATH.exists():
    print(f"Modelo não encontrado: {MODEL_PATH}")
    sys.exit(1)
if not IMAGES_DIR.exists():
    print(f"Pasta de imagens não encontrada: {IMAGES_DIR}")
    sys.exit(1)
PRINTS_DIR.mkdir(exist_ok=True)

print(f"Gerando detecções nas imagens de {IMAGES_DIR}")
print(f"Resultados serão salvos em {PRINTS_DIR}")

model = YOLO(str(MODEL_PATH))
image_paths = list(IMAGES_DIR.glob('*.jpg')) + list(IMAGES_DIR.glob('*.png'))
if not image_paths:
    print("Nenhuma imagem encontrada para visualização.")
    sys.exit(0)


# Forçar nomes das classes para 'mobs'
forced_names = ['mobs']

for img_path in image_paths:
    results = model(img_path)
    for r in results:
        # Sobrescreve os nomes das classes antes de salvar
        r.names = {i: name for i, name in enumerate(forced_names)}
        r.save(filename=str(PRINTS_DIR / img_path.name))
        print(f"Salvo: {PRINTS_DIR / img_path.name}")

print("Visualizações concluídas!")
