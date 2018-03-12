from marshmallow import Schema, fields, pre_dump, post_dump, pprint

class CardSchema(Schema):
    multiverse_id = fields.List(fields.Str())
    id = fields.Str()
    set = fields.Str()
    set_name = fields.Str()
    images = fields.Dict(fields.Str(), attribute="image_uris")
    name = fields.Str()
    cmc = fields.Integer()
    mana_cost = fields.Str()
    type_line = fields.Str()
    types = fields.List(fields.Str(), default=[])
    subtypes = fields.List(fields.Str(), default=[])

    @pre_dump
    def extract_types(self, in_data):
        if not 'type_line' in in_data:
            return in_data

        types = in_data['type_line'].split(' — ')
        in_data['types'] = types[0].split(' ')
        try:
            in_data['subtypes'] = types[1].split(' ')
        except IndexError:
            pass
        return in_data

class DeckboxCardSchema(Schema):
    name = fields.Str()
    count = fields.Integer()
    condition = fields.Dict()
    edition = fields.Dict()
    lang = fields.Dict()
    is_foil = fields.Boolean()
    is_promo = fields.Boolean()
    is_signed = fields.Boolean()
    is_textless = fields.Boolean()

class LastSeenOnlineSchema(Schema):
    date = fields.Str()
    timestamp = fields.Integer()

class DeckSchema(Schema):
    cards = fields.Nested(DeckboxCardSchema(), many=True)
    total = fields.Integer()
    distinct = fields.Integer()

class SetSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    mainboard = fields.Nested(DeckSchema())
    sideboard = fields.Nested(DeckSchema())

class UserSchema(Schema):
    id = fields.Str()
    username = fields.Str()
    bio = fields.Str()
    image = fields.Str()
    last_seen_online = fields.Nested(LastSeenOnlineSchema())
    location = fields.Str()
    sets = fields.Nested(SetSchema(), many=True)
    will_trade = fields.Str()
