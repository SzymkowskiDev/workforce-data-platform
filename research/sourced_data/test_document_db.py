import unittest
from document_db import JobOffersDB
import random
from sample_data import job_offer_sample
import pandas as pd

class TestJobOffersDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # set up the main database and the test database
        cls.job_offers_db = JobOffersDB('document_db.json')
        cls.test_job_offers_db = JobOffersDB('test_document_db.json')
    
    def setUp(self):
        # Select 20 random job offers from the existing database
        all_job_offers = self.job_offers_db.get_all_job_offers()
        random_job_offers = all_job_offers.sample(n=20)
        random_job_offers_list = random_job_offers.to_dict('records')

        # insert the random job offers into the test database
        self.test_job_offers_db.insert_multiple_job_offers(random_job_offers_list)

        # Store the ID of one of the randomly selected job offers
        self.random_job_offer_id = random_job_offers_list[0]['id']

        self.job_offer_sample = job_offer_sample


    def test_insert_job_offer(self):
        self.test_job_offers_db.insert_job_offer(self.job_offer_sample)
        job_offer = self.test_job_offers_db.get_job_offer_by_id(self.job_offer_sample['id'])
        self.assertEqual(job_offer, self.job_offer_sample)

    def test_get_job_offer_by_id(self):
        job_offer = self.test_job_offers_db.get_job_offer_by_id(self.random_job_offer_id)
        self.assertIsNotNone(job_offer)

    def test_get_all_job_offers(self):
        job_offers_df = self.test_job_offers_db.get_all_job_offers()
        self.assertEqual(job_offers_df.shape[0], 20)

    def test_update_job_offer(self):
        # insert job offer and update its title
        self.test_job_offers_db.insert_job_offer(self.job_offer_sample)
        updated_title = "Updated IT Business Analyst"
        self.job_offer_sample["title"] = updated_title
        self.test_job_offers_db.update_job_offer(self.job_offer_sample["id"], self.job_offer_sample)

        # check if the title was updated
        updated_job_offer = self.test_job_offers_db.get_job_offer_by_id(self.job_offer_sample["id"])
        self.assertEqual(updated_job_offer["title"], updated_title)

    def test_delete_job_offer(self):
        # insert job offer -> then delete it
        self.test_job_offers_db.insert_job_offer(self.job_offer_sample)
        self.test_job_offers_db.delete_job_offer(self.job_offer_sample["id"])

        # check if the job offer was deleted
        deleted_job_offer = self.test_job_offers_db.get_job_offer_by_id(self.job_offer_sample["id"])
        self.assertIsNone(deleted_job_offer)

    def test_insert_multiple_job_offers(self):
        new_job_offers = [self.job_offer_sample, self.job_offer_sample, self.job_offer_sample, self.job_offer_sample,  self.job_offer_sample]
        self.test_job_offers_db.insert_multiple_job_offers(new_job_offers)

        # Check if the new job offers have been added
        all_job_offers = self.test_job_offers_db.get_all_job_offers()
        self.assertEqual(len(all_job_offers), 25)

    def test_get_job_offers_by_salary_range(self):
        lower_bound = 15000
        upper_bound = 20000

        salary_range_job_offers = self.test_job_offers_db.get_job_offers_by_salary_range(lower_bound, upper_bound)
        for _, job_offer in salary_range_job_offers.iterrows():
            for emplyment_type in job_offer["employment_types"]:
                if emplyment_type["salary"]:
                    salary_from = emplyment_type["salary"].get("from",0)
                    salary_to = emplyment_type["salary"].get("to",0)
                    self.assertTrue(
                        lower_bound <= salary_from <= upper_bound,
                        f"Job offer salary_from {salary_from} is not within the specified range."
                    )
                    self.assertTrue(
                        lower_bound <= salary_to <= upper_bound,
                        f"Job offer salary_to {salary_to} is not within the specified range."
                    )
                

    def tearDown(self):
        # Clear the test database after each test
        all_job_offers_df = self.test_job_offers_db.get_all_job_offers()
        for _, job_offer in all_job_offers_df.iterrows():
            if isinstance(job_offer, pd.Series):
                self.test_job_offers_db.delete_job_offer(job_offer["id"])

    @classmethod
    def tearDownClass(cls):
        # Close the test database
        cls.test_job_offers_db.close()

    
if __name__ == '__main__':
    unittest.main()
