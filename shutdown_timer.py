import os
import time
import threading
import tkinter as tk
from tkinter import messagebox
import json
import os.path
from datetime import datetime, timedelta

languages = {'Turkish': 'Turkish', 'English': 'English'}
current_language = languages['Turkish']

turkish_texts = {
    "title": "Bilgisayar Kapatma Zamanlayıcısı",
    "question": "Kaç dakika sonra bilgisayarın kapanmasını istiyorsunuz?",
    "custom_time": "Kendi süre girişiniz (dakika):",
    "start": "Geri Sayımı Başlat",
    "cancel": "Kapatmayı İptal Et",
    "shutting_down": "Bilgisayar kapanıyor...",
    "shutdown_cancelled": "Bilgisayarı kapatma işlemi iptal edildi.",
    "error": "Hata",
    "invalid_input": "Lütfen geçerli bir sayı girin.",
    "countdown": "Kapanmaya kalan süre:",
    "estimated_shutdown": "Tahmini kapanma zamanı:",
    "warning_30_seconds": "30 saniye kaldı!",
    "language_change": "Change Language",
}

english_texts = {
    "title": "Computer Shutdown Timer",
    "question": "How many minutes until the computer shuts down?",
    "custom_time": "Enter your custom time (minutes):",
    "start": "Start Countdown",
    "cancel": "Cancel Shutdown",
    "shutting_down": "The computer is shutting down...",
    "shutdown_cancelled": "Shutdown operation has been cancelled.",
    "error": "Error",
    "invalid_input": "Please enter a valid number.",
    "countdown": "Time remaining until shutdown:",
    "estimated_shutdown": "Estimated shutdown time:",
    "warning_30_seconds": "30 seconds remaining!",
    "language_change": "Dil Değiştir",
}

texts = turkish_texts

def save_language(language):
    with open("settings.json", "w") as settings_file:
        json.dump({"language": language}, settings_file)

def load_language():
    global texts, current_language
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as settings_file:
            settings = json.load(settings_file)
            current_language = settings.get("language", languages['Turkish'])
            if current_language == languages['Turkish']:
                texts = turkish_texts
            elif current_language == languages['English']:
                texts = english_texts

def change_language():
    global texts, current_language
    language_selection = tk.Toplevel()
    language_selection.title(texts["language_change"])
    language_selection.geometry("400x200")
    language_selection.configure(bg="#f0f0f0")

    def set_language(language):
        global texts, current_language
        if language == languages['Turkish']:
            texts = turkish_texts
        elif language == languages['English']:
            texts = english_texts
        current_language = language
        save_language(language)
        language_selection.destroy()
        root.title(texts["title"])
        update_interface_texts()

    tk.Label(language_selection, text="Dil Seçiniz / Select Language", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=20)
    tk.Button(language_selection, text="Türkçe", command=lambda: set_language(languages['Turkish']), font=("Helvetica", 12), bg="#2196f3", fg="white").pack(pady=10)
    tk.Button(language_selection, text="English", command=lambda: set_language(languages['English']), font=("Helvetica", 12), bg="#2196f3", fg="white").pack(pady=10)

def update_interface_texts():
    title_label.config(text=texts["question"])
    custom_time_label.config(text=texts["custom_time"])
    start_button.config(text=texts["start"])
    cancel_button.config(text=texts["cancel"])
    settings_menu.entryconfig(0, label=texts["language_change"])

def shutdown():
    os.system('shutdown /s /t 1')

def show_30_seconds_warning():
    # Yeni bir top-level uyarı penceresi oluşturalım.
    warning_window = tk.Toplevel(root)
    warning_window.title(texts["title"])
    warning_window.geometry("300x100")
    warning_window.configure(bg="#f0f0f0")
    tk.Label(warning_window, text=texts["warning_30_seconds"], font=("Helvetica", 12, "bold"), bg="#f0f0f0").pack(pady=20)
    # Bu pencere modal değil, o yüzden geri sayım devam eder.
    # İsterseniz belirli bir süre sonra otomatik kapatabilirsiniz:
    warning_window.after(5000, warning_window.destroy) # 5 saniye sonra kapatır

