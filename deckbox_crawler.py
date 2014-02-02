import re, datetime, urllib
from pyquery import PyQuery

class DeckboxCrawler:
    _HTTP           = "http://"
    _DECKBOX_DOMAIN = "deckbox.org"

    _ORDER_BY_PARAMETER = 's'
    _ORDER_BY_LIST  = {
        'name': 'n',
        'edition': 'b',
        'price': {
            'inventory': 'j',
            'deck': 'i'
        },
        'type': 't',
        'cost': 'c',
        'color': 'a'
    }

    _ORDER_PARAMETER    = 'o'
    _ORDER_LIST     = {
        'asc': 'a',
        'desc': 'd'
    }

    def __init__(self, query_type = None, query_value = None):

        if query_type == "profile":
            query_url = "/users/"
        elif query_type == "card":
            query_url = "/mtg/"
        else:
            query_url = ""

        page_url = self._HTTP + urllib.quote(self._DECKBOX_DOMAIN + query_url + query_value)
        self.getPage(page_url)

    def getUserProfile(self):
        fields = [h.text() for h in self._page("#section_profile dd").items()]
        fields[0] = re.search(', ([0-9]+), ', fields[0]).group(1)

        return {
            "last_seen_online": {
                "timestamp": fields[0],
                "date": datetime.datetime.fromtimestamp(int(fields[0])).strftime('%Y-%m-%d %H:%M:%S')
            },
            "username": fields[1],
            "location": fields[2],
            "picture": self._HTTP + self._DECKBOX_DOMAIN + self._page("#profile_page_wrapper .friend_img").attr("src"),
            "feedback": fields[3],
            "will_trade": fields[4],
            "bio": self._page(".user_bio").text(),
        }

    def getUserFriends(self):
        self.getPage(self._page_url + "/friends")

        friends = []

        #Get all sets
        for i, profiles in enumerate(self._page("#all_friends .profile_wrapper").items()):
            current_friend = {}
            current_friend["username"] = profiles.find(".data a").attr("href").replace("/users/", "")
            current_friend["picture"] = self._HTTP + self._DECKBOX_DOMAIN + profiles.find(".friend_img").attr("src")

            friends.append(current_friend)

        return friends

    def getUserSets(self, set_id = None):
        sets = []

        #Get all sets
        for i, a in enumerate(self._page("#section_mtg .submenu_entry a.simple").items()):
            current_set = {}
            current_set["id"] = a.attr("href").replace("/sets/", "")

            if i == 0:
                current_set["name"] = "inventory"
            elif i == 1:
                current_set["name"] = "tradelist"
            elif i == 2:
                current_set["name"] = "wishlist"
            else:
                current_set["name"] = a.attr("data-title")

            if set_id and (set_id == current_set["id"] or set_id == current_set["name"]):
                return current_set

            sets.append(current_set)

        # Should already have returned the specified set
        if set_id:
            return None

        return sets

    def getUserSetCards(self, set_id, page = 1, order_by = 'name', order = 'asc'):
        set_object = self.getUserSets(set_id)

        if set_object == None:
            return {"status": "error", "description": "The user doesn't have the specified set."}

        parameters = {}
        parameters['p'] = str(page)
        parameters[self._ORDER_BY_PARAMETER] = self._ORDER_BY_LIST[order_by] if order_by in self._ORDER_BY_LIST else 'name'
        parameters[self._ORDER_PARAMETER] = self._ORDER_LIST[order] if order in self._ORDER_LIST else 'asc'

        set_url  = self._HTTP + self._DECKBOX_DOMAIN + "/sets/" + set_object["id"] + "?" + urllib.urlencode(parameters)
        self.getPage(set_url)
        return self.getCardsFromPage()


    def getCard(self):
        card = {}
        card["name"]    = self._page(".section_title:first").text()
        card_types = re.split(r'\s+-\s+', self._page(".card_properties tr:eq(3) td:last").text())
        card["type"]    = card_types[0]
        card["subtype"] = re.split(r'\s', card_types[1]) if len(card_types) > 1 else ""
        card_cost = []
        for img in self._page(".card_properties tr:eq(2) td:last img").items():
            card_cost.append(re.sub("(mtg_mana |mtg_mana_)", "", img.attr("class")))
        card["cost"]    = "".join(card_cost)
        card["editions"] = []
        for edition in self._page(".card_properties tr:eq(1) td:last img").items():
            card["editions"].append({
                "code": re.search(".*/(.*)_.\.jpg$", edition.attr("src")).group(1),
                "name": edition.attr("data-title")
            })

        return card

    #-------------------------
    #  HELPERS
    #-------------------------
    def log(self, message):
        print "LOG - " + message

    def getPage(self, page_url):
        self.log("Get cards from url: " + page_url)
        self._page_url = page_url
        self._page = PyQuery(url=page_url)

    def getCardsFromPage(self):
        is_deck_page    = True if self._page(".main.deck") else False
        cards           = self.getCardsFromTable(is_deck_page)

        #-------------------------
        # DECK PAGES
        #-------------------------
        if is_deck_page:
            title           = self._page(".section_title span:first").text()
            cards_count     = {"cards": 0, "distinct": 0}
            for script in self._page("script").items():
                m = re.search("total_card_count[^_s][^0-9]*([0-9]+) cards, ([0-9]+) distinct", script.text())
                if m != None and m.group(1) and m.group(2):
                    cards_count["cards"]    = int(m.group(1))
                    cards_count["distinct"] = int(m.group(2))

            return {"title": title, "cards": cards, "cards_count": cards_count}

        #-------------------------
        # DEFAULT SETS PAGES
        #-------------------------
        else:
            pagination      = self._page("#set_cards_table .pagination_controls:first span").text()
            m = re.search('([0-9]+)[^0-9]*([0-9]+)', pagination)
            card_table_id   = "#set_cards_table_details"
            current_page    = m.group(1)
            number_of_pages = m.group(2)
            title           = self._page(".section_title span:first").text()

            return {"title": title, "cards": cards, "page": current_page, "number_of_page": number_of_pages}

    #-------------------------
    # Cards Parser
    #-------------------------
    def getCardsFromTable(self, isDeckTable = False):
        cards = []

        # Parse cards on deck page
        if isDeckTable:
            for tr in self._page(".main.deck tr").items():
                if tr.attr("id") == None:
                    continue

                '''
                Deck card HTML example:
                <tr id="13392">
                    <td id="card_count_13392" class="card_count">4</td>
                    <td class="card_name">
                      <div class="relative">
                        <a class="simple" target="_blank" href="http://deckbox.org/mtg/Armed // Dangerous">
                            Armed // Dangerous
                        </a>
                      </div>
                    </td>
                    <td><span>Sorcery</span></td>
                    <td class="card_cost">
                        <img class="mtg_mana mtg_mana_1" src="/images/icon_spacer.gif">
                        <img class="mtg_mana mtg_mana_R" src="/images/icon_spacer.gif">
                    </td>
                    <td class="center price">
                        <span data-title="$0.04 / $0.19 / $0.95 / $0.95">$0.19</span>
                    </td>
                </tr>
                '''

                card = {}
                card["count"]   = tr.find("td.card_count").text()
                card["name"]    = tr.find("a").text()
                card_types = re.split(r'\s+-\s+', tr.find("td").eq(2).find("span").text())
                card["types"]   = re.split(r'\s', card_types[0]) if len(card_types) > 1 else card_types
                card["subtypes"]= re.split(r'\s', card_types[1]) if len(card_types) > 1 else []
                card_cost = []
                for img in tr.find("td.card_cost img").items():
                    card_cost.append(re.sub("(mtg_mana |mtg_mana_)", "", img.attr("class")))
                card["cost"]    = "".join(card_cost)

                cards.append(card)

        # Parse cards on default set (inventory, wishlist, tradelist) page
        else:
            for tr in self._page("#set_cards_table_details tr").items():
                if tr.attr("id") == None:
                    continue

                '''
                Default set card HTML example:
                <tr id="734306" class="even">
                    <td id="card_count_734306" class="card_count">1</td>
                    <td>
                      <a class="simple" target="_blank" href="http://deckbox.org/mtg/Abhorrent Overlord" data-tt="http://deckbox.org//system/images/mtg/cards/373661.jpg">
                        Abhorrent Overlord
                      </a>
                    </td>
                    <td class="details_col">
                        <span class="mtg_edition_price">
                            <span data-title="$0.10 / $0.28 / $1.45 / $0.94">$0.28</span>
                        </span>
                        <div class="mtg_edition_container">
                            <img src="/images/mtg/editions/THS_R.jpg" data-title="Theros" class="">
                        </div>
                        <img src="/images/icon_spacer.gif" class="sprite s_star2 " data-title="Near Mint">
                        <img src="/images/icon_spacer_16_11.gif" class="flag flag-us" data-title="English">
                        <img src="/images/icon_spacer.gif" class="sprite s_colors " data-title="Foil">
                    </td>
                    <td class="type_line minimum_width">Creature  - Demon</td>
                    <td class="mana_cost minimum_width">
                        <img class="mtg_mana mtg_mana_5" src="/images/icon_spacer.gif">
                        <img class="mtg_mana mtg_mana_B" src="/images/icon_spacer.gif">
                        <img class="mtg_mana mtg_mana_B" src="/images/icon_spacer.gif">
                    </td>
                </tr>
                '''

                card = {}
                card["count"]   = tr.find("td.card_count").text()
                card["name"]    = tr.find("a").text()

                edition_container = tr.find(".mtg_edition_container img")
                card["edition"] = {
                    "code": re.search(".*/(.*)_.\.jpg$", edition_container.attr("src")).group(1),
                    "name": edition_container.attr("data-title")
                }
                card["rarity"]  = re.search(".*_(.)\.jpg$", edition_container.attr("src")).group(1)
                condition = {}
                card["condition"] = {
                    "code": re.sub("(sprite |\s)", "", tr.find(".sprite:first").attr("class")),
                    "name": tr.find(".sprite:first").attr("data-title")
                } if tr.find(".sprite:first") else {"code": None, "name": None}
                card["is_foil"]     = True if tr.find(".sprite.s_colors") else False
                card["is_promo"]    = True if tr.find(".sprite.s_rosette") else False
                card["is_textless"] = True if tr.find(".sprite.s_square") else False
                card["is_signed"]   = True if tr.find(".sprite.s_letter") else False
                card["lang"] = {
                    "code": re.sub("(flag |\s)", "", tr.find(".flag").attr("class")),
                    "name": tr.find(".flag").attr("data-title")
                } if tr.find(".flag") else {"code": None, "name": None}

                card_types = re.split(r'\s+-\s+', tr.find("td").eq(3).text())
                card["types"]   = re.split(r'\s', card_types[0]) if len(card_types) > 1 else card_types
                card["subtypes"]= re.split(r'\s', card_types[1]) if len(card_types) > 1 else []

                card_cost = []
                for img in tr.find("td.mana_cost img").items():
                    card_cost.append(re.sub("(mtg_mana |mtg_mana_)", "", img.attr("class")))
                card["cost"]    = "".join(card_cost)

                cards.append(card)

        return cards

