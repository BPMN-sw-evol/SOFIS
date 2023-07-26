import argparse
import csv
import requests
import time
from datetime import datetime
import os

# Create the ArgumentParser object
parser = argparse.ArgumentParser(description='Get and store StackOverflow questions')

# Add the arguments
parser.add_argument('-k', '--key', required=True, help='StackExchange API Key')
parser.add_argument('-i', '--intitle', required=True, help='StackOverflow Search Title')
parser.add_argument('-s', '--upper-date', required=True, help='Upper date to filter discussions (DD-MM-YYYY)')
parser.add_argument('-d', '--directory', required=True, help='Directory to save CSV files')

# Parse the command line arguments
args = parser.parse_args()

url = "https://api.stackexchange.com/2.3/search"

params = {
    "key": args.key,
    "site": "stackoverflow",
    "intitle": args.intitle,
}

header_pars = [
    "TIMESTAMP",
    "API_KEY",
    "SEARCH_TITLE",
    "UPPER_DATE",
    "DIRECTORY"
]

csv_rows = []
existing_ids = set()

file_CSV = os.path.join(args.directory, f"{args.intitle}.csv")
file_pars = os.path.join("./Test/", f"SQ.pars.{args.intitle}.txt")

existing_info_count = 0  # Store the amount of existing information in the file
    
# Validate if the file exists
if os.path.exists(file_pars):
    # If the file exists, open it in read mode ('r')
    with open(file_pars, 'r') as file:
        # Read the existing content
        content = file.read()

    # If the content is empty, add the headers
    if not content.strip():
        with open(file_pars, 'a') as file:
            file.write(','.join(header_pars) + '\n')
else:
    # If the file does not exist, create it and open it in write mode ('w')
    with open(file_pars, 'w') as file:
        file.write(','.join(header_pars) + '\n')

# Add the information of the variables to the file
with open(file_pars, 'w') as file:
    file.write(','.join(header_pars) + '\n')
    file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S') }, { args.key }, { args.intitle }, { args.upper_date }, { args.directory }\n")
        
        
if os.path.isfile(file_CSV):
    # Load existing discussion IDs from the CSV file
    with open(file_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        existing_ids = set(row[0] for row in reader)
        existing_info_count = len(existing_ids)
else:
    # The file does not exist, create it and write the header
    with open(file_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id_discussion', 'title', 'link', 'score', 'answer_count', 'view_count', 'creation_date', 'tags']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

with open(file_CSV, 'a', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id_discussion', 'title', 'link', 'score', 'answer_count', 'view_count', 'creation_date', 'tags']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    page = 1
    inserted_count = 0
    neg_votes_omitted_count = 0
    existing_omitted_count = 0

    fecha_superior = datetime.strptime(args.upper_date, '%d-%m-%Y')

    while True:
        params["page"] = page
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            questions = data["items"]

            for question in questions:
                id_discussion = str(question["question_id"])
                creation_date = datetime.fromtimestamp(question["creation_date"])

                # Check if the creation date is within the desired range
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
                print("Waiting...")
                time.sleep(1)  # Wait 1 second after every 30 requests
        else:
            print("Error when making HTTP request:", response.status_code)
            break

    writer.writerows(csv_rows)

new_info_count = len(csv_rows)  # Store the amount of appended information

difference = new_info_count - existing_info_count  # Calculate the difference between existing and appended information

total_questions = inserted_count + neg_votes_omitted_count
total_omitted = neg_votes_omitted_count

print("Total discussions found: ", total_questions)
print("Total discussions inserted in CSV: ", inserted_count)
print("Total discussions omitted due to negative votes in the current query: ", neg_votes_omitted_count)
print("Amount of previous information: ", existing_info_count)