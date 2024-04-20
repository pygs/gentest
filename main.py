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
def get_subject_id(conn, subject_name):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subjects WHERE name = %s", (subject_name,))
        subject_id = cursor.fetchone()[0]
        cursor.close()
        return subject_id
    except psycopg2.Error as e:
        messagebox.showerror("Błąd", "Błąd podczas pobierania ID przedmiotu:\n{}".format(e))
        return None
    
def get_topic_id(conn, topic_name):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM topics WHERE name = %s", (topic_name,))
        subject_id = cursor.fetchone()[0]
        cursor.close()
        return subject_id
    except psycopg2.Error as e:
        messagebox.showerror("Błąd", "Błąd podczas pobierania ID tematu:\n{}".format(e))
        return None
    


def open_main_window(conn):
    main_window = tk.Tk()
    main_window.title("Główne okno")
    main_window.geometry("600x450")

    subjects = get_subjects(conn)
    global topic_value

    subject_label = tk.Label(main_window, text="Wybierz przedmiot:")
    subject_label.grid(row=0, column=0)
    subject_value = tk.StringVar(main_window)
    subject_value.set(subjects[0]) if subjects else subject_value.set("Brak przedmiotów")

    subject_box = tk.OptionMenu(main_window, subject_value, *subjects)
    subject_box.grid(row=0, column=1)

    subject_plus_button = tk.Button(main_window, text="+", command=lambda: open_add_subject_window(conn, subject_value, subject_box))
    subject_plus_button.grid(row=0, column=2)
    
    subject_value.trace_add("write", lambda name, index, mode, sv=subject_value: on_subjectbox_select(conn, sv.get()))
    subject_value.trace_add("write", lambda *args: refresh_topicbox(conn, topic_box, subject_value.get()))
    topics = get_topics(conn, subject_value.get())
    
    
    
    
    topic_label = tk.Label(main_window, text="Wybierz temat:")
    topic_label.grid(row=1, column=0)
    topic_value = tk.StringVar(main_window)
    topic_value.set(topics[0]) if topics else topic_value.set("Brak tematów")

    topic_box = tk.OptionMenu(main_window, topic_value, *topics)
    topic_box.grid(row=1, column=1)

    topic_plus_button = tk.Button(main_window, text="+", command=lambda: open_add_topic_window(conn, topic_value, topic_box, subject_value.get()))
    topic_plus_button.grid(row=1, column=2)

    topic_value.trace_add("write", lambda name, index, mode, tv=topic_value: on_topicbox_select(conn, tv.get()))

    question_label = tk.Label(main_window, text="Dodaj pytanie: ")
    question_label.grid(row=2, column=0)
    question_plus_button = tk.Button(main_window, text="+", command=lambda: open_add_question_window(conn, topic_value.get()))
    question_plus_button.grid(row=2, column=1)

    main_window.mainloop()

def refresh_topicbox(conn, combo_box, current_subject):
    # Usunięcie istniejących elementów z comboboxa
    combo_box['menu'].delete(0, 'end')

    # Pobranie zaktualizowanej listy przedmiotów
    topics = get_topics(conn, current_subject)

    # Dodanie zaktualizowanej listy przedmiotów do comboboxa
    
    for topic in topics:
        combo_box['menu'].add_command(label=topic, command=lambda value=topic: topic_value.set(value))

def on_subjectbox_select(conn, selected_subject):
    subject_id = get_subject_id(conn, selected_subject)
    if subject_id is not None:
        print("Wybrano przedmiot o ID:", subject_id)
        return subject_id
    else:
        print("Nie można pobrać ID wybranego przedmiotu.")

def on_topicbox_select(conn, selected_topic):
    topic_id = get_topic_id(conn, selected_topic)
    if topic_id is not None:
        print("Wybrano temat o ID:", topic_id)
        return topic_id
    else:
        print("Nie można pobrać ID wybranego tematu.")

def open_add_subject_window(conn, subject_value, subject_box):
    add_window = tk.Toplevel()
    add_window.title("Dodaj przedmiot")
    add_window.geometry("200x100")

    tk.Label(add_window, text="Nazwa przedmiotu:").pack()
    subject_name_entry = tk.Entry(add_window)
    subject_name_entry.pack()

    add_button = tk.Button(add_window, text="Dodaj", command=lambda: add_subject(conn, subject_name_entry.get(), subject_value, subject_box, add_window))
    add_button.pack()

