import os
import api
import unittest
from flask import json, jsonify

class FlaskrTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = api.app.test_client()
        cls.test_username = "deckbox_api"
        rv = cls.app.get('/api/' + cls.test_username + "/")
        cls.profile_data = json.loads(rv.data)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_api_profile_infos(self):
        user_profile_actual    = self.profile_data
        user_profile_expected  = {
          "bio": "This profile is used to test the Deckbox non-official API: http://deckbox-api.herokuapp.com/",
          "feedback": "0 (100% positive)",
          "last_seen_online": {
            "date": "2014-01-28 00:00:19",
            "timestamp": "1390885219"
          },
          "location": "Canada - Montreal",
          "username": "John Doe",
          "will_trade": "My Continent"
        }

        self.assertTrue("username" in user_profile_actual, "username doesn't exist.")
        self.assertEqual(user_profile_expected["username"], user_profile_actual["username"], "username doesn't match.")
        self.assertTrue("bio" in user_profile_actual, "bio doesn't exist.")
        self.assertEqual(user_profile_expected["bio"], user_profile_actual["bio"], "bio doesn't match.")
        self.assertTrue("feedback" in user_profile_actual, "username doesn't exist.")
        self.assertEqual(user_profile_expected["feedback"], user_profile_actual["feedback"], "feedback doesn't match.")
        self.assertTrue("location" in user_profile_actual, "username doesn't exist.")
        self.assertEqual(user_profile_expected["location"], user_profile_actual["location"], "location doesn't match.")
        self.assertTrue("will_trade" in user_profile_actual, "username doesn't exist.")
        self.assertEqual(user_profile_expected["will_trade"], user_profile_actual["will_trade"], "will_trade field doesn't match.")

    def test_api_profile_default_sets(self):
        user_profile_actual    = self.profile_data
        user_profile_expected  = {
          "sets": [
            {"id": "590740", "name": "inventory"},
            {"id": "590741", "name": "tradelist"},
            {"id": "590742", "name": "wishlist"}
          ],
        }

        self.assertEqual(len(user_profile_expected["sets"]), 3, "Sets count doesn't match.")
        self.assertEqual(user_profile_expected["sets"][0]["id"], user_profile_actual["sets"][0]["id"], "Inventory id doesn't match.")
        self.assertEqual(user_profile_expected["sets"][0]["name"], user_profile_actual["sets"][0]["name"], "Inventory name doesn't match.")
        self.assertEqual(user_profile_expected["sets"][1]["id"], user_profile_actual["sets"][1]["id"], "Tradelist id doesn't match.")
        self.assertEqual(user_profile_expected["sets"][1]["name"], user_profile_actual["sets"][1]["name"], "Tradelist name doesn't match.")
        self.assertEqual(user_profile_expected["sets"][2]["id"], user_profile_actual["sets"][2]["id"], "Wishlist id doesn't match.")
        self.assertEqual(user_profile_expected["sets"][2]["name"], user_profile_actual["sets"][2]["name"], "Wishlist name doesn't match.")

    def test_api_empty_deck(self):
        rv = self.app.get('/api/' + self.test_username + "/set/590775/")
        empty_deck_actual = json.loads(rv.data)

        empty_deck_expected  = {
          "cards": [],
          "cards_count": {
            "cards": 0,
            "distinct": 0
          },
          "title": "Empty deck"
        }

        self.assertEqual(len(empty_deck_expected["cards"]), 0, "Empty deck should have no cards.")
        self.assertEqual(empty_deck_expected["cards_count"]["cards"], empty_deck_actual["cards_count"]["cards"], "Cards count doesn't match.")
        self.assertEqual(empty_deck_expected["cards_count"]["distinct"], empty_deck_actual["cards_count"]["distinct"], "Distinct cards count doesn't match.")
        self.assertEqual(empty_deck_expected["title"], empty_deck_actual["title"], "title count doesn't match.")

if __name__ == '__main__':
    unittest.main()
