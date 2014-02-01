import os
import api
import unittest
from flask import json, jsonify

class FlaskrTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.test_username      = "deckbox_api"
        self.test_cardname      = "Ajani, Caller of the Pride"
        self.empty_deck_id      = "590775"
        self.standard_deck_id   = "590776"
        self.fixture_path       = "tests/fixtures/"

        self.app = api.app.test_client()

    def tearDown(self):
        pass

    def test_user_profile(self):
        url = '/api/users/' + self.test_username + '/'
        user_profile_actual = self.getJsonFromApi(url)

        json_data = open(self.fixture_path + 'user_profile.json')
        user_profile_expected = json.load(json_data)
        json_data.close()

        #Check if the last_seen_online value exist, not the value
        self.assertTrue("last_seen_online" in user_profile_actual)
        self.assertTrue("timestamp" in user_profile_actual["last_seen_online"])
        self.assertTrue("date" in user_profile_actual["last_seen_online"])

        user_profile_actual.pop("last_seen_online", None)
        self.assertDictEqual(user_profile_expected, user_profile_actual)

    def test_user_friends(self):
        url = '/api/users/' + self.test_username + '/friends/'
        user_friends_actual = self.getJsonFromApi(url)

        json_data = open(self.fixture_path + 'user_friends.json')
        user_friends_expected = json.load(json_data)
        json_data.close()

        self.assertDictEqual(user_friends_expected, user_friends_actual)

    def test_user_profile_default_sets(self):
        url = '/api/users/' + self.test_username + '/'
        user_profile_actual = self.getJsonFromApi(url)

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
        url = '/api/users/' + self.test_username + '/sets/'
        user_sets_actual = self.getJsonFromApi(url)

        json_data = open(self.fixture_path + 'user_sets.json')
        user_sets_expected = json.load(json_data)
        json_data.close()

        self.assertEqual(len(user_sets_expected), len(user_sets_actual))

        self.assertListEqual(user_sets_expected["sets"], user_sets_actual["sets"])

    def test_user_inventory(self):
        url = '/api/users/' + self.test_username + '/inventory/'
        user_inventory_actual = self.getJsonFromApi(url)

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
        url = '/api/users/' + self.test_username + '/sets/' + self.standard_deck_id + '/'
        standard_deck_actual = self.getJsonFromApi(url)

        json_data = open(self.fixture_path + 'standard_deck.json')
        standard_deck_expected = json.load(json_data)
        json_data.close()

        self.assertEqual(len(standard_deck_expected["cards"]), len(standard_deck_actual["cards"]))
        self.assertEqual(standard_deck_expected["cards_count"]["cards"], standard_deck_actual["cards_count"]["cards"])
        self.assertEqual(standard_deck_expected["cards_count"]["distinct"], standard_deck_actual["cards_count"]["distinct"])
        self.assertEqual(standard_deck_expected["title"], standard_deck_actual["title"])

    def test_card(self):
        url = '/api/cards/' + self.test_cardname + '/'
        card_actual = self.getJsonFromApi(url)

        json_data = open(self.fixture_path + 'card.json')
        card_expected = json.load(json_data)
        json_data.close()

        self.assertDictEqual(card_expected["card"], card_actual["card"])


    #-------------------------
    #  HELPERS
    #-------------------------
    def getJsonFromApi(self, url):
        page = self.app.get(url)
        try:
            json_data = json.loads(page.data)
        except ValueError:
            self.fail('No JSON found from URL: ' + url + "\n" + page.data)

        return json_data

if __name__ == '__main__':
    unittest.main()
