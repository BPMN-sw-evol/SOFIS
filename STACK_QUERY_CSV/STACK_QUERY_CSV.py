import csv
import requests
import time
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StackOverflow Search")

        # Deshabilitar la opción de maximizar
        self.resizable(False, False)

        # Crear elementos de la interfaz
        api_key_label = tk.Label(self, text="Clave de la API de StackExchange:")
        self.api_key_entry = tk.Entry(self, width=35)  # Ancho de 40 caracteres
        search_title_label = tk.Label(self, text="Título de búsqueda en StackOverflow:")
        self.search_title_entry = tk.Entry(self, width=35)  # Ancho de 40 caracteres
        fecha_superior_label = tk.Label(self, text="Fecha superior para filtrar las discusiones (DD-MM-YYYY):")
        self.fecha_superior_entry = tk.Entry(self, width=30)  # Ancho de 20 caracteres
        search_button = tk.Button(self, text="Buscar y Guardar", command=self.search_and_save)
        self.result_label = tk.Label(self, text="", wraplength=300, justify=tk.LEFT)

        # Ubicar elementos en la ventana
        api_key_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=5)
        search_title_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.search_title_entry.grid(row=1, column=1, padx=10, pady=5)
        fecha_superior_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.fecha_superior_entry.grid(row=2, column=1, padx=10, pady=5)
        search_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10) 

    def perform_search(self):

        key = self.api_key_entry.get()
        intitle = self.search_title_entry.get()
        fecha_superior = self.fecha_superior_entry.get()

        try:
            fecha_superior = datetime.strptime(fecha_superior, '%d-%m-%Y')
        except ValueError:
            messagebox.showerror("Error", "La fecha superior debe tener el formato DD-MM-YYYY")
            return

        directory = filedialog.askdirectory(title="Seleccione el directorio para guardar los archivos CSV")

        if not directory:
            return

        url = "https://api.stackexchange.com/2.3/search"

        params = {
            "key": key,
            "site": "stackoverflow",
            "intitle": intitle,
        }

        csv_rows = []
        existing_ids = set()

        filename_with_extension = os.path.join(directory, f"{intitle}.csv")

        existing_info_count = 0  # Almacena la cantidad de información existente en el archivo
        messagebox.showinfo("Advertencia", "El proceso de búsqueda y guardado ya está en marcha.")

        if os.path.isfile(filename_with_extension):
            # Cargar los IDs de discusión existentes del archivo CSV
            with open(filename_with_extension, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                existing_ids = set(row[0] for row in reader)
                existing_info_count = len(existing_ids)
        else:
            # El archivo no existe, crearlo y escribir el encabezado
            with open(filename_with_extension, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id_discussion', 'title', 'link', 'score',
                              'answer_count', 'view_count', 'creation_date', 'tags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

        with open(filename_with_extension, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id_discussion', 'title', 'link', 'score',
                          'answer_count', 'view_count', 'creation_date', 'tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            page = 1
            inserted_count = 0
            neg_votes_omitted_count = 0
            existing_omitted_count = 0

            while True:
                params["page"] = page
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    questions = data["items"]

                    for question in questions:
                        id_discussion = str(question["question_id"])
                        creation_date = datetime.fromtimestamp(
                            question["creation_date"])

                        # Verificar si la fecha de creación está dentro del rango deseado
                        if datetime(2014, 1, 14) <= creation_date <= fecha_superior:
                            if id_discussion not in existing_ids:
                                title = question["title"]
                                link = question["link"]
                                score = question["score"]
                                answer_count = question["answer_count"]
                                view_count = question["view_count"]
                                tags = ", ".join(question["tags"])

                                csv_row = {
                                    'id_discussion': id_discussion,
                                    'title': title,
                                    'link': link,
                                    'score': score,
                                    'answer_count': answer_count,
                                    'view_count': view_count,
                                    'creation_date': creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                                    'tags': tags
                                }
                                csv_rows.append(csv_row)
                                inserted_count += 1
                                existing_ids.add(id_discussion)
                            else:
                                existing_omitted_count += 1
                        else:
                            neg_votes_omitted_count += 1

                    if not data["has_more"]:
                        break

                    page += 1
                    if page % 30 == 0:
                        print("Esperando")
                        # Espera 1 segundo después de cada 30 solicitudes
                        time.sleep(1)
                else:
                    print("Error al realizar la solicitud HTTP:",
                          response.status_code)
                    break

            writer.writerows(csv_rows)

        # Almacena la cantidad de información anexada
        new_info_count = len(csv_rows)

        # Calcula la diferencia entre la información existente y la anexada
        difference = new_info_count - existing_info_count

        total_questions = inserted_count + neg_votes_omitted_count
        total_omitted = neg_votes_omitted_count

        # Detener y ocultar el ProgressBar
        self.after(100, lambda: self.progress_bar.stop())
        self.after(300, lambda: self.progress_bar.grid_forget())

        result_str = f"Total discusiones encontradas: {total_questions}\n" \
                     f"Total discusiones insertadas al CSV: {inserted_count}\n" \
                     f"Total discusiones omitidas por votos negativos de la actual consulta: {neg_votes_omitted_count}\n" \
                     f"Cantidad de información previa: {existing_info_count}\n" \
                     f"Cantidad de información nueva insertada: {new_info_count}\n" \
                     f"Diferencia entre información nueva y previa: {difference}\n"

        self.result_label.config(text=result_str)
        messagebox.showinfo("Finalizado", "La búsqueda y el guardado de datos se han completado exitosamente.")

    def search_and_save(self):
        
        # Crear ProgressBar
        self.progress_bar = ttk.Progressbar(self, length=200, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        self.progress_bar.start()

        # Iniciar la búsqueda y el guardado en un hilo separado para evitar bloquear la interfaz de usuario
        t = threading.Thread(target=self.perform_search)
        t.start()

if __name__ == "__main__":
    app = Application()
    app.mainloop()