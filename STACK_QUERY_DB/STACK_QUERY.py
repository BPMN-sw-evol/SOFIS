import argparse
import requests
import time
import psycopg2
from datetime import datetime

# Crear el objeto ArgumentParser
parser = argparse.ArgumentParser(description='Obtener y almacenar preguntas de StackOverflow')

# Agregar los argumentos
parser.add_argument('-k', '--key', required=True, help='Clave de la API de StackExchange')
parser.add_argument('-i', '--intitle', required=True, help='Título de búsqueda en StackOverflow')
parser.add_argument('-d', '--database', required=True, help='Nombre de la base de datos')
parser.add_argument('-u', '--user', required=True, help='Usuario de la base de datos')
parser.add_argument('-p', '--password', required=True, help='Contraseña de la base de datos')
parser.add_argument('-f', '--fecha-superior', required=True, help='Fecha superior para filtrar las discusiones')

# Parsear los argumentos de la línea de comandos
args = parser.parse_args()

# Define los parámetros de conexión a la base de datos
conn_params = {
    "host": "localhost",
    "database": args.database,
    "user": args.user,
    "password": args.password
}

# Establece una conexión con la base de datos
conn = psycopg2.connect(**conn_params)
cursor = conn.cursor()

url = "https://api.stackexchange.com/2.3/search"

params = {
    "key": args.key,
    "site": "stackoverflow",
    "intitle": args.intitle,
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
            print("esperando")
            time.sleep(1)  # Espera 1 segundo después de cada 30 solicitudes
    else:
        print("Error al realizar la solicitud HTTP:", response.status_code)
        break

# Consulta los IDs de discusión existentes en la base de datos
select_query = "SELECT id_discussion FROM STACK_QUERY"
cursor.execute(select_query)
existing_ids = set(row[0] for row in cursor.fetchall())

inserted_count = 0
neg_votes_omitted_count = 0
existing_omitted_count = 0

# Obtén la fecha superior del argumento y conviértela a un objeto de datetime
fecha_superior = datetime.strptime(args.fecha_superior, '%d-%m-%Y')

for question in questions:
    id_discussion = question["question_id"]

    # Verifica si el ID de discusión ya existe en la base de datos
    if id_discussion in existing_ids:
        existing_omitted_count += 1
        continue

    creation_date = datetime.fromtimestamp(question["creation_date"])

    # Verificar si la fecha de creación está dentro del rango deseado
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
        # La pregunta no está dentro del rango deseado, se omite
        existing_omitted_count += 1

# Confirma los cambios en la base de datos
conn.commit()

# Cierra la conexión con la base de datos
cursor.close()
conn.close()

total_questions = len(questions)
print("Total discusiones encontradas: ", total_questions)
print("Total discusiones insertadas en BD: ", inserted_count)
print("Total discusiones omitidas por votos negativos: ", neg_votes_omitted_count)
print("Total discusiones omitidas porque ya existían en la base de datos: ", existing_omitted_count)