import os
import time
import threading
import tkinter as tk
from tkinter import messagebox
import json
import os.path
from datetime import datetime, timedelta

# Dil seçenekleri / Language Options
# Dictionary to store available languages
languages = {'Turkish': 'Turkish', 'English': 'English'}
current_language = languages['Turkish']  # Set default language to Turkish

# Dil sözlükleri / Language Dictionaries
# Texts for Turkish interface
# This dictionary contains all the UI texts in Turkish
# Each key represents a different UI element or message

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

# Texts for English interface
# This dictionary contains all the UI texts in English
# Each key represents a different UI element or message
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

texts = turkish_texts  # Set default language texts to Turkish

# Dil seçim ayarlarını kaydetme / Save language settings
# This function saves the selected language to a JSON file
# so that the application remembers the user's choice.
def save_language(language):
    with open("settings.json", "w") as settings_file:
        json.dump({"language": language}, settings_file)

# Dil ayarlarını yükleme / Load language settings
# This function loads the language setting from a JSON file
# If the file exists, it updates the global 'texts' dictionary with the appropriate language.
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

# Dil Seçimi Penceresi / Language Selection Window
# This function creates a new window where the user can choose the application language.
def change_language():
    global texts, current_language
    language_selection = tk.Toplevel()  # Create a new window
    language_selection.title(texts["language_change"])
    language_selection.geometry("400x200")
    language_selection.configure(bg="#f0f0f0")

    # Nested function to set the chosen language and update UI accordingly
    def set_language(language):
        global texts, current_language
        if language == languages['Turkish']:
            texts = turkish_texts
        elif language == languages['English']:
            texts = english_texts
        current_language = language
        save_language(language)  # Save the language setting to file
        language_selection.destroy()  # Close the language selection window
        root.title(texts["title"])  # Update window title
        update_interface_texts()  # Update all UI texts

    # Buttons to choose Turkish or English
    tk.Label(language_selection, text="Dil Seçiniz / Select Language", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=20)
    tk.Button(language_selection, text="Türkçe", command=lambda: set_language(languages['Turkish']), font=("Helvetica", 12), bg="#2196f3", fg="white").pack(pady=10)
    tk.Button(language_selection, text="English", command=lambda: set_language(languages['English']), font=("Helvetica", 12), bg="#2196f3", fg="white").pack(pady=10)

# Arayüzdeki metinleri güncelleme / Update interface texts
# This function updates all the interface texts to match the selected language.
def update_interface_texts():
    title_label.config(text=texts["question"])
    custom_time_label.config(text=texts["custom_time"])
    start_button.config(text=texts["start"])
    cancel_button.config(text=texts["cancel"])
    settings_menu.entryconfig(0, label=texts["language_change"])

# Bilgisayarı kapatma fonksiyonu / Function to Shutdown the Computer
# This function shuts down the computer immediately.
def shutdown():
    # Bilgisayar doğrudan kapanacak, kullanıcı etkileşimi olmadan
    os.system('shutdown /s /t 1')

# Geri sayımı başlatan fonksiyon / Function to Start the Countdown
# This function handles the countdown logic and updates the UI every second.
def countdown_timer():
    global countdown, countdown_label, estimated_time_label, root
    estimated_shutdown_time = datetime.now() + timedelta(seconds=countdown)  # Calculate the estimated shutdown time
    estimated_time_str = estimated_shutdown_time.strftime("%H:%M:%S")  # Format the shutdown time
    estimated_time_label.config(text=f"{texts['estimated_shutdown']} {estimated_time_str}")  # Display estimated shutdown time
    while countdown > 0:
        mins, secs = divmod(countdown, 60)  # Convert seconds into minutes and seconds
        timer = '{:02d}:{:02d}'.format(mins, secs)  # Format the countdown timer
        countdown_label.config(text=f"{texts['countdown']} {timer}")  # Update countdown label
        if countdown == 30:
            messagebox.showinfo(texts["title"], texts["warning_30_seconds"])  # Show warning when 30 seconds are left
        root.update()  # Update the root window
        time.sleep(1)  # Wait for 1 second
        countdown -= 1  # Decrease countdown by 1 second
    if countdown == 0:
        shutdown()  # Shutdown the computer when countdown reaches zero

# Geri sayımı iptal etme fonksiyonu / Function to Cancel the Countdown
# This function cancels the shutdown countdown and closes the application window.
def cancel_shutdown():
    global countdown
    countdown = -1  # Set countdown to -1 to stop the countdown loop
    messagebox.showinfo(texts["title"], texts["shutdown_cancelled"])  # Display cancellation message
    root.destroy()  # Close the application window

