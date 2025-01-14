import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging

def mine_news_output_dataframe(keyword, num_pages):
    """
    Scrape Google News search results for a given keyword and number of pages.
    
    Args:
        keyword (str): The search query.
        num_pages (int): Number of pages to scrape.

    Returns:
        pd.DataFrame: A DataFrame containing unique news entries.
    """
    df = pd.DataFrame(columns=[keyword])
    hashset = set()

    for page in range(num_pages):
        start = page * 10  # Pagination: page 1 = start 0, page 2 = start 10, etc.

        url = (f"https://www.google.com/search?q={keyword}&sca_esv=c7a01837b1eb8e0f&rlz=1C1UEAD_enSG1060SG1060"
               f"&tbs=qdr:d,sbd:1&tbm=nws&sxsrf=ADLYWIJuzOuTZOex_My9k7KzN3z2MAPdSA:1725633163846"
               f"&ei=ixLbZpmnM8jD4-EPxezCKQ&start={start}&sa=N&ved=2ahUKEwjZmPm9xK6IAxXI4TgGHUW2MAUQ8NMDegQIAxAS")

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        contents = soup.find_all("div")  # Modify selector based on Google News structure.

        for x in contents:
            content = x.text.strip()

            if any(content[:5] == existing[:5] for existing in hashset):
                continue  # Skip duplicates.

            hashset.add(content)
            new_row = pd.DataFrame({keyword: [content]})
            df = pd.concat([df, new_row], ignore_index=True)

    return df


def scrape_news(keywords):

    logging.basicConfig(
        filename="C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\script.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Initialize an empty DataFrame
    combined_df = pd.DataFrame()

    # Scrape data for each keyword
    for keyword in keywords:
        print(f"Scraping news for: {keyword}")
        logging.info(f"Scraping news for: {keyword}")
        result_df = mine_news_output_dataframe(keyword, 5)  # Scrape 5 pages per keyword
        logging.info(f"Scraping news for: {keyword} completed")
        combined_df = pd.concat([combined_df, result_df], axis=1, join="outer")

    # Save results to a CSV file
    combined_df.to_csv("C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\google_news.csv", index=False)
    
    # Save results to a TXT file
    txt_file_path = "C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\google_news.txt"
    with open(txt_file_path, "w", encoding="utf-8") as f:
        combined_df.to_string(buf=f, index=False)
    
    print("Scraping completed. Results saved to google_news.csv and google_news.txt.")
    print(combined_df)
    
if __name__ == "__main__":
    # Keywords to search
    # keywords = ["global+news+today", "financial+markets+news", "fixed+income+news", "currencies+news", "equities+news", "commodities+news"]
    scrape_news(["global+news+today", "financial+markets+news"])