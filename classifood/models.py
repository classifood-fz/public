from google.appengine.ext import ndb

class User(ndb.Model):
    update_datetime = ndb.DateTimeProperty(auto_now=True, indexed=True)
    email = ndb.StringProperty(indexed=True)
    nutrients = ndb.JsonProperty(indexed=False)
    allergens = ndb.JsonProperty(indexed=False)
    additives = ndb.JsonProperty(indexed=False)
    ingredients = ndb.JsonProperty(indexed=False)
    is_admin = ndb.BooleanProperty(indexed=True)
    is_advertiser = ndb.BooleanProperty(indexed=True)
    is_paying = ndb.BooleanProperty(indexed=True)
    refresh_token = ndb.StringProperty(indexed=True)

class Shopping_List_Product(ndb.Model):
    add_datetime = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    user_id = ndb.StringProperty(indexed=True)
    barcode = ndb.StringProperty(indexed=True)
    
class Pantry_Product(ndb.Model):
    add_datetime = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    user_id = ndb.StringProperty(indexed=True)
    barcode = ndb.StringProperty(indexed=True)

class Ingredient(ndb.Model):
    last_update = ndb.DateTimeProperty(auto_now=True, indexed=True)
    name = ndb.StringProperty(required=True, indexed=True)
    grade = ndb.IntegerProperty(required=True, indexed=True, choices=range(1,11))
    description = ndb.TextProperty(required=True)