# Kullanıcıdan kaç dakika sonra kapatılacağını öğrenen fonksiyon / Function to Get User Input for Shutdown Time
# This function gets the user input for countdown time and starts the countdown timer in a separate thread.
def start_countdown(minutes=None):
    global countdown, countdown_label, estimated_time_label, root
    try:
        if minutes is None:
            minutes = int(minutes_entry.get())  # Get the minutes from the entry field
        countdown = minutes * 60  # Convert minutes to seconds
        countdown_label.pack(pady=10)  # Display the countdown label
        estimated_time_label.pack(pady=5)  # Display the estimated shutdown time label
        cancel_button.pack(pady=10)  # Display the cancel button
        start_button.config(state=tk.DISABLED)  # Disable the start button
        countdown_thread = threading.Thread(target=countdown_timer)  # Create a new thread for the countdown
        countdown_thread.start()  # Start the countdown thread
    except ValueError:
        messagebox.showerror(texts["error"], texts["invalid_input"])  # Show error message if input is invalid

# Ana arayüzü oluşturma fonksiyonu / Function to Create Main Interface
# This function creates the main interface of the application.
def create_main_interface():
    global root, countdown_label, estimated_time_label, cancel_button, start_button, minutes_entry, title_label, custom_time_label, settings_menu
    root = tk.Tk()  # Create the main window
    root.title(texts["title"])  # Set window title
    root.geometry("800x400")  # Set window size
    root.configure(bg="#f0f0f0")  # Set background color

    # Dil Değiştir menüsü / Change Language menu
    # Create a menu for changing the language
    menubar = tk.Menu(root)
    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(label=texts["language_change"], command=change_language)  # Add a command to change language
    menubar.add_cascade(label=texts["language_change"], menu=settings_menu)  # Add the language menu to the menubar
    root.config(menu=menubar)  # Set the menu for the root window

    # Kullanıcı arayüzü elemanları / User Interface Elements
    # Create the main user interface elements
    title_label = tk.Label(root, text=texts["question"], font=("Helvetica", 14, "bold"), bg="#f0f0f0", fg="#333333")
    title_label.pack(pady=15)  # Add the main question label

    # Varsayılan süre butonları / Default Time Buttons
    # Create default buttons for predefined times
    def create_time_button(text, minutes):
        return tk.Button(root, text=text, command=lambda: start_countdown(minutes), font=("Helvetica", 12), bg="#2196f3", fg="white", activebackground="#1976d2", relief="raised")

    time_buttons_frame = tk.Frame(root, bg="#f0f0f0")
    time_buttons_frame.pack(pady=10)

    # Predefined buttons with different shutdown times
    buttons = [
        ("5 dk", 5), ("10 dk", 10), ("15 dk", 15), ("20 dk", 20), ("30 dk", 30),
        ("1 saat", 60), ("2 saat", 120), ("3 saat", 180), ("4 saat", 240), ("5 saat", 300), ("6 saat", 360)
    ]

    # Create and add each predefined button to the frame
    for text, minutes in buttons:
        button = create_time_button(text, minutes)
        button.pack(side=tk.LEFT, padx=5, pady=5, in_=time_buttons_frame)

    # Kendi süre giriş alanı / Custom Time Entry
    # Create custom time entry field
    custom_time_frame = tk.Frame(root, bg="#f0f0f0")
    custom_time_frame.pack(pady=15)

    custom_time_label = tk.Label(custom_time_frame, text=texts["custom_time"], font=("Helvetica", 12), bg="#f0f0f0", fg="#333333")
    custom_time_label.pack(side=tk.LEFT, padx=5)

    minutes_entry = tk.Entry(custom_time_frame, font=("Helvetica", 14), width=5, justify="center")
    minutes_entry.pack(side=tk.LEFT, padx=5)

    # Start button to initiate the countdown
    start_button = tk.Button(root, text=texts["start"], command=start_countdown, font=("Helvetica", 12, "bold"), bg="#4caf50", fg="white", activebackground="#45a049", relief="raised")
    start_button.pack(pady=10)

    # Cancel button to stop the countdown
    cancel_button = tk.Button(root, text=texts["cancel"], command=cancel_shutdown, font=("Helvetica", 12, "bold"), bg="#f44336", fg="white", activebackground="#e53935", relief="raised")
    countdown_label = tk.Label(root, text="", font=("Helvetica", 14), fg="#1e88e5", bg="#f0f0f0")
    estimated_time_label = tk.Label(root, text="", font=("Helvetica", 12), fg="#555555", bg="#f0f0f0")

    # Tkinter ana döngüsünü başlat / Start Tkinter Main Loop
    root.mainloop()

# Dil ayarlarını yükle ve ana arayüzü oluştur / Load language settings and create main interface
load_language()
create_main_interface()
