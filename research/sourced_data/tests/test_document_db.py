import unittest
import random
from sample_data import job_offer_sample
import pandas as pd
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from document_db import JobOffersDB


class TestJobOffersDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # set up the main database and the test database
        main_db_path = pathlib.Path(__file__).parent.parent / 'document_db.json'
        cls.job_offers_db = JobOffersDB(str(main_db_path))
        
        test_db_path = pathlib.Path(__file__).parent / 'test_document_db.json'
        cls.test_job_offers_db = JobOffersDB(str(test_db_path))
    
    def setUp(self):
        # Select 20 random job offers from the existing database
        all_job_offers = self.job_offers_db.get_all_job_offers()
        random_job_offers = all_job_offers.sample(n=20)
        random_job_offers_list = random_job_offers.to_dict('records')

        # insert the random job offers into the test database
        self.test_job_offers_db.insert_multiple_job_offers(random_job_offers_list)

        # Store the ID of one of the randomly selected job offers
        self.random_job_offer_id = random_job_offers_list[0]['id']

        # Store a sample job offer
        self.job_offer_sample = job_offer_sample

    # 1
    def test_insert_job_offer(self):
        self.test_job_offers_db.insert_job_offer(self.job_offer_sample)
        job_offer = self.test_job_offers_db.get_job_offer_by_id(self.job_offer_sample['id'])
        self.assertEqual(job_offer, self.job_offer_sample)

    # 2
    def test_get_job_offer_by_id(self):
        job_offer = self.test_job_offers_db.get_job_offer_by_id(self.random_job_offer_id)
        self.assertIsNotNone(job_offer)

    # 3
    def test_get_all_job_offers(self):
        job_offers_df = self.test_job_offers_db.get_all_job_offers()
        self.assertEqual(job_offers_df.shape[0], 20)

    # 4
    def test_update_job_offer(self):
        # insert job offer and update its title
        self.test_job_offers_db.insert_job_offer(self.job_offer_sample)
        updated_title = "Updated IT Business Analyst"
        self.job_offer_sample["title"] = updated_title
        self.test_job_offers_db.update_job_offer(self.job_offer_sample["id"], self.job_offer_sample)

        # check if the title was updated
        updated_job_offer = self.test_job_offers_db.get_job_offer_by_id(self.job_offer_sample["id"])
        self.assertEqual(updated_job_offer["title"], updated_title)

    # 5
    def test_delete_job_offer(self):
        # insert job offer -> then delete it
        self.test_job_offers_db.insert_job_offer(self.job_offer_sample)
        self.test_job_offers_db.delete_job_offer(self.job_offer_sample["id"])

        # check if the job offer was deleted
        deleted_job_offer = self.test_job_offers_db.get_job_offer_by_id(self.job_offer_sample["id"])
        self.assertIsNone(deleted_job_offer)

    # 6
    def test_insert_multiple_job_offers(self):
        new_job_offers = [self.job_offer_sample, self.job_offer_sample, self.job_offer_sample, self.job_offer_sample,  self.job_offer_sample]
        self.test_job_offers_db.insert_multiple_job_offers(new_job_offers)

        # Check if the new job offers have been added
        all_job_offers = self.test_job_offers_db.get_all_job_offers()
        self.assertEqual(len(all_job_offers), 25)

    # 7
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

    # 8
    def test_get_job_offers_by_title_and_salary_range(self):
        lower_bound = 15000
        upper_bound = 20000
        self.test_job_offers_db.insert_job_offer(self.job_offer_sample)
        title = self.job_offer_sample["title"]

        salary_range_job_offers = self.test_job_offers_db.get_job_offers_by_title_and_salary_range(title, lower_bound, upper_bound)
        for _, job_offer in salary_range_job_offers.iterrows():
            self.assertEqual(job_offer["title"], title)
            for emplyment_type in job_offer["employment_types"]:
                if emplyment_type["salary"]:
                    salary_from = emplyment_type["salary"].get("from",0)
                    salary_to = emplyment_type["salary"].get("to",0)
                    self.assertTrue(
                        lower_bound <= salary_from <= upper_bound,
                        f"Job offer salary_from {salary_from} is not within the specifiedrange."
                    )
                    self.assertTrue(
                        lower_bound <= salary_to <= upper_bound,
                        f"Job offer salary_to {salary_to} is not within the specified range."
                    )
                
    # 9
    def test_get_number_of_job_offers(self):
        self.assertEqual(self.test_job_offers_db.get_number_of_job_offers(), 20)

    # 10
    def test_count_offers_with_skill(self):
        skill = "Python"
        offers_with_skill_count = self.test_job_offers_db.count_offers_with_skill(skill)

        self.assertGreater(offers_with_skill_count, 0)

        # now add our sample job offer with the skill and check if the count increased
        self.test_job_offers_db.insert_job_offer(self.job_offer_sample)
        offers_with_skill_count_after_insert = self.test_job_offers_db.count_offers_with_skill(skill)
        self.assertEqual(offers_with_skill_count_after_insert, offers_with_skill_count + 1)

    # 11
    def test_delete_all_job_offers(self):
        self.test_job_offers_db.delete_all_job_offers()
        self.assertEqual(self.test_job_offers_db.get_number_of_job_offers(), 0)

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
