import cv2
import numpy as np

def detectar_setor_com_mais_vermelhos(img_path, grid_size=3, debug=False):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Erro ao abrir {img_path}")
        return None
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, (0,120,120), (10,255,255))
    mask2 = cv2.inRange(hsv, (160,120,120), (180,255,255))
    mask = cv2.bitwise_or(mask1, mask2)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = img.shape[:2]
    grid = np.zeros((grid_size, grid_size), dtype=int)
    for cnt in contours:
        M = cv2.moments(cnt)
        if M['m00'] == 0:
            continue
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        gx = min(cx * grid_size // w, grid_size-1)
        gy = min(cy * grid_size // h, grid_size-1)
        grid[gy, gx] += 1
    max_count = np.max(grid)
    hotspot = np.unravel_index(np.argmax(grid), grid.shape)
    print(f"Setor com mais pontos vermelhos: {hotspot} ({max_count} pontos)")
    print("Mapa de calor dos setores:\n", grid)
    return hotspot, grid
