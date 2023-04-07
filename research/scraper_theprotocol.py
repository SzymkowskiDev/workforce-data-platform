import requests
import json
import os
import logging
from sourced_data.document_db import JobOffersDB
from bs4 import BeautifulSoup


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

#Defining the output file path and base URL
output_file_path = os.path.join('sourced_data/','document_db_protocol.json')
base_url = 'https://theprotocol.it/'
url = base_url + '?pageNumber={}'

#Initializing an empty list for job listings and a page counter
jobs = []
page_num = 1

db = JobOffersDB(output_file_path)
while True:
    print('Scraping page', page_num)
    response = requests.get(url.format(page_num))
    soup = BeautifulSoup(response.text, 'html.parser')
    job_listings = soup.find_all('a', {'href': lambda x: x and '/szczegoly/' in x})
    for job in job_listings:
        job_url = base_url + job['href']
        job_response = requests.get(job_url)
        job_soup = BeautifulSoup(job_response.text, 'html.parser')
        
        
        # Extract the job title
        try:
            # Extract the job title
            title = job_soup.find('h1', class_='rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc titleClass_ttiz6zs').text.strip()
        except:
            # Title could not be extracted, continue to the next job listing
            continue
   
        # Extract the company name
        company_name = job_soup.find('h2', {'class': 'rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc', 'data-test':'text-offerEmployer'}).text

        # Extract the street address
        street = job_soup.find('div', {'data-test': 'text-workplaceAddress'}).text.strip()
        
        
        # Extract the level
        levels = ["trainee", "assistant", "junior", "mid", "senior", "expert", "lead", "manager", "head"]
        for line in job_soup.find_all("div", {"class": "section_s1x3ch8k GridElement_g16c3y1q"}):
            if any(title in line.text.lower() for title in levels):
                level=(line.text.strip())
        
        operating=[]
        # Extract the operating mode
        operating_mode = ["praca zdalna", "praca hybrydowa", "praca stacjonarna"]
        for line in job_soup.find_all("div", {"class": "rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc"}):
            if any(title in line.text.lower() for title in operating_mode):
                operating=line.text.strip()
        
        
        # Extract the employment types
        employment_types = [x.find('p', {'class': 'Contract_cxuwut9'}).text.strip() for x in job_soup.find_all('div', {'data-test': 'section-contract'})]
        
        
        # Extract the salary and units
        job_list = []
        containers = job_soup.find_all('div', {'class': 'Container_cx7p4xk'})
        for container in containers:
            salary_elem = container.find('p', {'class': 'SalaryInfo_s6hpd6f'})
            salary = salary_elem.text if salary_elem else 'No salary information available'
            
            contract_elem = container.find('p', {'class': 'Contract_cxuwut9', 'data-test': 'text-contractName'})
            contract = contract_elem.text if contract_elem else 'No contract information available'
            
            units_elem = container.find('p', {'class': 'Units_u1ewriig', 'data-test': 'text-contractUnits'})
            units = units_elem.text if units_elem else 'No contract units information available'
            
            job = {'salary': salary, 'contract': contract, 'units': units}
            job_list.append(job)

        
        # Extract the skills
        required_skills = []
        skills_container = job_soup.find('div', class_='Container_cv2t83c')
        if skills_container:
            required_skills = [skill.text.strip() for skill in skills_container.find_all('span', class_='Label_l1fs6hs4')]
       
       
        # Extract the job description
        Description = job_soup.find('div', {'class': 'offerSection_oi4q9r7', 'id': 'TECHNOLOGY_AND_POSITION'}).text


       
        # Add the job listing to the jobs list
        job_dict = {
            'title': title,
            'street': street,
            'company_name': company_name,
            'workplace_type': operating,
            'experience_level': level,
            'employment_types': employment_types,
            'salary': job_list,
            'url': job_url,
            'skills': required_skills,
            'description': Description
        }
        jobs.append(job_dict)
        
    
    page_num += 1

    # Save data to output file  
    with open(output_file_path, "w") as f:
        json.dump(jobs, f)
