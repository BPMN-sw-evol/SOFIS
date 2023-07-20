import argparse
import csv
import requests
import time
from datetime import datetime
import os

# Create the object ArgumentParser
parser = argparse.ArgumentParser(description='Get and save StackOverflow questions')

# Add the arguments
parser.add_argument('-k', '--key', required=True, help='StackExchange API KEY')
parser.add_argument('-i', '--intitle', required=True, help='StackOverflow title to search')
parser.add_argument('-s', '--fecha-superior', required=True, help='Upper date to filter discussions')
parser.add_argument('-d', '--directory', required=True, help='Directory or folder to save the CSV files')

# Parser the command line arguments
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

existing_info_count = 0  # Stores the amount of information in the file

if os.path.isfile(filename_with_extension):
    # Load the discussion IDs exists CSV file 
    with open(filename_with_extension, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        existing_ids = set(row[0] for row in reader)
        existing_info_count = len(existing_ids)
else:
    # The file does not exists, create and write in the header 
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

                # Check if the creation date is between given range
                if datetime(2014, 1, 14) <= creation_date <= fecha_superior:
                    if id_discussion not in existing_ids:
                        title = question["title"]
                        link = question["link"]
                        score = question["score"]
                        answer_count = question["answer_count"]
                        view_count = question["view_count"]
                        tags = ", ".join(question["tags"])

                        # Define the rows in the csv file
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
                print("Waiting for...")
                time.sleep(1)  # Wait for a second after 30 requests
        else:
            print("Error when trying HTTP requests:", response.status_code)
            break

    writer.writerows(csv_rows)

new_info_count = len(csv_rows)  # Store the amount of appened information

difference = new_info_count - existing_info_count  # Calculate the difference between existing and appended information

total_questions = inserted_count + neg_votes_omitted_count
total_omitted = neg_votes_omitted_count

print("Total discussions found: ", total_questions)
print("Total discussions inserted in CSV: ", inserted_count)
print("Total discussions omitted for negatives votes: ", neg_votes_omitted_count)
print("Amount of previous information: ", existing_info_count)
