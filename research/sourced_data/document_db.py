"""
This module contains the JobOffersDB class which is used to store job offers in a TinyDB database.

The JobOffersDB class is used to store job offers in a TinyDB database. The database is used to store job offers that are scraped from internet websites. The class contains methods for inserting, updating and deleting job offers from the database. It also contains methods for searching for job offers in the database based on different criteria.

How to use the class:

    1. Create an instance of the class by passing the path to the database file as an argument.
    2. Use the methods of the class to insert, update, delete and search for job offers in the database.

Example:

    from document_db import JobOffersDB
    # create an instance of the class
    job_offers_db = JobOffersDB('job_offers_db.json')
    # insert a job offer into the database
    job_offers_db.insert_job_offer(job_offer)
"""

from tinydb import TinyDB, Query
from typing import List, Dict, Mapping, cast
import pandas as pd


class JobOffersDB:

    # TinyDB query object used to search for job offers in the database
    JobOffer = Query()

    def __init__(self, db_path: str):
        self.db = TinyDB(db_path)

    # CRUD
    def insert_job_offer(self, job_offer: Dict) -> int:
        """
        insert single job offer into db

        :param job_offer: job offert dict
        :return: ID of inserted job offer
        """
        try:
            return self.db.insert(job_offer)
        except Exception as e:
            print(f"Error inserting job offer: {e}")
            return -1

    # CRUD
    def insert_multiple_job_offers(self, job_offers: List[Dict]) -> List[int]:
        """
        insert multiple job offers into db

        :param job_offers: list of dicts with job offers
        :return: list of IDs of inserted job offers
        """
        try:
            inserted_ids = []
            for job_offer in job_offers:
                inserted_id = self.db.insert(job_offer)
                inserted_ids.append(inserted_id)
            return inserted_ids
        except Exception as e:
            print(f"Error inserting multiple job offers: {e}")
            return []

    # CRUD
    def update_job_offer(self, job_offer_id: int, updated_data: Dict) -> bool:
        """
        Update a job offer in the TinyDB database based on the job_offer_id.

        :param job_offer_id: ID of job offer to be updated
        :param updated_data: dict containing the updated job offer
        :return: True if job offer was updated, False if not
        """
        try:
            return bool(self.db.update(updated_data, self.JobOffer.id == job_offer_id))
        except Exception as e:
            print(f"Error updating job offer: {e}")
            return False

    # Analytics
    def get_job_offers_by_salary_range(self, salary_from: int, salary_to: int) -> pd.DataFrame:
        """
        Get all job offers with a salary between given range

        :param salary_from: lower limit of the salary
        :param salary_to: upper limit 
        :return: df of searched job offers
        """

        job_offers = self.db.search(
            self.JobOffer['employment_types'].any(
                lambda e: e['salary']
                and e['salary'].get('from', 0) >= salary_from
                and e['salary'].get('to', 0) <= salary_to
            )
        )

        return pd.DataFrame(job_offers)

    # Analytics
    def get_job_offers_by_title_and_salary_range(self, title: str, salary_from: int, salary_to: int) -> pd.DataFrame:
        """
        Get all job offers with the given title and salary range

        :param title: offer title to search for
        :param salary_from: lower limit of the salary
        :param salary_to: upper limit
        :return: df of searched job offers
        """

        job_offers = self.db.search(
            (self.JobOffer['title'] == title) & self.JobOffer['employment_types'].any(
                lambda e: e['salary']
                and e['salary'].get('from', 0) >= salary_from
                and e['salary'].get('to', 0) <= salary_to
            )
        )
        return pd.DataFrame(job_offers)

    # Analytics
    def get_all_job_offers(self) -> pd.DataFrame:
        """
        return all job offers in the database as a pandas dataframe

        :return: df of all job offers
        """
        all_job_offers = self.db.all()
        if all_job_offers:
            columns = list(all_job_offers[0].keys())
            df = pd.DataFrame(all_job_offers, columns=columns)
            return df
        else:
            return pd.DataFrame()

    # Analytics
    def get_number_of_job_offers(self) -> int:
        """
        return number of job offers in the database
        """
        return len(self.db.all())

    def get_job_offer_by_id(self, job_offer_id: int) -> Dict:
        """
        Get a job offer from the database based on the job_offer_id.

        :param job_offer_id: ID of job offer to be returned
        :return: dict with job offer
        """
        result = self.db.search(self.JobOffer.id == job_offer_id)
        if result:
            return result[0]
        else:
            return None

    # Analytics
    def count_offers_with_skill(self, skill: str) -> int:
        """
        Count number of job offers that contain the given skill

        :param skill: skill to search for
        :return: number of job offers with the given skill
        """
        return len(self.db.search(self.JobOffer['skills'].any(lambda s: s['name'] == skill)))

    # CRUD
    def delete_job_offer(self, job_offer_id: str) -> bool:
        """
        Delete a job offer from the database based on the job_offer_id.

        :param job_offer_id: ID of job offer to be deleted
        :return: True if job offer was deleted, False if not
        """
        return bool(self.db.remove(self.JobOffer.id == job_offer_id))

    # CRUD
    def delete_all_job_offers(self) -> None:
        """
        Delete all job offers from the database
        """
        self.db.truncate()

    def close(self) -> None:
        """
        Close the database connection
        """
        self.db.close()
