Deckbox API (non-official)
==========

Introduction
==========
This application emulates a deckbox API.  
It's based on a HTML parser that will get user public information from Deckbox and returns it as json objects.  
**This is not the official Deckbox API.**

Location
==========
You can access the API here: https://deckbox-api.herokuapp.com

How to use
==========
Requirements:

* Python 2.7.4
* [virtualenv](http://www.virtualenv.org/)

---

    $ git clone https://github.com/T0RAT0RA/deckbox-api.git
    $ cd deckbox-api
    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ python api.py

To run tests:

    $ python api_tests.py 1>/dev/null


Licence
==========

[MIT License](LICENSE.md)
