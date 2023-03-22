from tinydb import TinyDB, Query
from typing import List, Dict
import pandas as pd

class JobOffersDB:

    JobOffer = Query()

    def __init__(self, db_path: str):
        self.db = TinyDB(db_path)

    def insert_job_offer(self, job_offer: Dict) -> int:
        """
        insert single job offer into db
        
        :param job_offer: job offert dict
        :return: ID of inserted job offer
        """
        return self.db.insert(job_offer)
    
    def insert_multiple_job_offers(self, job_offers: List[Dict]) -> List[int]:
        """
        insert multiple job offers into db
        
        :param job_offers: list of dicts with job offers
        :return: list of IDs of inserted job offers
        """
        return self.db.insert_multiple(job_offers)
    
    def update_job_offer(self, job_offer_id: int, updated_data: Dict) -> bool:
        """
        Update a job offer in the TinyDB database based on the job_offer_id.
        
        :param job_offer_id: ID of job offer to be updated
        :param updated_data: dict containing the updated job offer
        :return: True if job offer was updated, False if not
        """
        return bool(self.db.update(updated_data, self.JobOffer.id == job_offer_id))
    
    def get_job_offers_by_salary_range(self, salary_from: int, salary_to: int) -> pd.DataFrame:
        """
        Get all job offers with a salary between given range

        :param salary_from: lower limit of the salary
        :param salary_to: upper limit
        :return: df of searched job offers
        """

        job_offers = self.db.search(self.JobOffer['employment_types'].any(lambda e: e['salary'] and e['salary'].get('from', 0) >= salary_from and e['salary'].get('to', 0) <= salary_to))
        
        return pd.DataFrame(job_offers)

    def get_job_offers_by_title_and_salary_range(self, title: str, salary_from: int, salary_to: int) -> pd.DataFrame:
        """
        Get all job offers with the given title and salary range

        :param title: offer title to search for
        :param salary_from: lower limit of the salary
        :param salary_to: upper limit
        :return: df of searched job offers
        """

        job_offers = self.db.search((self.JobOffer['title'] == title) & self.JobOffer['employment_types'].any(lambda e: e['salary'] and e['salary'].get('from', 0) >= salary_from and e['salary'].get('to', 0) <= salary_to))
        return pd.DataFrame(job_offers)
    
    def get_all_job_offers(self) -> pd.DataFrame:
        """
        return all job offers in the database as a pandas dataframe

        :return: df of all job offers
        """
        return pd.DataFrame(self.db.all())
    
    def get_number_of_job_offers(self) -> int:
        # returns number of job offers in the database
        return len(self.db.all())
    
    def count_offers_with_skill(self, skill: str) -> int:
        """
        Count number of job offers that contain the given skill

        :param skill: skill to search for
        :return: number of job offers with the given skill
        """
        return len(self.db.search(self.JobOffer['skills'].any(lambda s: s['name'] == skill)))
    
    def delete_job_offer(self, job_offer_id: str) -> bool:
        return bool(self.db.remove(self.JobOffer.id == job_offer_id))
