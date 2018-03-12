import os, time, urllib
from flask import Flask, render_template, jsonify, redirect, url_for, request, json
from flask_restful.reqparse import Argument
from flask.ext import restful
from flask_sslify import SSLify
from deckbox_crawler import DeckboxCrawler
from decorators import marshal_with, parse_request, paginate_deckbox_results
from schemas import CardSchema, UserSchema, SetSchema, DeckboxCardSchema
from marshmallow import pprint
import scrython

app = Flask(__name__)
sslify = SSLify(app, permanent=True)
restapi = restful.Api(app, '/api', catch_all_404s=True)

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
    @marshal_with(UserSchema())
    def get(self, username):
        deckbox_crawler = DeckboxCrawler(username)
        user_profile    = deckbox_crawler.getUserProfile()
        user_sets       = deckbox_crawler.getUserSets()

        return {
            **user_profile,
            "sets": user_sets
        }


class UserFriend(restful.Resource):
    @marshal_with(UserSchema(many=True), pagination=True)
    def get(self, username):
        deckbox_crawler = DeckboxCrawler(username)
        user_friends = deckbox_crawler.getUserFriends()

        return user_friends

class UserSetList(restful.Resource):
    @marshal_with(SetSchema(many=True), pagination=True)
    def get(self, username):
        deckbox_crawler = DeckboxCrawler(username)
        user_sets       = deckbox_crawler.getUserSets()

        return user_sets

class UserSet(restful.Resource):
    @marshal_with(SetSchema())
    def get(self, username, set_id, page=1, sort_by='name', order='asc'):
        deckbox_crawler = DeckboxCrawler(username)
        user_set    = deckbox_crawler.getUserSetCards(set_id)

        return user_set

class UserInventory(restful.Resource):
    @parse_request(
        Argument('page', type=int, default=1, required=False, store_missing=False),
        allow_ordering=True
    )
    @marshal_with(DeckboxCardSchema(many=True), pagination=True, paginator=paginate_deckbox_results)
    def get(self, username, page=1, sort_by='name', order='desc'):
        deckbox_crawler = DeckboxCrawler(username)
        user_inventory = deckbox_crawler.getUserSetCards("inventory", page, sort_by, order)

        return user_inventory

class UserWishlist(restful.Resource):
    @parse_request(
        Argument('page', type=int, default=1, required=False, store_missing=False),
        allow_ordering=True
    )
    @marshal_with(DeckboxCardSchema(many=True), pagination=True, paginator=paginate_deckbox_results)
    def get(self, username, page=1, sort_by='name', order='desc'):
        deckbox_crawler = DeckboxCrawler(username)
        user_wishlist = deckbox_crawler.getUserSetCards("wishlist", page, sort_by, order)

        return user_wishlist

class UserTradelist(restful.Resource):
    @parse_request(
        Argument('page', type=int, default=1, required=False, store_missing=False),
        allow_ordering=True
    )
    @marshal_with(DeckboxCardSchema(many=True), pagination=True, paginator=paginate_deckbox_results)
    def get(self, username, page=1, sort_by='name', order='desc'):
        deckbox_crawler = DeckboxCrawler(username)
        user_tradelist = deckbox_crawler.getUserSetCards("tradelist", page, sort_by, order)

        return user_tradelist

class Card(restful.Resource):
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
    return api_doc_list;


if __name__ == '__main__':
    app.run(debug=True)
