import cv2
import numpy as np
import pytesseract

def detect_location_string(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Erro ao abrir {image_path}")
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    custom_config = r'--oem 3 --psm 6'
    result = pytesseract.image_to_string(thresh, config=custom_config)
    result = result.strip().replace("\n", "").replace(" ", "")
    print(f"Localização detectada: {result}")
    return result

def crop_image(input_path, output_path, x=230, y=250, w=200, h=200):
    img = cv2.imread(input_path)
    if img is None:
        print(f"Erro ao abrir {input_path}")
        return
    crop = img[y:y+h, x:x+w]
    cv2.imwrite(output_path, crop)
    print(f"Imagem cortada salva em {output_path}")
