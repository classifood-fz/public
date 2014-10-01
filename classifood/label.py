"""
This module interacts with the Label API from FoodEssentials.
See http://developer.foodessentials.com/api for API documentation.
"""

from django.utils import http
from google.appengine.api import urlfetch
from classifood import settings
import json

"""
Builds url and calls API
"""
def call_api(http_method, api_method, params=None, body=None):
    url = "http://{0}/{1}".format(settings.LABEL_API_HOST, api_method)

    if params:
        # Convert params to url-encoded string pairs
        pairs = map(lambda pair: http.urlencode({pair[0]: pair[1]}), params.items())
        url += '?' + '&'.join(pairs)
    
    try:        
        response = urlfetch.fetch(url, payload=body, method=http_method, deadline=5)

    except urlfetch.InvalidURLError:
        return {'error': 'InvalidUrlError'}

    except urlfetch.DeadlineExceededError:
        return {'error': 'DeadlineExceededError'}

    except urlfetch.DownloadError:
        return {'error': 'DownloadError'}

    except urlfetch.ResponseTooLargeError:
        return {'error': 'ResponseTooLargeError'}

    else:
        try:
            return json.loads(response.content)
        except ValueError:
            return {'error': response.content}


"""
Creates a session with Label API. A Session ID is required for most API calls.
"""
def create_session(user_id=0, app_id=0, device_id=0, data_format='json', version='2.00'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'uid': user_id,
        'appid': app_id,
        'devid':device_id,
        'f': data_format,
        'v': version
    }

    return call_api('GET', 'createsession', params)


"""
Gets nutrition profile. Users can create nutrition profiles 
based on ingredients, nutrients, additives, and allergens to
improve search results.
"""
def get_profile(session_id, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY, 
        'sid': session_id,
        'f': data_format
    }

    return call_api('GET', 'getprofile', params)


"""
Sets nutrition profile. Users can create nutrition profiles 
based on ingredients, nutrients, additives, and allergens to
improve search results.
"""
def set_profile(session_id, user=None):
    profile = settings.LABEL_DEFAULT_PROFILE
    profile['session_id'] = session_id

    # Customize profile according to user-entered parameters
    if user:
        profile['nutrients'] = map(lambda x: {"name": x, "value": "true"}, user.nutrients)
        profile['allergens'] = map(lambda x: {"name": x, "value": "true"}, user.allergens)
        profile['additives'] = map(lambda x: {"name": x, "value": "true"}, user.additives)

    return call_api('POST', 'setprofile', body='api_key={0}&json={1}'.format(settings.LABEL_API_KEY, json.dumps(profile)))


"""
Searches for ingredients
"""
def ingredient_search(session_id, search_term, length=10, start=0, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'q': search_term,
        'n': length,
        's': start,
        'f': data_format
    }

    return call_api('GET', 'ingredientsearch', params)


"""
Adds an ingredient to user profile
"""
def add_ingredient(session_id, ingredient_id, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'id': ingredient_id,
        'f': data_format
    }

    return call_api('GET', 'addmyingredient', params)


"""
Removes an ingredient from user profile
"""
def remove_ingredient(session_id, ingredient_id, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'id': ingredient_id,
        'f': data_format
    }

    return call_api('GET', 'removemyingredient', params)


"""
Gets ingredient description
"""
def show_ingredient(session_id, search_term, ingredient_id, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'input': search_term,
        'id': ingredient_id,
        'f': json
    }

    return call_api('GET', 'showingredient', params)


"""
Searches for products by keywords; keywords can be product type,
product name, barcode, or brand
"""
def search_products(session_id, search_term, length=10, start=0, data_format='json', version='2.00', callback=None):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'q': search_term,
        'n': length,
        's': start,
        'f': data_format,
        'v': version
    }

    if callback:
        params['c'] = callback

    return call_api('GET', 'searchprods', params)


"""
Returns products information with scores between -100 to 100.
Scores are based on compatibility between products and user profiles,
"""
def product_score(session_id, barcode, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'u': barcode,
        'f': data_format
    }

    return call_api('GET', 'productscore', params)


"""
Returns detailed information about a product when given a UPC, including
allergens and additives
"""
def label(session_id, barcode, app_id=0, data_format='json', longitude=None, latitude=None):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'u': barcode,
        'appid': app_id,
        'f': data_format
    }

    if longitude:
        params['long'] = longitude

    if latitude:
        params['lat'] = latitude

    return call_api('GET', 'label', params)


"""
Returns a sorted list of products similar to a query product. The JSON object
returned includes detailed information about the products.
"""
def label_array(session_id, barcode, length=1, start=0, app_id=0, data_format='json', longitude=None, latitude=None):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'u': barcode,
        'n': length,
        's': start,
        'appid': app_id,
        'f': data_format
    }

    if longitude:
        params['long'] = longtitude

    if latitude:
        params['lat'] = latitude

    return call_api('GET', 'labelarray', params)


"""
Returns the product name, its barcode, and an URL to its information page on
FoodEssentials' website.
"""
def label_summary(session_id, barcode, app_id=0, data_format='json', longitude=None, latitude=None):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'u': barcode,
        'appid': app_id,
        'f': data_format
    }

    if longitude:
        params['long'] = longitude

    if latitude:
        params['lat'] = latitude

    return call_api('GET', 'label_summary', params)


"""
Returns allergen and additive information about a product given a product
code, property type, and property name
"""
def get_allergen_additive(session_id, barcode, prop_type, prop_name, app_id=0, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'u': barcode,
        'proptype': prop_type,
        'propery': prop_name,
        'appid': app_id,
        'f': data_format
    }

    return call_api('GET', 'getallergenadditive', params)


"""
Returns property description given a property type and property name
"""
def get_property_description(prop_type, prop_name, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'type': prop_type, 
        'name': prop_name,
        'f': data_format
    }

    return call_api('GET', 'getpropdescription', params)


"""
Returns a user's products list
"""
def get_my_list(session_id, length=10, start=0, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'n': length,
        's': start,
        'f': data_format
    }

    return call_api('GET', 'getmylist', params)


"""
Add a product to a user's list
"""
def add_my_list(session_id, barcode, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'u': barcode,
        'f': data_format
    }

    return call_api('GET', 'addmylist', params)


"""
Removes a product from a user's list
"""
def remove_my_list(session_id, barcode, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'u': barcode,
        'f': data_format
    }

    return call_api('GET', 'removemylist', params)


"""
Returns all search queries of a session
"""
def get_search_log(session_id, length=10, start=0, data_format='json'):
    params = {
        'api_key': settings.LABEL_API_KEY,
        'sid': session_id,
        'n': length,
        's': start,
        'f': data_format
    }

    return call_api('GET', 'getsearchlog', params)
