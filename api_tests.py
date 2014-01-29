import os
import api
import unittest
from flask import json, jsonify

class FlaskrTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_username       = "deckbox_api"
        cls.empty_deck_id       = "590775"
        cls.standard_deck_id    = "590776"

        cls.app = api.app.test_client()
        rv = cls.app.get('/api/users/' + cls.test_username + "/")
        cls.profile_data = json.loads(rv.data)
        cls.fixture_path = "tests/fixtures/"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_user_profile(self):
        user_profile_actual = self.profile_data

        json_data = open(self.fixture_path + 'user_profile.json')
        user_profile_expected = json.load(json_data)
        json_data.close()

        self.assertTrue("username" in user_profile_actual)
        self.assertEqual(user_profile_expected["username"], user_profile_actual["username"])
        self.assertTrue("bio" in user_profile_actual)
        self.assertEqual(user_profile_expected["bio"], user_profile_actual["bio"])
        self.assertTrue("feedback" in user_profile_actual)
        self.assertEqual(user_profile_expected["feedback"], user_profile_actual["feedback"])
        self.assertTrue("location" in user_profile_actual)
        self.assertEqual(user_profile_expected["location"], user_profile_actual["location"])
        self.assertTrue("will_trade" in user_profile_actual)
        self.assertEqual(user_profile_expected["will_trade"], user_profile_actual["will_trade"])

    def test_user_profile_default_sets(self):
        user_profile_actual    = self.profile_data
        user_profile_expected  = {
          "sets": [
            {"id": "590740", "name": "inventory"},
            {"id": "590741", "name": "tradelist"},
            {"id": "590742", "name": "wishlist"}
          ],
        }

        self.assertEqual(len(user_profile_expected["sets"]), 3)
        self.assertEqual(user_profile_expected["sets"][0]["id"], user_profile_actual["sets"][0]["id"])
        self.assertEqual(user_profile_expected["sets"][0]["name"], user_profile_actual["sets"][0]["name"])
        self.assertEqual(user_profile_expected["sets"][1]["id"], user_profile_actual["sets"][1]["id"])
        self.assertEqual(user_profile_expected["sets"][1]["name"], user_profile_actual["sets"][1]["name"])
        self.assertEqual(user_profile_expected["sets"][2]["id"], user_profile_actual["sets"][2]["id"])
        self.assertEqual(user_profile_expected["sets"][2]["name"], user_profile_actual["sets"][2]["name"])


    def test_user_sets(self):
        rv = self.app.get('/api/users/' + self.test_username + "/sets/")
        user_sets_actual = json.loads(rv.data)

        json_data = open(self.fixture_path + 'user_sets.json')
        user_sets_expected = json.load(json_data)
        json_data.close()

        self.assertEqual(len(user_sets_expected), len(user_sets_actual))

        self.assertListEqual(user_sets_expected["sets"], user_sets_actual["sets"])

    def test_user_inventory(self):
        rv = self.app.get('/api/users/' + self.test_username + "/sets/590740/")
        user_inventory_actual = json.loads(rv.data)

        json_data = open(self.fixture_path + 'inventory.json')
        user_inventory_expected = json.load(json_data)
        json_data.close()

        self.assertEqual(len(user_inventory_expected["cards"]), len(user_inventory_actual["cards"]))
        self.assertEqual(user_inventory_expected["number_of_page"], user_inventory_actual["number_of_page"])
        self.assertEqual(user_inventory_expected["page"], user_inventory_actual["page"])
        self.assertEqual(user_inventory_expected["title"], user_inventory_actual["title"])

        self.assertListEqual(user_inventory_expected["cards"], user_inventory_actual["cards"])

    def test_empty_deck(self):
        rv = self.app.get('/api/users/' + self.test_username + "/sets/" + self.empty_deck_id + "/")
        empty_deck_actual = json.loads(rv.data)

        json_data = open(self.fixture_path + 'empty_deck.json')
        empty_deck_expected = json.load(json_data)
        json_data.close()

        self.assertEqual(len(empty_deck_expected["cards"]), 0)
        self.assertEqual(empty_deck_expected["cards_count"]["cards"], empty_deck_actual["cards_count"]["cards"])
        self.assertEqual(empty_deck_expected["cards_count"]["distinct"], empty_deck_actual["cards_count"]["distinct"])
        self.assertEqual(empty_deck_expected["title"], empty_deck_actual["title"])

    def test_standard_deck(self):
        rv = self.app.get('/api/users/' + self.test_username + "/sets/" + self.standard_deck_id + "/")
        standard_deck_actual = json.loads(rv.data)

        json_data = open(self.fixture_path + 'standard_deck.json')
        standard_deck_expected = json.load(json_data)
        json_data.close()

        self.assertEqual(len(standard_deck_expected["cards"]), len(standard_deck_actual["cards"]))
        self.assertEqual(standard_deck_expected["cards_count"]["cards"], standard_deck_actual["cards_count"]["cards"])
        self.assertEqual(standard_deck_expected["cards_count"]["distinct"], standard_deck_actual["cards_count"]["distinct"])
        self.assertEqual(standard_deck_expected["title"], standard_deck_actual["title"])

if __name__ == '__main__':
    unittest.main()
