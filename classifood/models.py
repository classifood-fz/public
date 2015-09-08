from google.appengine.ext import ndb
from classifood import label_api, constants

class Search_Cache(ndb.Model):
    updated_on = ndb.DateTimeProperty(auto_now=True, indexed=True)
    profile_hash = ndb.StringProperty(required=True)
    search_term = ndb.StringProperty(required=True)
    start = ndb.IntegerProperty(required=True)
    products = ndb.JsonProperty(indexed=False)
    pages = ndb.JsonProperty(indexed=False)
    nfound = ndb.IntegerProperty(indexed=False)

class User(ndb.Model):
    updated_on = ndb.DateTimeProperty(auto_now=True, indexed=True)
    email = ndb.StringProperty(required=True)
    group_id = ndb.IntegerProperty(default=1)
    refresh_token = ndb.StringProperty(required=True)
    upgrade_exp = ndb.DateTimeProperty(indexed=True)

    def get_profile(self):
        return {
            'nutrients': [
                {'name': 'Calories', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Calories').get(keys_only=True)
                )},
                {'name': 'Calories from Fat', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Calories from Fat').get(keys_only=True)
                )},
                {'name': 'Saturated Fat Calories', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Saturated Fat Calories').get(keys_only=True)
                )},
                {'name': 'Total Fat', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Total Fat').get(keys_only=True)
                )},
                {'name': 'Saturated Fat', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Saturated Fat').get(keys_only=True)
                )},
                {'name': 'Monounsaturated Fat', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Monounsaturated Fat').get(keys_only=True)
                )},
                {'name': 'Polyunsaturated Fat', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Polyunsaturated Fat').get(keys_only=True)
                )},
                {'name': 'Cholesterol', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Cholesterol').get(keys_only=True)
                )},
                {'name': 'Sodium', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Sodium').get(keys_only=True)
                )},
                {'name': 'Potassium', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Potassium').get(keys_only=True)
                )},
                {'name': 'Total Carbohydrate', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Total Carbohydrate').get(keys_only=True)
                )},
                {'name': 'Other Carbohydrate', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Other Carbohydrate').get(keys_only=True)
                )},
                {'name': 'Dietary Fiber', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Dietary Fiber').get(keys_only=True)
                )},
                {'name': 'Soluble Fiber', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Soluble Fiber').get(keys_only=True)
                )},
                {'name': 'Insoluble Fiber', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Insoluble Fiber').get(keys_only=True)
                )},
                {'name': 'Sugars', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Sugars').get(keys_only=True)
                )},
                {'name': 'Protein', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Protein').get(keys_only=True)
                )}
            ],
            'allergens': [
                {'name': 'Cereals', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Cereals').get(keys_only=True)
                )},
                {'name': 'Coconut', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Coconut').get(keys_only=True)
                )},
                {'name': 'Corn', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Corn').get(keys_only=True)
                )},
                {'name': 'Egg', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Egg').get(keys_only=True)
                )},
                {'name': 'Fish', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Fish').get(keys_only=True)
                )},
                {'name': 'Gluten', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Gluten').get(keys_only=True)
                )},
                {'name': 'Lactose', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Lactose').get(keys_only=True)
                )},
                {'name': 'Milk', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Milk').get(keys_only=True)
                )},
                {'name': 'Peanuts', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Peanuts').get(keys_only=True)
                )},
                {'name': 'Sesame Seeds', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Sesame Seeds').get(keys_only=True)
                )},
                {'name': 'Shellfish', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Shellfish').get(keys_only=True)
                )},
                {'name': 'Soybean', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Soybean').get(keys_only=True)
                )},
                {'name': 'Sulfites', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Sulfites').get(keys_only=True)
                )},
                {'name': 'Tree Nuts', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Tree Nuts').get(keys_only=True)
                )},
                {'name': 'Wheat', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Wheat').get(keys_only=True)
                )}
            ],
            'additives': [
                {'name': 'Added Sugar', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Added Sugar').get(keys_only=True)
                )},
                {'name': 'Artificial Color', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Artificial Color').get(keys_only=True)
                )},
                {'name': 'Artificial Flavoring Agent', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Artificial Flavoring Agent').get(keys_only=True)
                )},
                {'name': 'Flavor Enhancer', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Flavor Enhancer').get(keys_only=True)
                )},
                {'name': 'Trans Fat', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Trans Fat').get(keys_only=True)
                )},
                {'name': 'Acidity Regulator', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Acidity Regulator').get(keys_only=True)
                )},
                {'name': 'Anti Caking Agents', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Anti Caking Agents').get(keys_only=True)
                )},
                {'name': 'Anti Foaming Agent', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Anti Foaming Agent').get(keys_only=True)
                )},
                {'name': 'Antioxidants', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Antioxidants').get(keys_only=True)
                )},
                {'name': 'Artificial Preservative', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Artificial Preservative').get(keys_only=True)
                )},
                {'name': 'Bulking Agents', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Bulking Agents').get(keys_only=True)
                )},
                {'name': 'Colors', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Colors').get(keys_only=True)
                )},
                {'name': 'Emulsifiers', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Emulsifiers').get(keys_only=True)
                )},
                {'name': 'Enzyme', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Enzyme').get(keys_only=True)
                )},
                {'name': 'Firming Agent', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Firming Agent').get(keys_only=True)
                )},
                {'name': 'Flour Treatment Agent', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Flour Treatment Agent').get(keys_only=True)
                )},
                {'name': 'Food Acids', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Food Acids').get(keys_only=True)
                )},
                {'name': 'Gelling Agents', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Gelling Agents').get(keys_only=True)
                )},
                {'name': 'Glazing Agent', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Glazing Agent').get(keys_only=True)
                )},
                {'name': 'Humectants', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Humectants').get(keys_only=True)
                )},
                {'name': 'Leavening Agent', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Leavening Agent').get(keys_only=True)
                )},
                {'name': 'Mineral Salt', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Mineral Salt').get(keys_only=True)
                )},
                {'name': 'Natural Color', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Natural Color').get(keys_only=True)
                )},
                {'name': 'Natural Flavoring Agent', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Natural Flavoring Agent').get(keys_only=True)
                )},
                {'name': 'Natural Preservative', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Natural Preservative').get(keys_only=True)
                )},
                {'name': 'Preservatives', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Preservatives').get(keys_only=True)
                )},
                {'name': 'Propellant', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Propellant').get(keys_only=True)
                )},
                {'name': 'Raising Agents', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Raising Agents').get(keys_only=True)
                )},
                {'name': 'Saturated Fat', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Saturated Fat').get(keys_only=True)
                )},
                {'name': 'Sequestrant', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Sequestrant').get(keys_only=True)
                )},
                {'name': 'Stabilizers', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Stabilizers').get(keys_only=True)
                )},
                {'name': 'Sweeteners', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Sweeteners').get(keys_only=True)
                )},
                {'name': 'Thickeners', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Thickeners').get(keys_only=True)
                )},
                {'name': 'Unsaturated Fat', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Unsaturated Fat').get(keys_only=True)
                )},
                {'name': 'Vegetable Gum', 'value': User._bool_to_str(
                    Label.query(
                        Label.user_id == self.key.id(),
                        Label.name == 'Vegetable Gum').get(keys_only=True)
                )}
            ],
            "myingredients": [],
            "mysort": [{"sort_variable": "Calories", "sort_order": 1, "variable_type": 1}]
        }

    def set_profile(self, session_id, profile=None):
        if profile:
            label_api.set_profile(session_id, profile)
        else:
            label_api.set_profile(session_id, self.get_profile())

    def reset_profile(self, session_id):
        """
        Resets a user's diet profile to exclude all premium filters
        """
        for nutrient in [x[0] for x in constants.known_nutrients if x[1]]:
            Label.query(Label.name == nutrient, Label.user_id == self.key.id()).map(
                lambda key: key.delete(), keys_only=True)

        for allergen in [x[0] for x in constants.known_allergens if x[1]]:
            Label.query(Label.name == allergen, Label.user_id == self.key.id()).map(
                lambda key: key.delete(), keys_only=True)

        for additive in [x[0] for x in constants.known_additives if x[1]]:
            Label.query(Label.name == additive, Label.user_id == self.key.id()).map(
                lambda key: key.delete(), keys_only=True)

        self.set_profile(session_id)

    @staticmethod
    def _bool_to_str(b):
        return 'true' if b else 'false'

class Order(ndb.Model):
    added_on = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    user_id = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    description = ndb.StringProperty(required=True)
    price = ndb.IntegerProperty(required=True) # Cents
    currency = ndb.StringProperty(required=True, default='usd')

class Shopping_List_Product(ndb.Model):
    added_on = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    user_id = ndb.StringProperty(required=True)
    barcode = ndb.StringProperty(required=True)
    
class Pantry_Product(ndb.Model):
    added_on = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    user_id = ndb.StringProperty(required=True)
    barcode = ndb.StringProperty(required=True)

class Label(ndb.Model):
    user_id = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    sub_id = ndb.StringProperty()
