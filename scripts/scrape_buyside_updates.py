import requests
from bs4 import BeautifulSoup
import csv
import json

# Input file (replace with your extracted CSV file location)
input_file = 'C:/Users/tee_m/Desktop/TIC3901 Indus Project/scripts/input_buy_side_weekly_updates.csv'

# Output file to save the scraped content
output_file = 'C:/Users/tee_m/Desktop/TIC3901 Indus Project/scripts/output_buy_side_weekly_updates.json'

def scrape_content(url):
    """Scrape the content of a webpage given its URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the text content from the webpage
        content = soup.get_text(separator='\n', strip=True)
        return content 
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Read the input CSV
with open(input_file, mode='r') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)

# Scrape content for each link
results = []
for row in rows:
    
    if row["name"] == "charlesSCHWAB": # CharlesSchwab cannot scrape
        continue
    
    name = row['name']
    link = row['link']
    print(f"Scraping {name}: {link}")
    content = scrape_content(link)
    results.append({'name': name, 'link': link, 'content': content})

# Write the results to an output JSON file
with open(output_file, mode='w', encoding='utf-8') as jsonfile:
    json.dump(results, jsonfile, indent=4, ensure_ascii=False)

print(f"Scraping completed. Results saved to {output_file}")