import requests
import json
import re
import os


scrapped_offers = 1000 # Initializing the number of scrapped offers

url = "https://justjoin.it/api/offers"
response = requests.get(url)
raw_data = response.json()[:scrapped_offers]

data = [{"title": item["title"], "street": item["street"], "country_code": item["country_code"], "address_text": item["address_text"], "marker_icon": item["marker_icon"], "workplace_type": item["workplace_type"], "company_name": item["company_name"], "company_url": item["company_url"], "company_size": item["company_size"], "experience_level": item["experience_level"], "id": item["id"], "employment_types": item["employment_types"], "skills": item["skills"], "remote": item["remote"], "multilocation": item["multilocation"]} for item in raw_data]

for item in data:
    
    offer_url = "https://justjoin.it/api/offers/" + item["id"]

    offer_response = requests.get(offer_url)
    offer_raw_data = offer_response.json()

    description = offer_raw_data["body"]
    pattern = re.compile('<.*?>')
    result = re.sub(pattern, '', description)
    item["description"] = result


with open(os.path.join('research/sourced_data/','document_db.json'), "w") as f:
    json.dump(data, f)


