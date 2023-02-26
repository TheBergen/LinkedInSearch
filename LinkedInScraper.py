import tkinter as tk
import customtkinter
from tkinter.filedialog import asksaveasfile
from serpapi import GoogleSearch
import pandas as pd
import re
import datetime

# Change appearance for the application
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Set root frame and size
root = customtkinter.CTk()
root.geometry("500x350")
root.title("LinkedIn Search")

# Specify API key
GoogleSearch.SERP_API_KEY = 'YOUR_API_KEY'

# Get account information
account_search = GoogleSearch({}).get_account()

# Get remaining searches
search_num = account_search.get('plan_searches_left')
searches_left = tk.StringVar(value="Searches left: " + str(search_num))


# Update searches left value
def update():
    global searches_left, search_num
    search_num -= 1
    searches_left = tk.StringVar(value="Searches left: " + str(search_num))
    label.configure(textvariable=searches_left)


# Search for Job Title after button click
def button_callback():
    global search_num, data
    job_title = entry1.get()

    search_query = (f"site:linkedin.com/in/ AND '{job_title}' AND 'Denmark'")

    params = {
        "engine": "google",
        "q": search_query,
        "hl": "da",
        "gl": "dk",
        "num": "500"
    }

    data = []
    search = GoogleSearch(params)
    results = search.get_dict()
    data = pd.json_normalize(results["organic_results"])

    # Get correct name by regex, split by special character
    name = []
    for nameList in data.title:
        splitName = re.findall(r'(\w+[\s\w]*)\b', nameList)
        name.append(splitName[0])
    data['name'] = name

    # If rich_snippet available get location, title and company
    data = data.rename(columns={'rich_snippet.top.extensions': "rich"})
    data['location'] = data.rich.str.get(0)
    data['title'] = data.rich.str.get(1)
    data['company'] = data.rich.str.get(2)

    # Update searches
    button2.configure(state="Enabled")
    update()


def save_file():
    global data
    current_time = datetime.datetime.now().strftime('%d-%m-%Y-%H:%M')
    file_path = asksaveasfile(initialfile=f"LinkedInExport-{current_time}.csv", mode='w', defaultextension=".csv")

    if file_path is None:
        return

    data.to_csv(file_path.name, columns=['position', 'name', 'title', 'link', 'company', 'snippet', 'location'], index=False)

# Frame
frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

# Searches label
label = customtkinter.CTkLabel(master=frame, textvariable=searches_left)
label.pack(pady=12, padx=10)

# Job title entry
entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Job Title")
entry1.pack(pady=12, padx=10)

# Search button
button1 = customtkinter.CTkButton(master=frame, command=button_callback, text="Search")
button1.pack(pady=10, padx=10)

# Export button
button2 = customtkinter.CTkButton(master=frame, text="Export", width=100, state="disabled", command=save_file)
button2.pack(pady=4, padx=10)
root.mainloop()

