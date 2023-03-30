import os
import sys
import pandas as pd
import numpy as np

from research.sourced_data.document_db import JobOffersDB
root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'research', 'sourced_data')
db_path = os.path.join(root_path, 'document_db.json')


def create_csv_from_document_db(db):
    data = db.get_all_job_offers()

    unique_skills = set()
    for skills in data['skills']:
        for skill in skills:
            unique_skills.add(skill['name'])
    
    skills_binary_df = pd.DataFrame(0, index=data.index, columns=list(unique_skills))

    for idx, skills in data['skills'].items():
        for skill in skills:
            skills_binary_df.at[idx, skill['name']] = 1

    data = pd.concat([data, skills_binary_df], axis=1)
    data = data.drop(columns=['skills'])
    def extract_employment_type_values(employment_types):
        if not employment_types or not isinstance(employment_types, list):
            return None, None, None, None

        emp_type = employment_types[0]
        type_ = emp_type.get('type', None)
        salary = emp_type.get('salary', {})

        if not isinstance(salary, dict):
            salary = {}

        salary_from = salary.get('from', np.NaN)  # Replace None with np.NaN
        salary_to = salary.get('to', np.NaN)  # Replace None with np.NaN
        currency = salary.get('currency', None)

        return type_, salary_from, salary_to, currency

    data[['type', 'salary_from', 'salary_to', 'currency']] = data['employment_types'].apply(extract_employment_type_values).apply(pd.Series)

    data = data.drop(columns=['employment_types'])

    def extract_city_names(multilocation):
        city_names = [loc.get('city', None) for loc in multilocation if isinstance(loc, dict)]
    
        if len(city_names) == 0:
            city_names += ['nonexistent'] * 5
        elif len(city_names) == 1:
         city_names += ['nonexistent'] * 4
        elif len(city_names) == 2:
         city_names += ['nonexistent'] * 3
        elif len(city_names) == 3:
            city_names += ['nonexistent'] * 2
        elif len(city_names) == 4:
            city_names += ['nonexistent']
    
        return city_names[:5]
    

    data[['city_1', 'city_2', 'city_3', 'city_4', 'city_5']] = data['multilocation'].apply(extract_city_names).apply(pd.Series)

    data = data.drop(columns=['multilocation'])

    data.to_csv(os.path.join(os.path.dirname(__file__), 'job_offers.csv'), index=False)

if __name__ == '__main__':
    db = JobOffersDB(db_path)
    create_csv_from_document_db(db)