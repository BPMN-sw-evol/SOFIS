import argparse
import requests
import time
import psycopg2
import os
import sys
from datetime import datetime

def show_help():
    print("""
    This program fetches Stackoverflow issues related to a specific BPM engine required by user-supplied search criteria.
    They are obtained as of 14/01/2014 ( the official publication date of the BPMN 2.0 standard). Stores the results in a PostgreSQL
    database provided by the user. 
    More info at https://github.com/BPMN-sw-evol/SOFIS.git 

    Usage: SOFIS_DB_CONSOLE.exe -k "API Key" -i "Search Title" -d "Database name" -u "Database username" -p "Database user password" -f "Upper date (DD-MM-YYYY)"

    OPTIONS:
    -k, --key            StackExchange API Key (required)
                        Example: -k "ahhBNdmxDJ5zP2dxaJvCHw(("

    -i, --intitle        Search Title on StackOverflow (Required)
                        Example: -i "camunda"

    -d, --database       Database name (required)
                        Example: -d "mydatabase"
          
    -u, --user           Database username (required)
                        Example: -u "myuser"

    -p, --password       Database user password (required)
                        Example: -p "mypassword"
          
    -f, --upper-date     Upper date to filter discussions (DD-MM-YYYY) (required)
                        Example: -f "12-06-2023"
          
    -h, --help           Show help
    """)

    sys.exit()

def parse_arguments():

    parser = argparse.ArgumentParser(description='Get and save StackOverflow questions')

    # Add arguments
    parser.add_argument('-k', '--key',nargs='?',
                        const='help_key', help='StackExchange API KEY')
    parser.add_argument('-i', '--intitle',nargs='?',
                        const='help_intitle', help='StackOverflow title to search')
    parser.add_argument('-d', '--database', nargs='?',
                        const='help_database', help='Database name')
    parser.add_argument('-u', '--user', nargs='?',
                        const='help_user', help='Database username')
    parser.add_argument('-p', '--password', nargs='?',
                        const='help_password', help='Database user password')
    parser.add_argument('-f', '--upper-date', nargs='?',
                        const='help_date', help='Upper date to filter discussions')
    
    if '-h' in sys.argv or '--help' in sys.argv:
        show_help()

    args = parser.parse_args()

    if args.key == 'help_key':
        print(f"Help for '-k': {parser._option_string_actions['-k'].help}")
        sys.exit(1)
    elif args.intitle == 'help_intitle':
        print(f"Help for '-i': {parser._option_string_actions['-i'].help}")
        sys.exit(1)
    elif args.database == 'help_database':
        print(f"Help for '-d': {parser._option_string_actions['-d'].help}")
        sys.exit(1)
    elif args.user == 'help_user':
        print(f"Help for '-u': {parser._option_string_actions['-u'].help}")
        sys.exit(1)
    elif args.password == 'help_password':
        print(f"Help for '-p': {parser._option_string_actions['-p'].help}")
        sys.exit(1)
    elif args.upper_date == 'help_date':
        print(f"Help for '-f': {parser._option_string_actions['-f'].help}")
        sys.exit(1)

    # Verify if all required arguments are provided
    if len(sys.argv) == 1:
        print(
            "Error: Insufficient arguments. Please provide all required parameters. For more information use [-h]")
        print(
            "Usage: %s -k \"API Key\" -i \"Search Title\" -d \"Database name\" -u \"Database username\" -p \"Database user password\" -f \"Upper Date (DD-MM-YYYY)\"" % sys.argv[0])
        sys.exit(1)

    if not args.key:
        print("Error: API Key not provided. Use the -k argument with an API_KEY. Example: -k \"ahhBNdmxDJ5zP2dxaJvCHw((")
        sys.exit(1)

    if not args.intitle:
        print("Error: Search Title not provided. Use the -i argument with a title. Example: -i \"camunda\"")
        sys.exit(1)

    if not args.database:
        print("Error: Database not provided. Use -d argument with a database. Example -d \"SOFIS\"")
        sys.exit(1)

    if not args.user:
        print("Error: User not provided. Use -u argument with a user. Example -u \"postgres\"")
        sys.exit(1)

    if not args.password:
        print("Error: password not provided. Use -p argument with a password. Example -p \"1234\"")
        sys.exit(1)

    if not args.upper_date:
        print("Error: Upper date not provided. Use -f argument with a date in format DD-MM-YYYY. Example -f \"12-06-2023\"")
        sys.exit(1)

    conn_params = {
        "host": "localhost",
        "database": args.database,
        "user": args.user,
        "password": args.password
    }

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

    select_query = "SELECT id_discussion FROM SOFIS_QUERY"
    cursor.execute(select_query)
    existing_ids = set(row[0] for row in cursor.fetchall())

    inserted_count = 0
    neg_votes_omitted_count = 0
    existing_omitted_count = 0

    fecha_superior = datetime.strptime(args.upper_date, '%d-%m-%Y')

    for question in questions:
        id_discussion = question["question_id"]

        if id_discussion in existing_ids:
            existing_omitted_count += 1
            continue

        creation_date = datetime.fromtimestamp(question["creation_date"])

        if datetime(2014, 1, 14) <= creation_date <= fecha_superior:
            title = question["title"]
            link = question["link"]
            score = question["score"]
            answer_count = question["answer_count"]
            view_count = question["view_count"]
            tags = ", ".join(question["tags"])

            if score >= 0:
                insert_query = "INSERT INTO SOFIS_QUERY(id_discussion, title, link, score, answer_count, view_count, creation_date, tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (id_discussion, title, link, score, answer_count, view_count, creation_date, tags))
                inserted_count += 1
                existing_ids.add(id_discussion)
            else:
                neg_votes_omitted_count += 1
        else:
            existing_omitted_count += 1

    conn.commit()
    cursor.close()
    conn.close()

    total_questions = len(questions)
    print("Total discussions found: ", total_questions)
    print("Total discussions inserted in DB: ", inserted_count)
    print("Total discussions omitted for negative votes: ", neg_votes_omitted_count)
    print("Total discussions omitted because already exist in DB: ", existing_omitted_count)

def main():
    parse_arguments()

if __name__ == "__main__":
    main()
