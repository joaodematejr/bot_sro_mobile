import os
import cv2
import glob

DATASET_IMG_DIR = 'dataset_yolo/images/train'
DATASET_LABEL_DIR = 'dataset_yolo/labels/train'

# Cores para as classes (adicione mais se tiver mais classes)
COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (0, 255, 255)]

# Nome das classes (ajuste conforme seu dataset.yaml)
CLASS_NAMES = ['mob']

def draw_boxes(img, label_path):
    if not os.path.exists(label_path):
        return img
    h, w = img.shape[:2]
    with open(label_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            cls, xc, yc, bw, bh = map(float, parts[:5])
            cls = int(cls)
            x1 = int((xc - bw/2) * w)
            y1 = int((yc - bh/2) * h)
            x2 = int((xc + bw/2) * w)
            y2 = int((yc + bh/2) * h)
            color = COLORS[cls % len(COLORS)]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            label = CLASS_NAMES[cls] if cls < len(CLASS_NAMES) else str(cls)
            cv2.putText(img, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return img

def main():
    imgs = sorted(glob.glob(os.path.join(DATASET_IMG_DIR, '*.png')))
    idx = 0
    while 0 <= idx < len(imgs):
        img_path = imgs[idx]
        label_path = os.path.join(DATASET_LABEL_DIR, os.path.basename(img_path).replace('.png', '.txt'))
        img = cv2.imread(img_path)
        if img is None:
            print(f'Erro ao abrir {img_path}')
            idx += 1
            continue
        img = draw_boxes(img, label_path)
        cv2.imshow('YOLO Annotator Viewer', img)
        print(f'Exibindo: {img_path} | Anotação: {label_path}')
        print('n: próximo | p: anterior | q: sair')
        key = cv2.waitKey(0)
        if key == ord('n'):
            idx += 1
        elif key == ord('p'):
            idx -= 1
        elif key == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
