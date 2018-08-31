import re, datetime, urllib.parse, base64, json
from pyquery import PyQuery

class DeckboxCrawler:
    _HTTP           = "https://"
    _DECKBOX_DOMAIN = "deckbox.org"

    _ORDER_BY_PARAMETER = 's'
    _ORDER_BY_LIST = {
        'name':     'n',
        'edition':  'b',
        'price': {
            'inventory': 'j',
            'deck':      'i'
        },
        'type':     't',
        'cost':     'c',
        'color':    'a'
    }
    _ORDER_PARAMETER = 'o'
    _ORDER_LIST = {
        'asc':  'a',
        'desc': 'd'
    }

    _CARDS_QUERY_KEY = "f"
    _CARDS_QUERY_SEPARATOR = "!"
    _TOOLTIP = "/mtg/<cardname>/tooltip"

    def __init__(self, username):
        page_url = self._HTTP + urllib.parse.quote("{}/users/{}".format(self._DECKBOX_DOMAIN, username))
        self.getPage(page_url)

    def getUserProfile(self):
        details = [h.text() for h in self._page(".dl_with_img .details dd").items()]
        #Parse last seen online date
        details[2] = int(re.search(', ([0-9]+), ', details[2]).group(1))

        return {
            "last_seen_online": {
                "timestamp": details[2],
                "date": datetime.datetime.fromtimestamp(details[2]).strftime('%Y-%m-%d %H:%M:%S')
            },
            "username": self._page(".dl_with_img .section_title").text(),
            "location": details[0],
            "image": self._HTTP + self._DECKBOX_DOMAIN + self._page(".profile_page .friend_img").attr("src"),
            "will_trade": details[3],

            "bio": self._page(".indented_content").text(),
        }

    def getUserFriends(self):
        self.getPage(self._page_url + "/friends")

        friends = []

        #Get all friends
        for i, profile in enumerate(self._page("#all_friends .friends_list td").items()):
            current_friend = {}
            current_friend["username"] = profile.find(".data a").attr("href").replace("/users/", "")
            current_friend["image"] = self._HTTP + self._DECKBOX_DOMAIN + profile.find(".friend_img").attr("src")

            details = [h.text() for h in profile.find(".details dd").items()]

            #Parse last seen online date
            details[0] = int(re.search(', ([0-9]+), ', details[0]).group(1))
            current_friend["last_seen_online"] = {
                "timestamp": details[0],
                "date": datetime.datetime.fromtimestamp(details[0]).strftime('%Y-%m-%d %H:%M:%S')
            }
            current_friend["location"] = details[1]
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

    def getUserSetCards(self, set_id, page=1, order_by='name', order='asc'):
        set_object = self.getUserSets(set_id)

        if set_object == None:
            return {"status": "error", "description": "The user doesn't have the specified set."}

        parameters = {}
        parameters['p'] = str(page)
        parameters[self._ORDER_BY_PARAMETER] = self._ORDER_BY_LIST[order_by] if order_by in self._ORDER_BY_LIST else 'name'
        parameters[self._ORDER_PARAMETER] = self._ORDER_LIST[order] if order in self._ORDER_LIST else 'asc'

        set_url  = self._HTTP + self._DECKBOX_DOMAIN + "/sets/" + set_object["id"] + "?" + urllib.parse.urlencode(parameters)
        self.getPage(set_url)
        return {"id": set_id, **self.getCardsFromPage()}

    def getCards(self, page = 1, order_by = 'name', order = 'asc', filters = None):
        card_filters = self.getFiltersFromPage()
        parameters = {}
        parameters['p'] = str(page)
        parameters[self._ORDER_BY_PARAMETER] = self._ORDER_BY_LIST[order_by] if order_by in self._ORDER_BY_LIST else 'name'
        parameters[self._ORDER_PARAMETER] = self._ORDER_LIST[order] if order in self._ORDER_LIST else 'asc'
        parameters[self._CARDS_QUERY_KEY] = ""

        if filters:
            filters = json.loads(filters)
            converted_filters = []

            for filter_name, filter_data in filters.items()():
                if not filter_data:
                    pass

                # Need to encode string filters in base64
                if filter_data["operator"] not in ["all_of", "one_of", "none_of"]:
                    filter_value = base64.b64encode(filter_data["value"], "**")
                else:
                    filter_value = []
                    for value in filter_data["value"]:
                        filter_value.append(card_filters[filter_name][value.replace(" ", "_").lower()])
                    filter_value = ".".join(filter_value)

                converted_filter = card_filters["filter"][filter_name] + card_filters["operator"][filter_data["operator"]] + filter_value
                converted_filters.append(converted_filter)

            parameters[self._CARDS_QUERY_KEY] = self._CARDS_QUERY_SEPARATOR.join(converted_filters)

        cards_url  = self._HTTP + self._DECKBOX_DOMAIN + "/games/mtg/cards" + "?" + urllib.parse.urlencode(parameters)
        self.getPage(cards_url)

        return self.getCardsFromPage()

    def getCard(self):
        card = {}
        card["name"]    = self._page(".section_title:first").text()
        card_types = re.split(r'\s+-\s+', self._page(".card_properties tr:eq(3) td:last").text())
        card["types"]   = re.split(r'\s', card_types[0]) if len(card_types) > 1 else card_types
        card["subtypes"]= re.split(r'\s', card_types[1]) if len(card_types) > 1 else []
        card_cost = []
        for img in self._page(".card_properties tr:eq(2) td:last img").items():
            card_cost.append(re.sub("(mtg_mana |mtg_mana_)", "", img.attr("class")))
        card["cost"]    = "".join(card_cost)
        card["rules"]   = self._page(".card_properties tr:eq(4) td:last").text()
        card["image"]   = self._HTTP + self._DECKBOX_DOMAIN + self._page("#card_image").attr("src")
        card["tooltip"] = self._HTTP + self._DECKBOX_DOMAIN + self._TOOLTIP.replace("<cardname>", urllib.parse.quote(card["name"]))
        card["editions"] = []
        for edition in self._page(".card_properties tr:eq(1) td:last img").items():
            card["editions"].append({
                "code": re.search(".*/(.*)_.\.jpg$", edition.attr("src")).group(1),
                "name": edition.attr("data-title")
            })
        #Card type depending fields
        for tr in self._page(".card_properties tr:gt(4)").items():
            field = tr.find(".label").text().lower()
            field = {
                "p / t": "PT",
                "rulings": "gatherer_link"
            }.get(field, field)
            field_value = tr.find(".label").siblings()
            value = {
                "PT": {
                    "P": re.sub(r" / [0-9]+$", "", field_value.text()),
                    "T": re.sub(r"^[0-9]+ / ", "", field_value.text())
                },
                "gatherer_link": field_value.find("a").attr("href"),
                "formats": {
                    "legal": [x for x in field_value.text().lower().replace("legal in ", "").replace(".", "").split(", ") if x] if field_value.text().lower().find("legal in ") >= 0 else [],
                    "restricted": [x for x in field_value.text().lower().replace("restricted in ", "").replace(".", "").split(", ") if x] if field_value.text().lower().find("restricted in ") >= 0 else []
                }
            }.get(field, field_value.text())
            card[field] = value

        return card

    #-------------------------
    #  HELPERS
    #-------------------------
    def log(self, message):
        pass
        # print("LOG - " + message)

    def getPage(self, page_url):
        self.log("Get cards from url: " + page_url)
        self._page_url = page_url
        self._page = PyQuery(url=page_url)

    def getFiltersFromPage(self):
        filters = {}

        xpaths = [
            ("filter",  "#add_filter_btn"),
            ("type",    "#_container_3"),
            ("edition_printed_in", "#_container_5"),
            ("rarity",  "#_container_6"),
            ("color",   "#_container_7")
        ]

        for xpath in xpaths:
            script = self._page(xpath[1]).next("script")
            matches = re.findall('\["([^"]+)","([^"]+)"\]', script.text())
            filters[xpath[0]] = dict((x.replace(" ", "_").lower(), y) for x, y in matches)

        filters["operator"] = {
            'all_of':       '1',
            'none_of':      '2',
            'one_of':       '3',
            'equals':       '4',
            'larger_than':  '5',
            'smaller_than': '6',
            'contains':     '7',
            'not_contains': '8'
        }
        return filters

    def getCardsFromPage(self):
        if self._page(".main.simple_table.with_details"):
            page_type = "deck"
        elif self._page(".set_cards.with_details"):
            page_type = "inventory"
        elif self._page(".set_cards.simple_table"):
            page_type = "cards"
        else:
            page_type = "unknown"

        cards, sideboard = self.getCardsFromTable(page_type)

        #-------------------------
        # DECK PAGES
        #-------------------------
        if page_type == "deck":
            name            = self._page(".page_header .section_title").children().remove().end().text().replace('\'s ', '')
            cards_count     = {"total": 0, "distinct": 0}
            deck_cards = self._page(".section_title.section_title").eq(1)
            m = re.search("([0-9]+) cards, ([0-9]+) distinct", deck_cards.text())
            if m != None and m.group(1) and m.group(2):
                cards_count["total"]    = int(m.group(1))
                cards_count["distinct"] = int(m.group(2))

            sideboard_count = {"total": 0, "distinct": 0}
            sideboard_cards = self._page(".section_title.section_title").eq(2)
            m = re.search("([0-9]+) cards, ([0-9]+) distinct", sideboard_cards.text())
            if m != None and m.group(1) and m.group(2):
                sideboard_count["total"]    = int(m.group(1))
                sideboard_count["distinct"] = int(m.group(2))

            return {
                "name": name,
                "mainboard": {
                    "cards": cards,
                    "total": cards_count["total"],
                    "distinct": cards_count["distinct"]
                },
                "sideboard": {
                    "cards": sideboard,
                    "total": sideboard_count["total"],
                    "distinct": sideboard_count["distinct"]
                },
            }

        #-------------------------
        # DEFAULT SETS PAGES
        #-------------------------
        else:
            pagination      = self._page("#set_cards_table .pagination_controls").text()
            m = re.search('([0-9]+) total results .* Page ([0-9]+) of ([0-9]+)', pagination)
            total           = int(m.group(1)) if m else 1
            current_page    = int(m.group(2)) if m else 1
            total_pages     = int(m.group(3)) if m else 1
            name            = self._page(".section_title span:first").text()

            return {
                "name": name,
                "cards": cards,
                "total": total,
                "count": len(cards),
                "page": current_page,
                "total_pages": total_pages
            }

    #-------------------------
    # Cards Parser
    #-------------------------
    def getCardsFromTable(self, page_type):
        cards       = []
        sideboard   = []

        # Parse cards on deck page
        if page_type == "deck":
            tables = {
                "mainboard": self._page(".main.simple_table.with_details tr").items(),
                "sideboard": self._page(".sideboard.simple_table.with_details tr").items()
            }
            for table_type, table in tables.items():
                for tr in table:
                    if tr.attr("id") == None:
                        continue

                    '''
                    Deck card HTML example:
                    <tr id="13008_main">
                        <td class="card_count">1</td>
                        <td class="card_name">
                            <a class="simple" href="https://deckbox.org/mtg/Phantom%20General" target="_blank">Phantom General</a>
                        </td>
                        <td>Creature  - Spirit Soldier</td>
                        <td class="center"><img class="mtg_mana mtg_mana_3" src="/images/icon_spacer.gif"><img class="mtg_mana mtg_mana_W" src="/images/icon_spacer.gif"></td>
                        <td class="center"><div class="mtg_edition_container " onclick="">
                               <img src="/images/mtg/editions/RTR_U.jpg" data-title="Last Important Printing - Return to Ravnica" class="">
                             </div></td>
                        <td class="center minimum_width">$0.22</td>
                    </tr>
                    '''

                    card = {}
                    card["count"]   = tr.find("td.card_count").text()
                    card["name"]    = tr.find("a").text()
                    # card["tooltip"] = self._HTTP + self._DECKBOX_DOMAIN + self._TOOLTIP.replace("<cardname>", urllib.parse.quote(card["name"]))
                    # card_types = re.split(r'\s+-\s+', tr.find("td").eq(2).text())
                    # card["types"]   = re.split(r'\s', card_types[0]) if len(card_types) > 1 else card_types
                    # card["subtypes"]= re.split(r'\s', card_types[1]) if len(card_types) > 1 else []
                    # card_cost = []
                    # for img in tr.find("td").eq(3).find('img').items():
                    #     card_cost.append(re.sub("(mtg_mana |mtg_mana_)", "", img.attr("class")))
                    # card["cost"]    = "".join(card_cost)

                    {
                        "mainboard": cards,
                        "sideboard": sideboard,
                    }.get(table_type).append(card)

        # Parse cards on default set (inventory, wishlist, tradelist) page
        elif page_type == "cards":
            for tr in self._page(".set_cards.simple_table tr").items():
                if tr.attr("id") == None:
                    continue

                '''
                Default card HTML example:
                <tr id="7730" >
                    <td class="card_name">
                      <div class="relative">
                        <a class="simple" target="_blank" href="http://deckbox.org/mtg/Annul">Annul</a>
                      </div>
                    </td>
                    <td><span>Instant</span></td>
                    <td class="card_cost"><img class="mtg_mana mtg_mana_U" src="/images/icon_spacer.gif" /></td>
                    <td class="center price"><span data-title="$0.03 / $0.14 / $0.43 / $0.68">$0.14</span></td>
                </tr>
                '''

                card = {}
                card["name"]    = tr.find("a").text()
                card["tooltip"] = self._HTTP + self._DECKBOX_DOMAIN + self._TOOLTIP.replace("<cardname>", urllib.parse.quote(card["name"]))
                card_types  = re.split(r'\s+-\s+', tr.find("td").eq(1).find("span").text())
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
                <tr class="" id="734306" onclick="">
                    <td class="inventory_count card_count">1</td>
                    <td>
                        <a class="simple" href="https://deckbox.org/mtg/Abhorrent%20Overlord?printing=21860&amp;lang=us" target="_blank">
                            Abhorrent Overlord
                        </a>
                    </td>
                    <td class="center minimum_width">$0.29</td>
                    <td class="minimum_width">
                        <div class="mtg_edition_container " onclick="">
                            <img src="/images/mtg/editions/THS_R.jpg" data-title="Theros (Card #75)" class="">
                        </div>
                    <img src="/images/icon_spacer.gif" class="sprite s_star2" data-title="Near Mint">
                    <img src="/images/icon_spacer_16_11.png" class="flag flag-us" data-title="English"></td>
                    <td class="minimum_width">Creature  - Demon</td>
                </tr>

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
                # card["tooltip"] = self._HTTP + self._DECKBOX_DOMAIN + self._TOOLTIP.replace("<cardname>", urllib.parse.quote(card["name"]))

                edition_container = tr.find(".mtg_edition_container img")
                card["edition"] = {}
                try:
                    card["edition"]["code"] = re.search(".*/(.*)_.\.jpg$", edition_container.attr("src")).group(1),
                except:
                    card["edition"]["code"] = None

                card["edition"]["name"] = edition_container.attr("data-title")

                # card["rarity"]  = re.search(".*_(.)\.jpg$", edition_container.attr("src")).group(1)

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

                # card_types = re.split(r'\s+-\s+', tr.find("td").eq(3).text())
                # card["types"]   = re.split(r'\s', card_types[0]) if len(card_types) > 1 else card_types
                # card["subtypes"]= re.split(r'\s', card_types[1]) if len(card_types) > 1 else []

                # card_cost = []
                # for img in tr.find("td.mana_cost img").items():
                #     card_cost.append(re.sub("(mtg_mana |mtg_mana_)", "", img.attr("class")))
                # card["cost"]    = "".join(card_cost)

                cards.append(card)

        return (cards, sideboard)
