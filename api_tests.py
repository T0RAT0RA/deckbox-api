import os
import api
import unittest
from flask import json, jsonify

class FlaskrTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.test_username      = "deckbox_api"
        self.test_cardname      = "Ajani, Caller of the Pride"
        self.test_cardname_restricted = "Black Lotus"
        self.empty_deck_id      = "590775"
        self.standard_deck_id   = "590776"
        self.fixture_path       = "tests/fixtures/"

        self.app = api.app.test_client()

    def tearDown(self):
        pass

    def test_user_profile(self):
        url = '/api/users/' + self.test_username + '/'
        user_profile_actual     = self.getJsonFromApi(url)
        user_profile_expected   = self.getJsonFromFixture('user_profile.json')

        #Check if the last_seen_online value exist, not the value
        self.assertTrue("last_seen_online" in user_profile_actual)
        self.assertTrue("timestamp" in user_profile_actual["last_seen_online"])
        self.assertTrue("date" in user_profile_actual["last_seen_online"])

        user_profile_actual.pop("last_seen_online", None)
        self.assertDictEqual(user_profile_expected, user_profile_actual)

    def test_user_friends(self):
        url = '/api/users/' + self.test_username + '/friends/'
        user_friends_actual     = self.getJsonFromApi(url)
        user_friends_expected   = self.getJsonFromFixture('user_friends.json')

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
        user_sets_actual    = self.getJsonFromApi(url)
        user_sets_expected  = self.getJsonFromFixture('user_sets.json')

        self.assertEqual(len(user_sets_expected), len(user_sets_actual))

        self.assertListEqual(user_sets_expected["sets"], user_sets_actual["sets"])

    def test_user_inventory(self):
        url = '/api/users/' + self.test_username + '/inventory/'
        user_inventory_actual   = self.getJsonFromApi(url)
        user_inventory_expected = self.getJsonFromFixture('inventory.json')

        self.assertDictEqual(user_inventory_expected, user_inventory_actual)

    def test_user_inventory_ordered_by_edition_default(self):
        url = '/api/users/' + self.test_username + '/inventory/?order_by=edition'
        user_inventory_actual   = self.getJsonFromApi(url)
        user_inventory_expected = self.getJsonFromFixture('inventory_ordered_by_edition_default.json')

        self.assertDictEqual(user_inventory_expected, user_inventory_actual)

    def test_user_inventory_ordered_by_color_ascending(self):
        url = '/api/users/' + self.test_username + '/inventory/?order_by=color&order=asc'
        user_inventory_actual   = self.getJsonFromApi(url)
        user_inventory_expected = self.getJsonFromFixture('inventory_ordered_by_color_ascending.json')

        self.assertDictEqual(user_inventory_expected, user_inventory_actual)

    def test_user_inventory_ordered_by_name_descending(self):
        url = '/api/users/' + self.test_username + '/inventory/?order=desc'
        user_inventory_actual   = self.getJsonFromApi(url)
        user_inventory_expected = self.getJsonFromFixture('inventory_ordered_by_name_desc.json')

        self.assertDictEqual(user_inventory_expected, user_inventory_actual)

    def test_user_inventory_ordered_by_type_descending(self):
        url = '/api/users/' + self.test_username + '/inventory/?order_by=type&order=desc'
        user_inventory_actual   = self.getJsonFromApi(url)
        user_inventory_expected = self.getJsonFromFixture('inventory_ordered_by_type_descending.json')

    def test_user_inventory_ordered_by_cost_descending(self):
        url = '/api/users/' + self.test_username + '/inventory/?order_by=cost&order=desc'
        user_inventory_actual   = self.getJsonFromApi(url)
        user_inventory_expected = self.getJsonFromFixture('inventory_ordered_by_cost_descending.json')

        self.assertDictEqual(user_inventory_expected, user_inventory_actual)

    def test_user_wishlist(self):
        url = '/api/users/' + self.test_username + '/wishlist/'
        user_wishlist_actual   = self.getJsonFromApi(url)
        user_wishlist_expected = self.getJsonFromFixture('wishlist.json')

        self.assertDictEqual(user_wishlist_expected, user_wishlist_actual)

    def test_user_tradelist(self):
        url = '/api/users/' + self.test_username + '/tradelist/'
        user_tradelist_actual   = self.getJsonFromApi(url)
        user_tradelist_expected = self.getJsonFromFixture('tradelist.json')

        self.assertDictEqual(user_tradelist_expected, user_tradelist_actual)

    def test_empty_deck(self):
        rv = self.app.get('/api/users/' + self.test_username + "/sets/" + self.empty_deck_id + "/")
        empty_deck_actual   = json.loads(rv.data)
        empty_deck_expected = self.getJsonFromFixture('empty_deck.json')

        self.assertEqual(len(empty_deck_expected["cards"]), 0)
        self.assertEqual(empty_deck_expected["cards_count"]["cards"], empty_deck_actual["cards_count"]["cards"])
        self.assertEqual(empty_deck_expected["cards_count"]["distinct"], empty_deck_actual["cards_count"]["distinct"])
        self.assertEqual(empty_deck_expected["title"], empty_deck_actual["title"])

    def test_standard_deck(self):
        url = '/api/users/' + self.test_username + '/sets/' + self.standard_deck_id + '/'
        standard_deck_actual    = self.getJsonFromApi(url)
        standard_deck_expected  = self.getJsonFromFixture('standard_deck.json')

        self.assertEqual(len(standard_deck_expected["cards"]), len(standard_deck_actual["cards"]))
        self.assertEqual(standard_deck_expected["cards_count"]["cards"], standard_deck_actual["cards_count"]["cards"])
        self.assertEqual(standard_deck_expected["cards_count"]["distinct"], standard_deck_actual["cards_count"]["distinct"])
        self.assertEqual(standard_deck_expected["title"], standard_deck_actual["title"])

    def test_card(self):
        url = '/api/cards/' + self.test_cardname + '/'
        card_actual     = self.getJsonFromApi(url)
        card_expected   = self.getJsonFromFixture('card.json')

        self.assertDictEqual(card_expected["card"], card_actual["card"])

    def test_card_restricted(self):
        url = '/api/cards/' + self.test_cardname_restricted + '/'
        card_actual     = self.getJsonFromApi(url)
        card_expected   = self.getJsonFromFixture('card_restricted.json')

        self.assertDictEqual(card_expected["card"], card_actual["card"])

    def test_cards_no_filter(self):
        url = '/api/cards/'
        cards_actual     = self.getJsonFromApi(url)
        cards_expected   = self.getJsonFromFixture('cards_no_filters.json')

        #Remove number of page dependency
        cards_actual.pop("number_of_page", None)
        cards_expected.pop("number_of_page", None)
        self.assertDictEqual(cards_expected, cards_actual)

    def test_cards_text_filter_ordered_by_cost_ascending(self):
        filters = '?filters={"name":{"operator":"contains","value":"cent"},"rules_text":{"operator":"contains","value":"trample"},"subtype":{"operator":"not_contains","value":"human"},"cost":{"operator":"larger_than","value":"4"}}'
        url = '/api/cards/' + filters + "&order_by=cost&order=asc"
        cards_actual     = self.getJsonFromApi(url)
        cards_expected   = self.getJsonFromFixture('cards_text_filters_ordered_by_cost_ascending.json')

        self.assertDictEqual(cards_expected, cards_actual)


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

    def getJsonFromFixture(self, fixture_file):
        try:
            json_data = open(self.fixture_path + fixture_file)
            fixture_data = json.load(json_data)
            json_data.close()
        except IOError:
            self.fail('No fixture file found: ' + self.fixture_path + fixture_file)

        return fixture_data

if __name__ == '__main__':
    unittest.main()
