import argparse
import requests
import time
import psycopg2
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StackOverflow Search")

        # Deshabilitar la opción de maximizar
        self.resizable(False, False)

        self.api_key_label = tk.Label(self, text="Clave de la API de StackExchange:")
        self.api_key_entry = tk.Entry(self, width=35)
        self.search_title_label = tk.Label(self, text="Título de búsqueda en StackOverflow:")
        self.search_title_entry = tk.Entry(self, width=35)
        self.upper_date_label = tk.Label(self, text="Fecha superior para filtrar las discusiones (DD-MM-YYYY):")
        self.upper_date_entry = tk.Entry(self, width=35)
        self.database_label = tk.Label(self, text="Nombre de la base de datos:")
        self.database_entry = tk.Entry(self, width=35)
        self.user_label = tk.Label(self, text="Usuario de la base de datos:")
        self.user_entry = tk.Entry(self, width=35)
        self.password_label = tk.Label(self, text="Contraseña de la base de datos:")
        self.password_entry = tk.Entry(self, show="*", width=35)
        self.search_button = tk.Button(self, text="Buscar y Guardar", command=self.start_search_and_save)
        self.progress_bar = ttk.Progressbar(self, length=200, mode='indeterminate')
        self.result_label = tk.Label(self, text="",width=50, wraplength=300, justify=tk.LEFT)


        self.api_key_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=5)
        self.search_title_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.search_title_entry.grid(row=1, column=1, padx=10, pady=5)
        self.upper_date_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.upper_date_entry.grid(row=2, column=1, padx=10, pady=5)
        self.database_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.database_entry.grid(row=3, column=1, padx=10, pady=5)
        self.user_label.grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        self.user_entry.grid(row=4, column=1, padx=10, pady=5)
        self.password_label.grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        self.password_entry.grid(row=5, column=1, padx=10, pady=5)
        self.search_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        self.result_label.grid(row=7, column=0, columnspan=2, padx=10,pady=10)

        # Variable de control para determinar si el proceso de búsqueda y guardado está en marcha
        self.is_searching = False 

    def start_search_and_save(self):
        if self.is_searching:
            messagebox.showinfo("Advertencia", "El proceso de búsqueda y guardado ya está en marcha.")
            return

        # Obtener los valores de los campos de entrada
        key = self.api_key_entry.get()
        intitle = self.search_title_entry.get()
        fecha_superior = self.upper_date_entry.get()
        database = self.database_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()

        # Verificar si hay campos vacíos
        if not key or not intitle or not fecha_superior or not database or not user or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        # Marcar el proceso de búsqueda y guardado como activo
        self.is_searching = True

        # Deshabilitar el botón mientras se realiza la búsqueda y el guardado
        self.search_button.config(state=tk.DISABLED)

        # Crear conn_params para la conexión a la base de datos
        conn_params = {
            "host": "localhost",
            "database": database,
            "user": user,
            "password": password
        }

        # Iniciar la búsqueda y el guardado en un hilo separado para evitar bloquear la interfaz de usuario
        t = threading.Thread(target=self.perform_search_and_save, args=(key, intitle, fecha_superior, conn_params))
        t.start()

    def perform_search_and_save(self, key, intitle, fecha_superior, conn_params):
        # Crear ProgressBar antes de iniciar el proceso de búsqueda y guardado
        self.progress_bar.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
        self.progress_bar.start()

        try:
            # Establish connection with the database
            conn = psycopg2.connect(**conn_params)
            cursor = conn.cursor()

            url = "https://api.stackexchange.com/2.3/search"

            params = {
                "key": key,
                "site": "stackoverflow",
                "intitle": intitle,
            }

            questions = []

            page = 1
            while True:
                params["page"] = page
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    questions.extend(data["items"])
                    has_more = data["has_more"]
                    if not has_more:
                        break
                    page += 1
                    if page % 30 == 0:
                        print("waiting for...")
                        time.sleep(1)  # Wait for a second after 30 requests
                else:
                    print("Error when trying HTTP request:", response.status_code)
                    break

            # Query the existing discussion IDs in the database
            select_query = "SELECT id_discussion FROM STACK_QUERY"
            cursor.execute(select_query)
            existing_ids = set(row[0] for row in cursor.fetchall())

            inserted_count = 0
            neg_votes_omitted_count = 0
            existing_omitted_count = 0

            # Get the argument upper date and convert to a datatime object
            fecha_superior = datetime.strptime(fecha_superior, '%d-%m-%Y')

            for question in questions:
                id_discussion = question["question_id"]

                # Check if discussion ID already exists in the database
                if id_discussion in existing_ids:
                    existing_omitted_count += 1
                    continue

                creation_date = datetime.fromtimestamp(question["creation_date"])

                # Check if the creation date is between given range
                if datetime(2014, 1, 14) <= creation_date <= fecha_superior:
                    title = question["title"]
                    link = question["link"]
                    score = question["score"]
                    answer_count = question["answer_count"]
                    view_count = question["view_count"]
                    tags = ", ".join(question["tags"])

                    if score >= 0:
                        insert_query = "INSERT INTO STACK_QUERY(id_discussion, title, link, score, answer_count, view_count, creation_date, tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        cursor.execute(insert_query, (id_discussion, title, link, score, answer_count, view_count, creation_date, tags))
                        inserted_count += 1
                        existing_ids.add(id_discussion)
                    else:
                        neg_votes_omitted_count += 1
                else:
                    # The question is not inside given range, it is omitted
                    existing_omitted_count += 1

            # Confirm the changes in the database
            conn.commit()

            # Close the connection with the database
            cursor.close()
            conn.close()

            total_questions = len(questions)
            result_str = f"Total discussions found: {total_questions}\n" \
                         f"Total discussions inserted in DB: {inserted_count}\n" \
                         f"Total discussions omitted for negatives votes: {neg_votes_omitted_count}\n" \
                         f"Total discussions omitted because already exists in DB: {existing_omitted_count}\n"

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al procesar la búsqueda y el guardado: {e}")
        finally:
            # Marcar el proceso de búsqueda y guardado como inactivo
            self.is_searching = False
            
            # Habilitar el botón después de finalizar la búsqueda y el guardado
            self.search_button.config(state=tk.NORMAL)

            # Detener y ocultar el ProgressBar
            self.progress_bar.stop()
            self.progress_bar.grid_forget()
            self.result_label.config(text=result_str)
            messagebox.showinfo("Finalizado", "La búsqueda y el guardado de datos se han completado exitosamente.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()