def open_add_topic_window(conn, topic_value, topic_box, current_subject):
    add_window = tk.Toplevel()
    add_window.title("Dodaj temat")
    add_window.geometry("200x100")

    tk.Label(add_window, text="Nazwa tematu:").pack()
    topic_name_entry = tk.Entry(add_window)
    topic_name_entry.pack()

    add_button = tk.Button(add_window, text="Dodaj", command=lambda: add_topic(conn, topic_name_entry.get(), topic_value, topic_box, add_window, current_subject))
    add_button.pack()

def open_add_question_window(conn, current_topic):
    add_window = tk.Toplevel()
    add_window.title("Dodaj pytanie")
    add_window.geometry("300x200")

    tk.Label(add_window, text="Pytanie:").grid(row=0, column=0)
    question_name_entry = tk.Entry(add_window)
    question_name_entry.grid(row=0, column=1)

    tk.Label(add_window, text="Odpowiedź poprawna:").grid(row=1, column=0)
    answer_1_entry = tk.Entry(add_window)
    answer_1_entry.grid(row=1, column=1)

    tk.Label(add_window, text="Odpowiedź 1:").grid(row=2, column=0)
    answer_2_entry = tk.Entry(add_window)
    answer_2_entry.grid(row=2, column=1)

    tk.Label(add_window, text="Odpowiedź 2:").grid(row=3, column=0)
    answer_3_entry = tk.Entry(add_window)
    answer_3_entry.grid(row=3, column=1)

    tk.Label(add_window, text="Odpowiedź 3:").grid(row=4, column=0)
    answer_4_entry = tk.Entry(add_window)
    answer_4_entry.grid(row=4, column=1)


    add_button = tk.Button(add_window, text="Dodaj", command=lambda: add_question(conn, question_name_entry.get(), answer_1_entry.get(), answer_2_entry.get(), answer_3_entry.get(), answer_4_entry.get(), add_window, current_topic))
    add_button.grid(row=5, column=0)

def add_subject(conn, subject_name, subject_value, subject_box, add_window):
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
        subject_box['menu'].delete(0, 'end')  # Usunięcie poprzednich wartości
        for subject in subjects:
            subject_box['menu'].add_command(label=subject, command=tk._setit(subject_value, subject))

        add_window.destroy()

    except psycopg2.Error as e:
        messagebox.showerror("Błąd", "Błąd podczas dodawania przedmiotu:\n{}".format(e))

def add_topic(conn, topic_name, topic_value, topic_box, add_window, current_subject):
    if not topic_name:
        messagebox.showerror("Błąd", "Nazwa tematu nie może być pusta.")
        return
    
    try:
        cursor = conn.cursor()
        subject_id = get_subject_id(conn, current_subject)
        cursor.execute("INSERT INTO topics (name, subject_id) VALUES (%s, %s)", (topic_name, subject_id))
        conn.commit()
        cursor.close()
        messagebox.showinfo("Sukces", "Temat dodany pomyślnie!")

        topics = get_topics(conn, current_subject)
        topic_box['menu'].delete(0, 'end')  # Usunięcie poprzednich wartości
        for topic in topics:
            topic_box['menu'].add_command(label=topic, command=tk._setit(topic_value, topic))

        add_window.destroy()

    except psycopg2.Error as e:
        messagebox.showerror("Błąd", "Błąd podczas dodawania tematu:\n{}".format(e))

def add_question(conn, question_name, a1, a2, a3, a4, add_window, current_topic):
    if not question_name:
        messagebox.showerror("Błąd", "Nazwa pytania nie może być pusta.")
        return
    if not a1 or a2 or a3 or a4:
        messagebox.showerror("Błąd", "Odpowiedź nie może być pusta.")
        return
    
    try:
        cursor = conn.cursor()
        topic_id = get_topic_id(conn, current_topic)
        cursor.execute("INSERT INTO qa (topic_id, question, answer_1, answer_2, answer_3, answer_4) VALUES (%s, %s, %s, %s, %s, %s)", (topic_id, question_name, a1, a2, a3, a4))
        conn.commit()
        cursor.close()
        messagebox.showinfo("Sukces", "Pytanie dodane pomyślnie!")

        add_window.destroy()

    except psycopg2.Error as e:
        messagebox.showerror("Błąd", "Błąd podczas dodawania pytania:\n{}".format(e))

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
    
def get_topics(conn, current_subject):
    try:
        subject_id = get_subject_id(conn, current_subject)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM topics WHERE subject_id = %s", (subject_id,))
        topics = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return topics
    except psycopg2.Error as e:
        messagebox.showerror("Błąd", "Błąd podczas pobierania tematów:\n{}".format(e))
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
