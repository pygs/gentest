import tkinter as tk
from tkinter import messagebox
import psycopg2
import json
import os

CONFIG_FILE = "config.json"

def save_config(host, username, password):
    config_data = {
        "host": host,
        "username": username,
        "password": password
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f)

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
            return config_data["host"], config_data["username"], config_data["password"]
    except FileNotFoundError:
        return "", "", ""

def delete_config():
    try:
        os.remove(CONFIG_FILE)
    except FileNotFoundError:
        pass

def login():
    host = host_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    remember = remember_var.get()
    
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=username,
            password=password,
            host=host,
            port="5432"
        )

        if remember:
            save_config(host, username, password)
        else:
            delete_config()
        
        root.destroy()
        open_main_window()  

    except psycopg2.Error as e:
        messagebox.showerror("Błąd logowania", "Błąd logowania do bazy danych:\n{}".format(e))

def open_main_window():
    main_window = tk.Tk()
    main_window.title("Główne okno")
    main_window.geometry("600x450")
    tk.Label(main_window, text="Zalogowano pomyślnie!").pack()
    main_window.mainloop()

root = tk.Tk()
root.title("Logowanie do PGAdmina")
root.geometry("400x300")

host, username, password = load_config()

tk.Label(root, text="Host:").pack()
host_entry = tk.Entry(root)
host_entry.pack()
host_entry.insert(0, host)

tk.Label(root, text="Login:").pack()
username_entry = tk.Entry(root)
username_entry.pack()
username_entry.insert(0, username)

tk.Label(root, text="Hasło:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()
password_entry.insert(0, password)

remember_var = tk.BooleanVar()
remember_checkbox = tk.Checkbutton(root, text="Zapamiętaj dane logowania", variable=remember_var)
remember_checkbox.pack()
remember_checkbox.select()

login_button = tk.Button(root, text="Zaloguj", command=login)
login_button.pack()

root.mainloop()
