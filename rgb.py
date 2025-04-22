import tkinter as tk
import serial
import serial.tools.list_ports
import threading
import time
from tkinter.colorchooser import askcolor

# Arduino'yu bul
def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "CH340" in port.description:
            return port.device
    return None

arduino_port = find_arduino()
if arduino_port is None:
    print("Arduino bulunamadı. Portu elle giriniz.")
    arduino_port = input("Port ismi (örnek: COM3): ")

# Seri bağlantı
try:
    ser = serial.Serial(arduino_port, 9600, timeout=1)
    print(f"Bağlandı: {arduino_port}")
except Exception as e:
    print(f"Bağlantı hatası: {e}")
    ser = None

# Renk gönder
def send_color(r, g, b):
    if ser:
        try:
            ser.write(bytes([r, g, b]))
        except:
            print("Veri gönderilemedi.")

# RGB güncelle
def update_color(_=None):
    global rgb_mode_active
    if rgb_mode_active: return  # RGB mod açıkken slider değeri gönderme
    r = red_slider.get()
    g = green_slider.get()
    b = blue_slider.get()
    show_color(r, g, b)
    send_color(r, g, b)

def show_color(r, g, b):
    hex_color = f'#{r:02x}{g:02x}{b:02x}'
    color_display.config(bg=hex_color)
    value_label.config(text=f"R: {r} | G: {g} | B: {b}")

# Renk Seçici
def choose_color():
    color = askcolor()[0]
    if color:
        r, g, b = [int(c) for c in color]
        red_slider.set(r)
        green_slider.set(g)
        blue_slider.set(b)
        update_color()

# Otomatik RGB Mod
rgb_mode_active = False
def rgb_loop():
    global rgb_mode_active
    r = g = b = 0
    step = 5
    while rgb_mode_active:
        for r in range(0, 256, step):
            if not rgb_mode_active: return
            send_color(r, 0, 255 - r)
            show_color(r, 0, 255 - r)
            time.sleep(0.03)
        for g in range(0, 256, step):
            if not rgb_mode_active: return
            send_color(255 - g, g, 0)
            show_color(255 - g, g, 0)
            time.sleep(0.03)
        for b in range(0, 256, step):
            if not rgb_mode_active: return
            send_color(0, 255 - b, b)
            show_color(0, 255 - b, b)
            time.sleep(0.03)

def start_rgb_mode():
    global rgb_mode_active
    if not rgb_mode_active:
        rgb_mode_active = True
        threading.Thread(target=rgb_loop, daemon=True).start()

def stop_rgb_mode():
    global rgb_mode_active
    rgb_mode_active = False

# GUI
root = tk.Tk()
root.title("Arduino RGB LED Kontrol")

# GUI stilini ayarlayalım
root.configure(bg="#1e1e1e")
root.geometry("600x700")
root.resizable(False, False)

# Başlık
title_label = tk.Label(root, text="RGB LED Kontrol", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#1e1e1e")
title_label.pack(pady=30)

# Sliderlar
slider_frame = tk.Frame(root, bg="#1e1e1e")
slider_frame.pack()

red_slider = tk.Scale(slider_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Kırmızı", sliderlength=25, width=20, length=350, command=update_color, bg="#1e1e1e", fg="#ffffff", activebackground="#ff6347")
green_slider = tk.Scale(slider_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Yeşil", sliderlength=25, width=20, length=350, command=update_color, bg="#1e1e1e", fg="#ffffff", activebackground="#32cd32")
blue_slider = tk.Scale(slider_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Mavi", sliderlength=25, width=20, length=350, command=update_color, bg="#1e1e1e", fg="#ffffff", activebackground="#1e90ff")

red_slider.pack(pady=15)
green_slider.pack(pady=15)
blue_slider.pack(pady=15)

# Önizleme
color_display = tk.Label(root, text="Önizleme", width=20, height=3, bg="#000000", relief="solid", borderwidth=3, bd=0, highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff")
color_display.pack(pady=25)

value_label = tk.Label(root, text="R: 0 | G: 0 | B: 0", font=("Helvetica", 12), fg="#ffffff", bg="#1e1e1e")
value_label.pack()

# RGB Mod Butonları
btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=25)

start_btn = tk.Button(btn_frame, text="RGB Modu Başlat 🌈", command=start_rgb_mode, font=("Helvetica", 14), fg="#ffffff", bg="#4caf50", relief="flat", borderwidth=2, width=20)
start_btn.pack(side="left", padx=20, pady=10)

stop_btn = tk.Button(btn_frame, text="Durdur ✋", command=stop_rgb_mode, font=("Helvetica", 14), fg="#ffffff", bg="#f44336", relief="flat", borderwidth=2, width=20)
stop_btn.pack(side="right", padx=20, pady=10)

# Renk Seçici Butonu
color_picker_btn = tk.Button(root, text="Renk Seç", command=choose_color, font=("Helvetica", 14), fg="#ffffff", bg="#2196f3", relief="flat", borderwidth=2, width=20)
color_picker_btn.pack(pady=20)

# GUI döngüsünü başlat
root.mainloop()
