import os
from flask import Flask, render_template, jsonify, redirect, url_for, request, json
from flask.ext import restful
from deckbox_crawler import DeckboxCrawler

app = Flask(__name__)
restapi = restful.Api(app, '/api')

@app.route('/')
def index():
    return render_template('index.html', api_doc_list = getApiDocList())

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

class UserSetList(restful.Resource):
    def get(self, username):
        deckbox_crawler = DeckboxCrawler("profile", username)
        user_sets       = deckbox_crawler.getUserSets()

        return jsonify(sets = user_sets)

class UserSet(restful.Resource):
    def get(self, username, set_id):
        deckbox_crawler = DeckboxCrawler("profile", username)
        page = request.args.get('p', 1)
        user_inventory = deckbox_crawler.getUserSetCards(set_id, page)

        return jsonify(user_inventory)

class Card(restful.Resource):
    def get(self, cardname):
        deckbox_crawler = DeckboxCrawler("card", cardname)
        card = deckbox_crawler.getCard()

        return jsonify(card = card)

restapi.add_resource(ApiDoc, '/')
restapi.add_resource(User, '/users/<username>/')
restapi.add_resource(UserSetList, '/users/<string:username>/sets/')
restapi.add_resource(UserSet, '/users/<string:username>/sets/<set_id>/')
restapi.add_resource(Card, '/cards/<string:cardname>/')


def getApiDocList():
    json_data = open('api_doc_list.json')
    api_doc_list = json.load(json_data)
    json_data.close()
    return api_doc_list;


if __name__ == '__main__':
    app.run(debug=True)
