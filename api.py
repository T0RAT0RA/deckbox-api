import os, time, urllib, functools
from flask import Flask, render_template, jsonify, redirect, url_for, request, json
from flask_restful.reqparse import Argument
from flask_restful import Resource, Api
from flask_sslify import SSLify
from deckbox_crawler import DeckboxCrawler
from decorators import marshal_with, parse_request, paginate_deckbox_results
from schemas import CardSchema, UserSchema, SetSchema, DeckboxCardSchema
import redis
import dpath.util
import scrython

app = Flask(__name__)
sslify = SSLify(app, permanent=True)
restapi = Api(app, '/api', catch_all_404s=True)

r = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))


def extend_cards(*args, **kwargs):
    """
    Decorator to add card metadata
    """
    def decorator(f):
        @functools.wraps(f)
        def inner(*fargs, **fkwargs):
            rv = f(*fargs, **fkwargs)
            for path in args:
                cards_list = dpath.util.get(rv, path, separator='.')
                cards = {x['name']: x for x in cards_list}

                if not cards:
                    continue

                cards_meta = {x['name']: x for x in [json.loads(x) for x in r.mget(cards) if x]}
                cards_not_cached = set(list(cards.keys())) - set(list(cards_meta.keys()))

                if cards_not_cached:
                    query = "name:/{}/".format("/ or name:/".join([c for c in cards if c in cards_not_cached]))
                    time.sleep(0.1) #required by scryfall policies
                    response = scrython.cards.Search(q=query).data()
                    print('LOG - get card meta q=' + query)
                    cards_meta.update({x['name']: x for x in response})

                    r.mset({
                        x['name']: json.dumps(x) for x in cards_meta.values()
                    })

                cards_inflated = []
                for c in cards_list:
                    name = c['name']
                    cards_inflated.append(
                        {**cards[name], **cards_meta[name]}
                    )
                cards = cards_inflated

                dpath.util.set(rv, path, cards, separator='.')

            return rv
        return inner
    return decorator


@app.route('/')
def index():
    test_data = {
        "username": "deckbox_api",
        "set_id": "608751",
        "cardname": "Nicol Bolas, Planeswalker"
    }

    return render_template('index.html', api_doc_list = getApiDocList(), test_data = test_data)


class ApiDoc(Resource):
    def get(self):
        return getApiDocList()


class User(Resource):
    @marshal_with(UserSchema())
    def get(self, username):
        deckbox_crawler = DeckboxCrawler(username)
        user_profile = deckbox_crawler.getUserProfile()
        user_sets = deckbox_crawler.getUserSets()

        return {
            **user_profile,
            "sets": user_sets
        }


class UserFriend(Resource):
    @marshal_with(UserSchema(many=True), pagination=True)
    def get(self, username):
        deckbox_crawler = DeckboxCrawler(username)
        user_friends = deckbox_crawler.getUserFriends()

        return user_friends


class UserSetList(Resource):
    @marshal_with(SetSchema(many=True), pagination=True)
    def get(self, username):
        deckbox_crawler = DeckboxCrawler(username)
        user_sets = deckbox_crawler.getUserSets()

        return user_sets


class UserSet(Resource):
    @marshal_with(SetSchema())
    @extend_cards(
        'mainboard.cards',
        'sideboard.cards',
    )
    def get(self, username, set_id, page=1, sort_by='name', order='asc'):
        deckbox_crawler = DeckboxCrawler(username)
        user_set = deckbox_crawler.getUserSetCards(set_id, page, sort_by, order)

        return user_set


class UserInventory(Resource):
    @parse_request(
        Argument('page', type=int, default=1, required=False, store_missing=False),
        allow_ordering=True
    )
    @marshal_with(DeckboxCardSchema(many=True), pagination=True, paginator=paginate_deckbox_results)
    @extend_cards(
        'cards',
    )
    def get(self, username, page=1, sort_by='name', order='asc'):
        deckbox_crawler = DeckboxCrawler(username)
        user_inventory = deckbox_crawler.getUserSetCards("inventory", page, sort_by, order)

        return user_inventory


class UserWishlist(Resource):
    @parse_request(
        Argument('page', type=int, default=1, required=False, store_missing=False),
        allow_ordering=True
    )
    @marshal_with(DeckboxCardSchema(many=True), pagination=True, paginator=paginate_deckbox_results)
    @extend_cards(
        'cards',
    )
    def get(self, username, page=1, sort_by='name', order='asc'):
        deckbox_crawler = DeckboxCrawler(username)
        user_wishlist = deckbox_crawler.getUserSetCards("wishlist", page, sort_by, order)

        return user_wishlist


class UserTradelist(Resource):
    @parse_request(
        Argument('page', type=int, default=1, required=False, store_missing=False),
        allow_ordering=True
    )
    @marshal_with(DeckboxCardSchema(many=True), pagination=True, paginator=paginate_deckbox_results)
    @extend_cards(
        'cards',
    )
    def get(self, username, page=1, sort_by='name', order='asc'):
        deckbox_crawler = DeckboxCrawler(username)
        user_tradelist = deckbox_crawler.getUserSetCards("tradelist", page, sort_by, order)

        return user_tradelist


class Card(Resource):
    @marshal_with(CardSchema(many=True), pagination=True)
    def get(self, cardname):
        return scrython.cards.Search(q="name:/{}/".format(cardname)).data()


restapi.add_resource(ApiDoc, '/')
restapi.add_resource(User, '/users/<string:username>')
restapi.add_resource(UserFriend, '/users/<string:username>/friends/')
restapi.add_resource(UserSetList, '/users/<string:username>/sets/')
restapi.add_resource(UserInventory, '/users/<string:username>/inventory')
restapi.add_resource(UserWishlist, '/users/<string:username>/wishlist')
restapi.add_resource(UserTradelist, '/users/<string:username>/tradelist')
restapi.add_resource(UserSet, '/users/<string:username>/sets/<set_id>')
restapi.add_resource(Card, '/cards/<path:cardname>')


def getApiDocList():
    json_data = open('api_doc_list.json')
    api_doc_list = json.load(json_data)
    json_data.close()
    return api_doc_list


if __name__ == '__main__':
    app.run(debug=True)
