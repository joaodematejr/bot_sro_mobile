import cv2
import numpy as np

# Caminho para a imagem de referência (template)
template_path = 'imagem_treinamento.png'  # Altere para o nome correto do arquivo
def crop_image(input_path, output_path, x=230, y=250, w=200, h=200):
    """
    Faz o crop de uma imagem nas coordenadas e dimensões especificadas.
    input_path: caminho da imagem de entrada
    output_path: caminho para salvar a imagem cortada
    x, y: coordenadas do canto superior esquerdo
    w, h: largura e altura do recorte
    """
    img = cv2.imread(input_path)
    if img is None:
        print(f"Erro ao abrir {input_path}")
        return
    crop = img[y:y+h, x:x+w]
    cv2.imwrite(output_path, crop)
    print(f"Imagem cortada salva em {output_path}")

# Carrega a imagem de referência (template)
template = cv2.imread(template_path, cv2.IMREAD_COLOR)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
w, h = template_gray.shape[::-1]

# Carrega a imagem onde será feita a busca
img_path = 'imagem_treinamento.png'  # Altere para o nome correto do arquivo alvo
img = cv2.imread(img_path, cv2.IMREAD_COLOR)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Aplica o template matching
res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
threshold = 0.8  # Ajuste o limiar conforme necessário
loc = np.where(res >= threshold)

# Desenha retângulos onde encontrou o template
for pt in zip(*loc[::-1]):
    cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)

# Mostra o resultado
cv2.imshow('Resultado', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Chamada da função para fazer o crop
# Crop mini Map
crop_image('imagem_treinamento.png', 'mini_map.png', x=130, y=150, w=200, h=200)
# Crop mini Map
crop_image('imagem_treinamento.png', 'localizacao.png', x=180, y=180, w=100, h=25)
# Crop vida
crop_image('imagem_treinamento.png', 'vida.png', x=190, y=30, w=120, h=50)
# Crop XP
crop_image('imagem_treinamento.png', 'xp.png', x=30, y=900, w=140, h=125)