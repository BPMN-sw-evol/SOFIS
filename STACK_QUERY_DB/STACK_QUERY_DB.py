import requests
import time
import psycopg2
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StackOverflow Search")

        # Disable the option to maximize the window
        self.resizable(False, False)

        self.api_key_label = tk.Label(self, text="StackExchange API Key:")
        self.api_key_entry = tk.Entry(self, width=35)
        self.search_title_label = tk.Label(self, text="StackOverflow Search Title:")
        self.search_title_entry = tk.Entry(self, width=35)
        self.upper_date_label = tk.Label(self, text="Upper date to filter discussions (DD-MM-YYYY):")
        self.upper_date_entry = tk.Entry(self, width=35)
        self.database_label = tk.Label(self, text="Database Name:")
        self.database_entry = tk.Entry(self, width=35)
        self.user_label = tk.Label(self, text="Database User:")
        self.user_entry = tk.Entry(self, width=35)
        self.password_label = tk.Label(self, text="Database Password:")
        self.password_entry = tk.Entry(self, show="*", width=35)
        self.search_button = tk.Button(self, text="Search and Save", command=self.start_search_and_save)
        self.progress_bar = ttk.Progressbar(self, length=200, mode='indeterminate')
        self.result_label = tk.Label(self, text="", width=50, wraplength=300, justify=tk.LEFT)

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
        self.result_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        # Control variable to determine if the search and save process is in progress
        self.is_searching = False

    def start_search_and_save(self):
        if self.is_searching:
            messagebox.showinfo("Warning", "The search and save process is already in progress.")
            return

        # Get the values from the input fields
        key = self.api_key_entry.get()
        intitle = self.search_title_entry.get()
        upper_date = self.upper_date_entry.get()
        database = self.database_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()

        # Check for empty fields
        if not key or not intitle or not upper_date or not database or not user or not password:
            messagebox.showerror("Error", "Please fill in all the fields.")
            return

        # Mark the search and save process as active
        self.is_searching = True

        # Disable the button while performing the search and save process
        self.search_button.config(state=tk.DISABLED)

        # Create conn_params for the database connection
        conn_params = {
            "host": "localhost",
            "database": database,
            "user": user,
            "password": password
        }

        # Start the search and save in a separate thread to avoid blocking the UI
        t = threading.Thread(target=self.perform_search_and_save, args=(key, intitle, upper_date, conn_params))
        t.start()

    def perform_search_and_save(self, key, intitle, upper_date, conn_params):
        # Create ProgressBar before starting the search and save process
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

            # Get the argument upper date and convert to a datetime object
            upper_date = datetime.strptime(upper_date, '%d-%m-%Y')

            for question in questions:
                id_discussion = question["question_id"]

                # Check if discussion ID already exists in the database
                if id_discussion in existing_ids:
                    existing_omitted_count += 1
                    continue

                creation_date = datetime.fromtimestamp(question["creation_date"])

                # Check if the creation date is between the given range
                if datetime(2014, 1, 14) <= creation_date <= upper_date:
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
                    # The question is not inside the given range, it is omitted
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
                         f"Total discussions omitted because already exist in DB: {existing_omitted_count}\n"

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing the search and save: {e}")
        finally:
            # Mark the search and save process as inactive
            self.is_searching = False

            # Enable the button after finishing the search and save process
            self.search_button.config(state=tk.NORMAL)

            # Stop and hide the ProgressBar
            self.progress_bar.stop()
            self.progress_bar.grid_forget()
            self.result_label.config(text=result_str)
            messagebox.showinfo("Finished", "The search and save process has been successfully completed.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
