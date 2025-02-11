import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import timedelta

def adjust_time(data):
    time = pd.to_datetime(data)
    update = time + timedelta(hours=13)
    return update

def scrape_and_process_calendar():
    url = "https://www.investing.com/economic-calendar/"
    
    # Send a GET request to the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all <tr> elements
    contents = soup.find_all("tr")

    data = []
    # Loop through each <tr> and find <td> elements within each row
    for row in contents:
        columns = row.find_all("td")  # Find all <td> within this <tr>
        # Extract and print text from each column in the row
        row_data = [col.text.strip() for col in columns]
        if len(row_data) == 8:
            data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data)
    df.drop(columns=[2, 7], inplace=True)
    cols = ["Time", "Country", "Event", "Actual", "Forecast", "Previous"]
    df.columns = cols

    for i in range(len(df)):
        df.loc[i, "Time"] = adjust_time(df.loc[i, "Time"])

    df.to_csv("C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\calendar.csv", index=False)
    
    print(df.to_string(index=False))
    
    return df.to_html(index=False, justify="center", border=1)


def scrape_and_process_calendar_2():
    url = "https://www.investing.com/economic-calendar/"
    
    # Set up Selenium WebDriver with SSL options (e.g., Chrome)
    options = webdriver.FirefoxOptions()
    options.accept_insecure_certs = True
    driver = webdriver.Firefox(options=options)  # Ensure geckodriver is in your PATH
    
    # Retry mechanism
    max_retries = 3
    for attempt in range(max_retries):
        try:
            driver.get(url)
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait before retrying
            else:
                raise
    
    # Wait for the popup close icon to be clickable and click it
    try:
        popup_close_icon = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "popupCloseIcon"))
        )
        popup_close_icon.click()
    except Exception as e:
        print("No popup found or failed to close popup:", e)
    
    # Wait for the dropdown arrow inside the economicCurrentTime div to be clickable and click it
    dropdown_arrow = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="economicCurrentTime"]/span[@class="dropDownArrowGray"]'))
    )
    dropdown_arrow.click()
    
    # Wait for the specific timezone option to be clickable and click it
    gmt_plus_8_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="liTz113"]'))
    )
    gmt_plus_8_option.click()
    
    # # Get the page source after the interaction
    page_source = driver.page_source
    # print(page_source)
    driver.quit()
    
    return page_source
    
    # # Parse the page source with BeautifulSoup
    # soup = BeautifulSoup(page_source, "html.parser")

    # # Find all <tr> elements
    # contents = soup.find_all("tr")

    # data = []
    # # Loop through each <tr> and find <td> elements within each row
    # for row in contents:
    #     columns = row.find_all("td")  # Find all <td> within this <tr>
    #     # Extract and print text from each column in the row
    #     row_data = [col.text.strip() for col in columns]
    #     if len(row_data) == 8:
    #         data.append(row_data)

    # # Create DataFrame
    # df = pd.DataFrame(data)
    # df.drop(columns=[2, 7], inplace=True)
    # cols = ["Time", "Country", "Event", "Actual", "Forecast", "Previous"]
    # df.columns = cols

    # for i in range(len(df)):
    #     df.loc[i, "Time"] = adjust_time(df.loc[i, "Time"])

    # df.to_csv("C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\calendar.csv", index=False)
    
    # print(df.to_string(index=False))
    
    # return df.to_html(index=False, justify="center", border=1)

if __name__ == "__main__":
    scrape_and_process_calendar_2()