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

        # Disable the option to maximize the window
        self.resizable(False, False)

        # Create interface elements
        api_key_label = tk.Label(self, text="StackExchange API Key:")
        self.api_key_entry = tk.Entry(self, width=35)  # 40-character width
        search_title_label = tk.Label(self, text="StackOverflow Search Title:")
        self.search_title_entry = tk.Entry(self, width=35)  # 40-character width
        upper_date_label = tk.Label(self, text="Upper date to filter discussions (DD-MM-YYYY):")
        self.upper_date_entry = tk.Entry(self, width=30)  # 20-character width
        search_button = tk.Button(self, text="Search and Save", command=self.search_and_save)
        self.result_label = tk.Label(self, text="", wraplength=300, justify=tk.LEFT)

        # Place elements on the window
        api_key_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=5)
        search_title_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.search_title_entry.grid(row=1, column=1, padx=10, pady=5)
        upper_date_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.upper_date_entry.grid(row=2, column=1, padx=10, pady=5)
        search_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def perform_search(self):

        key = self.api_key_entry.get()
        intitle = self.search_title_entry.get()
        upper_date = self.upper_date_entry.get()

        try:
            upper_date = datetime.strptime(upper_date, '%d-%m-%Y')
        except ValueError:
            messagebox.showerror("Error", "The upper date must be in the format DD-MM-YYYY")
            return

        directory = filedialog.askdirectory(title="Select the directory to save the CSV files")

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

        existing_info_count = 0  # Stores the amount of existing information in the CSV file
        messagebox.showinfo("Warning", "The search and save process is already in progress.")

        if os.path.isfile(filename_with_extension):
            # Load existing discussion IDs from the CSV file
            with open(filename_with_extension, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                existing_ids = set(row[0] for row in reader)
                existing_info_count = len(existing_ids)
        else:
            # The file does not exist, create it and write the header
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

                        # Check if the creation date is within the desired range
                        if datetime(2014, 1, 14) <= creation_date <= upper_date:
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
                        print("Waiting")
                        # Wait for 1 second after every 30 requests
                        time.sleep(1)
                else:
                    print("Error when trying HTTP request:", response.status_code)
                    break

            writer.writerows(csv_rows)

        # Store the amount of appended information
        new_info_count = len(csv_rows)

        # Calculate the difference between existing and appended information
        difference = new_info_count - existing_info_count

        total_questions = inserted_count + neg_votes_omitted_count
        total_omitted = neg_votes_omitted_count

        # Stop and hide the ProgressBar
        self.after(100, lambda: self.progress_bar.stop())
        self.after(300, lambda: self.progress_bar.grid_forget())

        result_str = f"Total discussions found: {total_questions}\n" \
                     f"Total discussions inserted into CSV: {inserted_count}\n" \
                     f"Total discussions omitted due to negative votes in the current query: {neg_votes_omitted_count}\n" \
                     f"Amount of existing information: {existing_info_count}\n" \
                     f"Amount of new information inserted: {new_info_count}\n" \
                     f"Difference between new and existing information: {difference}\n"

        self.result_label.config(text=result_str)
        messagebox.showinfo("Finished", "The search and save process has been successfully completed.")

    def search_and_save(self):

        # Create ProgressBar
        self.progress_bar = ttk.Progressbar(self, length=200, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        self.progress_bar.start()

        # Start the search and save process in a separate thread to avoid blocking the user interface
        t = threading.Thread(target=self.perform_search)
        t.start()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
