import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time


scrapped_offers=2 # Initializing the number of scrapped offers

# Looping through the number of scrapped offers
for i in range(srapped_offers):
    
    url = "https://justjoin.it/api/offers"
    response = requests.get(url)

    raw_data = response.json()
    data = [{"title": item["title"], "street": item["street"], "country_code": item["country_code"], "address_text": item["address_text"], "marker_icon": item["marker_icon"], "workplace_type": item["workplace_type"], "company_name": item["company_name"], "company_url": item["company_url"], "company_size": item["company_size"], "experience_level": item["experience_level"], "id": item["id"], "employment_types": item["employment_types"], "skills": item["skills"], "remote": item["remote"], "multilocation": item["multilocation"]} for item in raw_data[:scrapped_offers]]

    for item in data:
        # Creating a new webdriver instance and setting the options
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=options)

        driver.get("https://justjoin.it/offers/" + item["id"]) # Navigating to the offer page using the offer ID from the API

        time.sleep(5) # Waiting for the page to load

        # Finding the element on the page that contains the offer description and extracting its text content
        desc= driver.find_elements(by=By.CLASS_NAME, value='css-p1hlmi')
        item["description"] = desc[0].text

        # Close the chromebrowser
        driver.quit()

    # Writing the data to a JSON file
    with open("iustioinit_offerts.json", "w") as f:
        json.dump(data, f)