def countdown_timer():
    global countdown, countdown_label, estimated_time_label, root
    estimated_shutdown_time = datetime.now() + timedelta(seconds=countdown)
    estimated_time_str = estimated_shutdown_time.strftime("%H:%M:%S")
    estimated_time_label.config(text=f"{texts['estimated_shutdown']} {estimated_time_str}")
    while countdown > 0:
        mins, secs = divmod(countdown, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        countdown_label.config(text=f"{texts['countdown']} {timer}")
        # 30 saniye kaldığında messagebox yerine Toplevel kullan
        if countdown == 30:
            # Uyarı ver, geri sayım devam etsin
            show_30_seconds_warning()
        root.update()
        time.sleep(1)
        countdown -= 1
    if countdown == 0:
        shutdown()

def cancel_shutdown():
    global countdown
    countdown = -1
    messagebox.showinfo(texts["title"], texts["shutdown_cancelled"])
    root.destroy()

def start_countdown(minutes=None):
    global countdown, countdown_label, estimated_time_label, root
    try:
        if minutes is None:
            minutes = int(minutes_entry.get())
        countdown = minutes * 60
        countdown_label.pack(pady=10)
        estimated_time_label.pack(pady=5)
        cancel_button.pack(pady=10)
        start_button.config(state=tk.DISABLED)
        countdown_thread = threading.Thread(target=countdown_timer)
        countdown_thread.start()
    except ValueError:
        messagebox.showerror(texts["error"], texts["invalid_input"])

def create_main_interface():
    global root, countdown_label, estimated_time_label, cancel_button, start_button, minutes_entry, title_label, custom_time_label, settings_menu
    root = tk.Tk()
    root.title(texts["title"])
    root.geometry("800x400")
    root.configure(bg="#f0f0f0")

    menubar = tk.Menu(root)
    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(label=texts["language_change"], command=change_language)
    menubar.add_cascade(label=texts["language_change"], menu=settings_menu)
    root.config(menu=menubar)

    title_label = tk.Label(root, text=texts["question"], font=("Helvetica", 14, "bold"), bg="#f0f0f0", fg="#333333")
    title_label.pack(pady=15)

    def create_time_button(text, minutes):
        return tk.Button(root, text=text, command=lambda: start_countdown(minutes), font=("Helvetica", 12), bg="#2196f3", fg="white", activebackground="#1976d2", relief="raised")

    time_buttons_frame = tk.Frame(root, bg="#f0f0f0")
    time_buttons_frame.pack(pady=10)

    buttons = [
        ("5 dk", 5), ("10 dk", 10), ("15 dk", 15), ("20 dk", 20), ("30 dk", 30),
        ("1 saat", 60), ("2 saat", 120), ("3 saat", 180), ("4 saat", 240), ("5 saat", 300), ("6 saat", 360)
    ]

    for text, minutes in buttons:
        button = create_time_button(text, minutes)
        button.pack(side=tk.LEFT, padx=5, pady=5, in_=time_buttons_frame)

    custom_time_frame = tk.Frame(root, bg="#f0f0f0")
    custom_time_frame.pack(pady=15)

    custom_time_label = tk.Label(custom_time_frame, text=texts["custom_time"], font=("Helvetica", 12), bg="#f0f0f0", fg="#333333")
    custom_time_label.pack(side=tk.LEFT, padx=5)

    minutes_entry = tk.Entry(custom_time_frame, font=("Helvetica", 14), width=5, justify="center")
    minutes_entry.pack(side=tk.LEFT, padx=5)

    start_button = tk.Button(root, text=texts["start"], command=start_countdown, font=("Helvetica", 12, "bold"), bg="#4caf50", fg="white", activebackground="#45a049", relief="raised")
    start_button.pack(pady=10)

    cancel_button = tk.Button(root, text=texts["cancel"], command=cancel_shutdown, font=("Helvetica", 12, "bold"), bg="#f44336", fg="white", activebackground="#e53935", relief="raised")
    countdown_label = tk.Label(root, text="", font=("Helvetica", 14), fg="#1e88e5", bg="#f0f0f0")
    estimated_time_label = tk.Label(root, text="", font=("Helvetica", 12), fg="#555555", bg="#f0f0f0")

    root.mainloop()

load_language()
create_main_interface()
