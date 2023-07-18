# PROGRAM INFORMATION
***Name:*** STACK_QUERY<br>
***Description:*** Programa that fetches discussions from StackOverflow on a given topic using an API and stores the results in a PostgreSQL database called STACK_QUERY or in local CSV files.<br>
***API:*** https://stackapps.com/apps/oauth/view/26090

***IMPORTANT:*** the program has two versions: the **FIRST** one called STACK_QUERY_CSV contains a python code that when executed generates the CSV file with the obtained results and the **SECOND** one, called STACK_QUERY_DB uses a PostgreSQL database to store the obtained results.   
**Version A**: Se obtiene información sobre las preguntas más votadas por un usuario

# Getting the API KEY:
In both cases you need to get the API key if you need to make many requests.

1. Register at https://stackapps.com/users/login.
2. Register the application to obtain the credentials to use the StackOverflow API https://stackapps.com/apps/oauth/register. 
3. Obtain a client ID and a secret key for OAuth authentication in Stack Overflow.

# To run the program you need:

1.	Install a code editor, recommended Visual Studio Code (VSCODE): https://code.visualstudio.com/download
2.	Install the version control system GIT: https://git-scm.com/downloads
3.	Clone the repository using the command: git clone https://github.com/danilonunezgil/BPM_PC_S.git
4.	Install Python, any version: https://www.python.org/downloads/ or install the extension in VSCODE.
5.	Install the following modules:
pip install requests (for making HTTP requests) pip install psycopg2-binary (only if you're using the PostgreSQL version)
6.	If you need to use PostgreSQL, follow these steps, otherwise skip them.
7.	Install PostgreSQL: https://www.postgresql.org/download/windows/ (stable version or latest version)
8.	Using pgAdmin 4, create a database called BPM_PC_QUERY.
9.	In the same database, using the script called BPM_PC_Query.sql, create the following table:
   
   CREATE TABLE BPM_PC_QUERY (<br>
      id_discussion SERIAL PRIMARY KEY,<br>
      topic VARCHAR(25),<br>
      title VARCHAR(255),<br>
      link VARCHAR(255),<br>
      score INTEGER,<br>
      answer_count INTEGER,<br>
      view_count INTEGER,<br>
      creation_date DATE,<br>
      tags VARCHAR(255)<br>
   );<br>
   
10. Execute the program using the following instruction in the terminal:
    
   ***Example for STACK_QUERY:*** <br><br>python STACK_QUERY.py -k "ahhBNdmxDJ5zP2dxaJvCHw((" -i "camunda" -d "STACK_QUERY" -u "postgres" -p "12345" -f "12-06-2023" <br>
   ***Example for STACK_QUERY_CSV:*** <br><br>python STACK_QUERY_CSV.py -k  "ahhBNdmxDJ5zP2dxaJvCHw((" -i "camunda" -s DD-MM-YYYY -d "/ruta/que/desees"  <br>

12. If there are no errors, the data will be saved discarding those discussions that have negative votes (less than zero). The program performs a validation of the existence of a discussion and skips it if it is already in the database. To verify the data, execute the SQL statement in pgAdmin 4:

SELECT * FROM DB_name WHERE title ILIKE '%search_name%';

# Development Summary: 
This program is responsible for using the StackOverflow API to retrieve questions related to a specified search title. It then stores these questions in a local database using PostgreSQL. The program checks if each question already exists in the database, and if not, and it has a score greater than or equal to zero, it inserts it. Finally, statistics are displayed regarding the number of questions found, inserted, skipped due to negative votes, and skipped due to already existing in the database.

The database stores the following attributes for each discussion:

| Attribute | Description |
| --- | --- |
| id_discussion | Unique identifier of the discussion |
| title | Title of the discussion |
| link | Link to the StackOverflow webside for the discussion |
| score | Score of the discussion |
| answer_count | Number of answers for the discussion |
| view_count | Number of views for the discussion |
| creation_date | Creation date of the discussion |
| tags | Tags related to the discussion |

The development in question focuses on searching for discussions within StackOverflow whose titles contain the specific platform requested as a parameter. This is because, at times, the data provided by the API is not fully contextualized in relation to the target platform if the specific platform is searched for in both the discussion body and its answers.

# API Usage Limitations:
https://api.stackexchange.com/docs/throttle<br>
Maximum 30 requests per second<br>
Maximum 10,000 requests per day<br>
If the daily limit is exceeded, an HTTP 429 error will be returned.<br>
If the daily request limit to the server is exceeded, the 10,000 requests will be renewed from the next midnight.

# Future Improvements:
Implement a cloud-based database.<br>
Update record by record or specific record.
