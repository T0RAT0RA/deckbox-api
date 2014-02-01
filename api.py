import os
from flask import Flask, render_template, jsonify, redirect, url_for, request, json
from flask.ext import restful
from deckbox_crawler import DeckboxCrawler

app = Flask(__name__)
restapi = restful.Api(app, '/api')

@app.route('/')
def index():
    test_data  = {
        "username": "deckbox_api",
        "set_id": "590740",
        "cardname": "Nicol Bolas, Planeswalker"
    }

    return render_template('index.html', api_doc_list = getApiDocList(), test_data = test_data)

class ApiDoc(restful.Resource):
    def get(self):
        return getApiDocList()

class User(restful.Resource):
    def get(self, username):
        deckbox_crawler = DeckboxCrawler("profile", username)
        user_profile    = deckbox_crawler.getUserProfile()
        user_sets       = deckbox_crawler.getUserSets()

        return jsonify(
            user_profile,
            sets = user_sets,
        )

class UserFriend(restful.Resource):
    def get(self, username):
        deckbox_crawler = DeckboxCrawler("profile", username)
        user_friends = deckbox_crawler.getUserFriends()

        return jsonify(friends=user_friends)

class UserSetList(restful.Resource):
    def get(self, username):
        deckbox_crawler = DeckboxCrawler("profile", username)
        user_sets       = deckbox_crawler.getUserSets()

        return jsonify(sets = user_sets)

class UserSet(restful.Resource):
    def get(self, username, set_id):
        deckbox_crawler = DeckboxCrawler("profile", username)
        page = request.args.get('p', 1)
        user_set = deckbox_crawler.getUserSetCards(set_id, page)

        return jsonify(user_set)

class UserInventory(restful.Resource):
    def get(self, username):
        deckbox_crawler = DeckboxCrawler("profile", username)
        user_inventory = deckbox_crawler.getUserSetCards("inventory")

        return jsonify(user_inventory)

class UserWishlist(restful.Resource):
    def get(self, username):
        deckbox_crawler = DeckboxCrawler("profile", username)
        user_wishlist = deckbox_crawler.getUserSetCards("wishlist")

        return jsonify(user_wishlist)

class UserTradelist(restful.Resource):
    def get(self, username):
        deckbox_crawler = DeckboxCrawler("profile", username)
        user_tradelist = deckbox_crawler.getUserSetCards("tradelist")

        return jsonify(user_tradelist)

class Card(restful.Resource):
    def get(self, cardname):
        deckbox_crawler = DeckboxCrawler("card", cardname)
        card = deckbox_crawler.getCard()

        return jsonify(card = card)

restapi.add_resource(ApiDoc, '/')
restapi.add_resource(User, '/users/<username>/')
restapi.add_resource(UserFriend, '/users/<username>/friends/')
restapi.add_resource(UserSetList, '/users/<string:username>/sets/')
restapi.add_resource(UserInventory, '/users/<string:username>/inventory/')
restapi.add_resource(UserWishlist, '/users/<string:username>/wishlist/')
restapi.add_resource(UserTradelist, '/users/<string:username>/tradelist/')
restapi.add_resource(UserSet, '/users/<string:username>/sets/<set_id>/')
restapi.add_resource(Card, '/cards/<string:cardname>/')


def getApiDocList():
    json_data = open('api_doc_list.json')
    api_doc_list = json.load(json_data)
    json_data.close()
    return api_doc_list;


if __name__ == '__main__':
    app.run(debug=True)
