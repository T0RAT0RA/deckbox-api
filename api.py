import os
from flask import Flask, render_template, jsonify, redirect, url_for, request
from flask.ext import restful
from deckbox_crawler import DeckboxCrawler


app = Flask(__name__)
restapi = restful.Api(app, '/api')

@app.route('/')
def index():
    return render_template('index.html')


class Api(restful.Resource):
    def get(self):
        return jsonify({
            '/api/:username/': 'Get user profile information and sets id.',
            '/api/:username/set/:set_id': 'Get cards from a set. Use the p parameter for the pagination.',
        })

class User(restful.Resource):
    def get(self, username):
        deckbox_crawler = DeckboxCrawler(username)
        user_profile    = deckbox_crawler.getUserProfile()
        user_sets       = deckbox_crawler.getUserSets()

        return jsonify(
            user_profile,
            sets = user_sets,
        )


class UserSet(restful.Resource):
    def get(self, username, set_id):
        deckbox_crawler = DeckboxCrawler(username)
        page = request.args.get('p', 1)
        user_inventory = deckbox_crawler.getUserSetCards(set_id, page)

        return jsonify(user_inventory)

restapi.add_resource(Api, '/')
restapi.add_resource(User, '/<username>/')
restapi.add_resource(UserSet, '/<username>/set/<set_id>/')

if __name__ == '__main__':
    app.run(debug=True)
