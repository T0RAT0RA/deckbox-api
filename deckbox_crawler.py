import re
from pyquery import PyQuery

class DeckboxCrawler:
    _DECKBOX_DOMAIN = "http://deckbox.org"

    def __init__(self, username):
        url = self._DECKBOX_DOMAIN + "/users/" + username

        self.log("Get user profile page: " + url)
        self._page = PyQuery(url=url)

    def getUserProfile(self):
        fields = [h.text() for h in self._page("#section_profile dd").items()]
        fields[0] = re.search(', ([0-9]+), ', fields[0]).group(1)
        return fields

    def getUserSets(self, set_id = None):
        sets = {}
        for i, a in enumerate(self._page("#section_mtg .submenu_entry a.simple").items()):
            current_set_id   = a.attr("href").replace("/sets/", "")

            if i == 0:
                current_set_name = "inventory"
            elif i == 1:
                current_set_name = "tradelist"
            elif i == 2:
                current_set_name = "wishlist"
            else:
                current_set_name = a.attr("data-title")

            sets[current_set_name] = current_set_id

            if set_id and set_id == current_set_id:
                return sets[set_id]

        return sets

    def getUserSetCards(self, set_id, page = 1):
        self.log("getUserSetCards(" + set_id + ", " + str(page) + ")")
        set_link = self.getUserSets(set_id)
        set_url  = self._DECKBOX_DOMAIN + set_link + "?p=" + str(page)
        return self.getCardsFromPage(set_url)

    #################################
    #  HELPERS                      #
    #################################
    def log(self, message):
        print "LOG - " + message

    def getCardsFromPage(self, page_url):
        self.log("Get cards from url: " + page_url)

        page = PyQuery(url=page_url)

        pagination  = page("#set_cards_table .pagination_controls:first span").text()
        m = re.search('([0-9]+)[^0-9]*([0-9]+)', pagination)
        current_page    = m.group(1)
        number_of_pages = m.group(2)
        cards = [tr.text() for tr in page("#set_cards_table_details tr:gt(1) a").items()]
        cards_per_page = len(cards)

        return {"cards": cards, "cards_per_page": cards_per_page, "page": current_page, "number_of_page": number_of_pages}
