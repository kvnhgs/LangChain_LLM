import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import os
import time

# Base URL for Project Gutenberg
base_url = "https://www.gutenberg.org/ebooks/"

# Create a directory named 'Files' if it doesn't already exist
output_dir = 'Files'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to scrape the "about" section for a single book
def scrape_about(book_id):
    url = base_url + str(book_id)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        about_data = {}
        
        # Extract the "about" section (table format)
        table = soup.find('table', {'class': 'bibrec'})
        if table:
            rows = table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                
                # Check if both 'th' and 'td' are found before getting text
                if th and td:
                    header = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    about_data[header] = value
                
            return about_data
        else:
            print(f"No 'About' section found for book ID: {book_id}")
            return None
    else:
        print(f"Failed to retrieve book with ID: {book_id}, Status Code: {response.status_code}")
        return None

# Scrape one random book between ID 1 and 74000
def scrape_one_book():
    book_id = random.randint(1, 74000)
    print(f"Attempting to scrape book with ID: {book_id}")
    about_info = scrape_about(book_id)
    
    if about_info:
        print(f"Successfully scraped book ID: {book_id}")
        print(about_info)

        # Convert the data into a DataFrame
        df = pd.DataFrame([about_info])
        
        # Save the DataFrame to a CSV file named after the book ID
        csv_output_file = os.path.join(output_dir, f"{book_id}.csv")
        df.to_csv(csv_output_file, index=False)
        print(f"CSV file saved as {csv_output_file}")
        
        # Save the DataFrame to an Excel file named after the book ID
        xlsx_output_file = os.path.join(output_dir, f"{book_id}.xlsx")
        df.to_excel(xlsx_output_file, index=False)
        print(f"Excel file saved as {xlsx_output_file}")
    else:
        print(f"Scraping failed for book ID: {book_id}")

# Scrape one book
scrape_one_book()

# Optional: Pause for a bit before making another request (useful in larger scripts)
time.sleep(1)
