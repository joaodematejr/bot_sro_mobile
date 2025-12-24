import cv2
import os
import time

PRINTS_DIR = "prints_yolo"
LOG_FILE = "log_bot.txt"

def ler_logs():
    if not os.path.exists(LOG_FILE):
        return "(Sem logs ainda)"
    with open(LOG_FILE, "r") as f:
        linhas = f.readlines()
    return "".join(linhas[-10:])  # Últimas 10 linhas

def main():
    print("Visualização ao vivo das imagens do prints_yolo + logs abaixo. Pressione Q para sair.")
    imagens = sorted([f for f in os.listdir(PRINTS_DIR) if f.endswith(".png") or f.endswith(".jpg")])
    idx = 0
    while True:
        novas = sorted([f for f in os.listdir(PRINTS_DIR) if f.endswith(".png") or f.endswith(".jpg")])
        if len(novas) > len(imagens):
            imagens = novas
            idx = len(imagens) - 1
        if imagens:
            img_path = os.path.join(PRINTS_DIR, imagens[idx])
            img = cv2.imread(img_path)
            if img is not None:
                cv2.imshow("YOLO Visualização ao Vivo", img)
        logs = ler_logs()
        print("\n--- LOGS ---")
        print(logs)
        if cv2.waitKey(500) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()