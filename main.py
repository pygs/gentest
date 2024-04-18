import tkinter as tk
from tkinter import messagebox
import psycopg2

def login():
    host = host_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=username,
            password=password,
            host=host,
            port="5432"
        )
        
        messagebox.showinfo("Sukces", "Zalogowano pomyślnie!")

        conn.close()
    except psycopg2.Error as e:
        messagebox.showerror("Błąd logowania", "Błąd logowania do bazy danych:\n{}".format(e))

root = tk.Tk()
root.title("Logowanie do PGAdmina")

tk.Label(root, text="Host:").pack()
host_entry = tk.Entry(root)
host_entry.pack()

tk.Label(root, text="Login:").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Hasło:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

login_button = tk.Button(root, text="Zaloguj", command=login)
login_button.pack()

root.mainloop()
