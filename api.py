import os
from flask import Flask, render_template, jsonify, redirect, url_for, request
from deckbox_crawler import DeckboxCrawler

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/')
def api():
    return jsonify({
        "/api/:username/": "Get user profile information and sets id.",
        "/api/:username/set/:set_id": "Get cards from a set. Use the p parameter for the pagination.",
    })

@app.route('/api/<username>/')
def api_get_user_profile(username):
    deckbox_crawler     = DeckboxCrawler(username)
    user_profile        = deckbox_crawler.getUserProfile()
    user_default_sets   = deckbox_crawler.getUserSets()

    return jsonify(
        user_profile,
        sets = user_default_sets,
    )

@app.route('/api/<username>/set/<set_id>/')
def api_get_user_set(username, set_id):
    deckbox_crawler = DeckboxCrawler(username)
    page = request.args.get('p', 1)
    user_inventory = deckbox_crawler.getUserSetCards(set_id, page)

    return jsonify(user_inventory)


if __name__ == '__main__':
    app.run(debug=True)
