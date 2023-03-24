import requests
import json
import re
import os
import logging
from template import data

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

# Configuration variables
scrapped_offers = 10000
output_file_path = os.path.join('research/sourced_data/', 'document_db.json')

def main():
    """
    Web scraper made to work with justjoin.it. Scrapes job offers and saves them in JSON format in a specified location.
    To use, execute the script.
    """
    try:
        # Get raw data from the API
        url = "https://justjoin.it/api/offers"
        response = requests.get(url)
        raw_data = response.json()[:scrapped_offers]

        # Extract appropriate information from the raw data based on the structure stored in the template.py file and store it in the list of dictionaries
        data = [{k: item[k] for k in item} for item in raw_data]

        # Get the offer descriptions by making additional requests to the API and clean up the HTML tags
        for item in data:
            offer_url = f"https://justjoin.it/api/offers/{item['id']}"
            offer_response = requests.get(offer_url)
            offer_response.raise_for_status() # Raises an exception for 4xx or 5xx status codes
            offer_raw_data = offer_response.json()
       
            # Extract the job offer description from the fetched data
            description = offer_raw_data["body"]

            # Remove all HTML tags from the description
            pattern = re.compile('<.*?>')
            result = re.sub(pattern, '', description)

            # Add the cleaned description as a new key-value pair to "data"
            item["description"] = result

        # Save data to output file
        with open(output_file_path, "w") as f:
            json.dump(data, f)

        # Log success
        logging.debug("* "*50)
        logging.debug("Web scraper completed successfully.")
        logging.debug(f"Obtained {len(data)} of job offers from {url}")
        logging.debug(f"Output saved to {output_file_path}")
        logging.debug("* "*50)

    except requests.exceptions.RequestException as e:
        # Handle the exception
        print("Exception request")
        print(e)


if __name__ == "__main__":
    main()
