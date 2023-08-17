import argparse
import os
import sys
import time
from datetime import datetime
import csv
import requests

def show_help():
    print("""
    This program fetches Stackoverflow issues related to a specific BPM engine as required by user-provided search criteria.
    Issues are obtained from 14/01/2014 (the official release date of the BPMN 2.0 standard). Results are stored in a CSV file 
    provided by the user.
    More information at https://github.com/BPMN-sw-evol/SOFIS.git

    Usage: SOFIS_CSV_CONSOLE.exe -k "API Key" -i "Search Title" -u "Upper Date (DD-MM-YYYY)" -d "Directory to save CSV files"

    OPTIONS:
    -k, --key            StackExchange API Key (Required)
                        Example: -k "ahhBNdmxDJ5zP2dxaJvCHw(("

    -i, --intitle        Search Title on StackOverflow (Required)
                        Example: -i "camunda"

    -u, --upper-date     Upper date for filtering discussions (DD-MM-YYYY) (Required)
                        Example: -u "12-06-2023"

    -d, --directory      Directory to save CSV files (Required)
                        Example: -d "G:\Tutorials"
    
    -h, --help           Show help
    """)
    sys.exit()

def parse_arguments():

    parser = argparse.ArgumentParser(
        description='Fetch and store StackOverflow questions')
    
    # Add arguments
    parser.add_argument('-k', '--key', nargs='?',
                        const='help_key', help='StackExchange API Key')
    parser.add_argument('-i', '--intitle', nargs='?',
                        const='help_intitle', help='Search Title on StackOverflow')
    parser.add_argument('-u', '--upper-date', nargs='?', const='help_upper_date',
                        help='Upper date for filtering discussions (DD-MM-YYYY)')
    parser.add_argument('-d', '--directory', nargs='?',
                        const='help_directory', help='Directory to save CSV files')

    if '-h' in sys.argv or '--help' in sys.argv:
        show_help()

    args = parser.parse_args()

    if args.key == 'help_key':
        print(f"Help for '-k': {parser._option_string_actions['-k'].help}")
        sys.exit(1)
    elif args.intitle == 'help_intitle':
        print(f"Help for '-i': {parser._option_string_actions['-i'].help}")
        sys.exit(1)
    elif args.upper_date == 'help_upper_date':
        print(f"Help for '-u': {parser._option_string_actions['-u'].help}")
        sys.exit(1)
    elif args.directory == 'help_directory':
        print(f"Help for '-d': {parser._option_string_actions['-d'].help}")
        sys.exit(1)

    # Verify if all required arguments are provided
    if len(sys.argv) == 1:
        print(
            "Error: Insufficient arguments. Provide all required parameters. For more information, use [-h]")
        print(
            "Usage: %s -k \"API Key\" -i \"Search Title\" -u \"Upper Date (DD-MM-YYYY)\" -d \"Directory to save CSV files\"" % sys.argv[0])
        sys.exit(1)

    if not args.key:
        print("Error: API Key not provided. Use the -k argument with an API_KEY. Example: -k \"ahhBNdmxDJ5zP2dxaJvCHw((")
        sys.exit(1)

    if not args.intitle:
        print("Error: Search Title not provided. Use the -i argument with a title. Example: -i \"camunda\"")
        sys.exit(1)

    if not args.upper_date:
        print("Error: Upper Date not provided. Use the -u argument with a date in the format DD-MM-YYYY. Example: -u \"12-06-2023\"")
        sys.exit(1)

    if not args.directory:
        print("Error: Directory not provided. Use the -d argument with a directory. Example: -d \"G:\\Tutorials\"")
        sys.exit(1)


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
    file_pars = os.path.join(args.directory, f"SQ.pars.{args.intitle}.txt")

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
            fieldnames = ['id_discussion', 'title', 'link', 'score',
                        'answer_count', 'view_count', 'creation_date', 'tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    with open(file_CSV, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id_discussion', 'title', 'link', 'score',
                    'answer_count', 'view_count', 'creation_date', 'tags']
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
                    creation_date = datetime.fromtimestamp(
                        question["creation_date"])

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

    # Calculate the difference between existing and appended information
    difference = new_info_count - existing_info_count

    total_questions = inserted_count + neg_votes_omitted_count
    total_omitted = neg_votes_omitted_count

    print("Total discussions found: ", total_questions)
    print("Total discussions inserted in CSV: ", inserted_count)
    print("Total discussions omitted due to negative votes in the current query: ",
          neg_votes_omitted_count)
    print("Amount of previous information: ", existing_info_count)

def main():
    parse_arguments()


if __name__ == "__main__":
    main()
