import argparse
import requests
import time
import psycopg2
from datetime import datetime

# Create the object ArgumentParser
parser = argparse.ArgumentParser(description='Get and save StackOverflow questions')

# Add the arguments
parser.add_argument('-k', '--key', required=True, help='StackExchange API KEY')
parser.add_argument('-i', '--intitle', required=True, help='StackOverflow title to search')
parser.add_argument('-d', '--database', required=True, help='Database name')
parser.add_argument('-u', '--user', required=True, help='Database username')
parser.add_argument('-p', '--password', required=True, help='Database user password')
parser.add_argument('-f', '--upper-date', required=True, help='Upper date to filter discussions')

# Parse the command line arguments
args = parser.parse_args()

# Database connection parameters
conn_params = {
    "host": "localhost",
    "database": args.database,
    "user": args.user,
    "password": args.password
}

# Establish connection with the database
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
fecha_superior = datetime.strptime(args.fecha_superior, '%d-%m-%Y')

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
print("Total discussions found: ", total_questions)
print("Total discussions inserted in DB: ", inserted_count)
print("Total discussions omitted for negatives votes: ", neg_votes_omitted_count)
print("Total discussions omitted because already exists in DB: ", existing_omitted_count)