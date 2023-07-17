import argparse
import csv
import requests
import time
from datetime import datetime
import os

# Crear el objeto ArgumentParser
parser = argparse.ArgumentParser(description='Obtener y almacenar preguntas de StackOverflow')

# Agregar los argumentos
parser.add_argument('-k', '--key', required=True, help='Clave de la API de StackExchange')
parser.add_argument('-i', '--intitle', required=True, help='Título de búsqueda en StackOverflow')
parser.add_argument('-s', '--fecha-superior', required=True, help='Fecha superior para filtrar las discusiones')
parser.add_argument('-d', '--directory', required=True, help='Directorio para guardar los archivos CSV')

# Parsear los argumentos de la línea de comandos
args = parser.parse_args()

url = "https://api.stackexchange.com/2.3/search"

params = {
    "key": args.key,
    "site": "stackoverflow",
    "intitle": args.intitle,
}

csv_rows = []
existing_ids = set()    

filename_with_extension = os.path.join(args.directory, f"{args.intitle}.csv")

existing_info_count = 0  # Almacena la cantidad de información existente en el archivo

if os.path.isfile(filename_with_extension):
    # Cargar los IDs de discusión existentes del archivo CSV
    with open(filename_with_extension, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        existing_ids = set(row[0] for row in reader)
        existing_info_count = len(existing_ids)
else:
    # El archivo no existe, crearlo y escribir el encabezado
    with open(filename_with_extension, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id_discussion', 'title', 'link', 'score', 'answer_count', 'view_count', 'creation_date', 'tags']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

with open(filename_with_extension, 'a', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id_discussion', 'title', 'link', 'score', 'answer_count', 'view_count', 'creation_date', 'tags']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    page = 1
    inserted_count = 0
    neg_votes_omitted_count = 0
    existing_omitted_count = 0

    fecha_superior = datetime.strptime(args.fecha_superior, '%d-%m-%Y')

    while True:
        params["page"] = page
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            questions = data["items"]

            for question in questions:
                id_discussion = str(question["question_id"])
                creation_date = datetime.fromtimestamp(question["creation_date"])

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
                time.sleep(1)  # Espera 1 segundo después de cada 30 solicitudes
        else:
            print("Error al realizar la solicitud HTTP:", response.status_code)
            break

    writer.writerows(csv_rows)

new_info_count = len(csv_rows)  # Almacena la cantidad de información anexada

difference = new_info_count - existing_info_count  # Calcula la diferencia entre la información existente y la anexada

total_questions = inserted_count + neg_votes_omitted_count
total_omitted = neg_votes_omitted_count

print("Total discusiones encontradas: ", total_questions)
print("Total discusiones insertadas al CSV: ", inserted_count)
print("Total discusiones omitidas por votos negativos de la actual consulta: ", neg_votes_omitted_count)
print("Cantidad de información previa: ", existing_info_count)
