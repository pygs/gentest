import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2
import json
import os

print(tk.TkVersion)
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
        open_main_window(conn)  

    except psycopg2.Error as e:
        messagebox.showerror("Błąd logowania", "Błąd logowania do bazy danych:\n{}".format(e))

def open_main_window(conn):
    main_window = tk.Tk()
    main_window.title("Główne okno")
    main_window.geometry("600x450")

    subjects = get_subjects(conn)

    combo_label = tk.Label(main_window, text="Wybierz przedmiot:")
    combo_label.grid(row=0, column=0)

    selected_value = tk.StringVar(main_window)
    selected_value.set(subjects[0]) if subjects else selected_value.set("Brak przedmiotów")

    combo_box = tk.OptionMenu(main_window, selected_value, *subjects)
    combo_box.grid(row=0, column=1)

    plus_button = tk.Button(main_window, text="+", command=lambda: open_add_subject_window(conn, selected_value, combo_box))
    plus_button.grid(row=0, column=2)
    
    main_window.mainloop()

def open_add_subject_window(conn, selected_value, combo_box):
    add_window = tk.Toplevel()
    add_window.title("Dodaj przedmiot")
    add_window.geometry("200x100")

    tk.Label(add_window, text="Nazwa przedmiotu:").pack()
    subject_name_entry = tk.Entry(add_window)
    subject_name_entry.pack()

    add_button = tk.Button(add_window, text="Dodaj", command=lambda: add_subject(conn, subject_name_entry.get(), selected_value, combo_box, add_window))
    add_button.pack()

def add_subject(conn, subject_name, selected_value, combo_box, add_window):
    if not subject_name:
        messagebox.showerror("Błąd", "Nazwa przedmiotu nie może być pusta.")
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (name) VALUES (%s)", (subject_name,))
        conn.commit()
        cursor.close()
        messagebox.showinfo("Sukces", "Przedmiot dodany pomyślnie!")

        subjects = get_subjects(conn)
        combo_box['menu'].delete(0, 'end')  # Usunięcie poprzednich wartości
        for subject in subjects:
            combo_box['menu'].add_command(label=subject, command=tk._setit(selected_value, subject))

        add_window.destroy()

    except psycopg2.Error as e:
        messagebox.showerror("Błąd", "Błąd podczas dodawania przedmiotu:\n{}".format(e))

def get_subjects(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM subjects")
        subjects = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return subjects
    except psycopg2.Error as e:
        messagebox.showerror("Błąd", "Błąd podczas pobierania przedmiotów:\n{}".format(e))
        return []

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
