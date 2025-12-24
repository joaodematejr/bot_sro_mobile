import cv2
import os
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk

PRINTS_DIR = "prints_yolo"
LOG_FILE = "log_bot.txt"
REFRESH_MS = 500

class VisualBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Visual - Última Detecção + Logs")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

        # Frame para imagem
        self.img_label = tk.Label(self.root)
        self.img_label.pack(pady=10)

        # Área de logs
        self.log_area = scrolledtext.ScrolledText(self.root, height=12, width=110, font=("Consolas", 10))
        self.log_area.pack(pady=5)
        self.log_area.config(state=tk.DISABLED)

        self.last_img = None
        self.last_log = ""
        self.update_content()

    def update_content(self):
        # Atualiza imagem
        img_path = self.get_latest_image()
        if img_path:
            img = Image.open(img_path)
            img = img.resize((880, 440))
            self.last_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.last_img)
        # Atualiza logs
        logs = self.get_latest_logs()
        if logs != self.last_log:
            self.log_area.config(state=tk.NORMAL)
            self.log_area.delete(1.0, tk.END)
            self.log_area.insert(tk.END, logs)
            self.log_area.config(state=tk.DISABLED)
            self.last_log = logs
        self.root.after(REFRESH_MS, self.update_content)

    def get_latest_image(self):
        imgs = [f for f in os.listdir(PRINTS_DIR) if f.endswith('.png') or f.endswith('.jpg')]
        if not imgs:
            return None
        imgs.sort(key=lambda x: os.path.getmtime(os.path.join(PRINTS_DIR, x)), reverse=True)
        return os.path.join(PRINTS_DIR, imgs[0])

    def get_latest_logs(self):
        if not os.path.exists(LOG_FILE):
            return "(Sem logs ainda)"
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            linhas = f.readlines()
        return "".join(linhas[-20:])  # Últimas 20 linhas

def main():
    root = tk.Tk()
    app = VisualBotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
