from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, redirect
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.http import HttpResponse

from google.appengine.api import mail, users
from google.appengine.ext import ndb

from classifood import label, utils, settings, crypto, constants
from classifood.models import User, Temp_User, Order, Search, Shopping_List_Product, Pantry_Product

from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError

from recaptcha.client import captcha
from datetime import datetime

import httplib2
import json
import time
import jwt

"""
Returns the about page
"""
def about(request):
    return render_to_response('about.html')


"""
Adds an additive to a user's additive list
"""
def add_additive(request):
    session_id = request.get_signed_cookie('session_id', default=None)
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    additive = request.POST.get('additive', '')

    if session_id and user and additive and additive not in user.additives:
        user.additives.append(additive)
        set_profile = label.set_profile(session_id, user)
        if 'result' in set_profile and set_profile['result']  == 'success':
            user.put()
            return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Adds an allergen to a user's allergen list
"""
def add_allergen(request):
    session_id = request.get_signed_cookie('session_id', default=None)
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    allergen = request.POST.get('allergen', '')

    if session_id and user and allergen and allergen not in user.allergens:
        user.allergens.append(allergen)
        set_profile = label.set_profile(session_id, user)
        if 'result' in set_profile and set_profile['result']  == 'success':
            user.put()
            return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Adds a nutrient to a user's nutrient list
"""
def add_nutrient(request):
    session_id = request.get_signed_cookie('session_id', default=None)
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    nutrient = request.POST.get('nutrient', '')

    if session_id and user and nutrient and nutrient not in user.nutrients:
        user.nutrients.append(nutrient)
        set_profile = label.set_profile(session_id, user)
        if 'result' in set_profile and set_profile['result']  == 'success':
            user.put()
            return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Adds an ingredient to a user's ingredient list
"""
def add_ingredient(request):
    session_id = request.get_signed_cookie('session_id', default=None)
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    pair = [request.POST.get('ingredient_id', ''), request.POST.get('ingredient_name', '')]

    try:
        pair[0] = int(pair[0])
    except ValueError:
        return HttpResponse('{"result": "failure"}', content_type='application/json')

    if session_id and user and pair[0] and pair[1]:
        if pair in user.ingredients:
            return HttpResponse('{"result": "exists"}', content_type='application/json')

        user.ingredients.append(pair)
        status = label.add_ingredient(session_id, pair[0])
        if 'result' in status and status['result']  == 'success':
            user.put()
            return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Adds a product to the Pantry_Product table
"""
def add_to_pantry(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    barcode = request.POST.get('barcode', '')

    if user and barcode and not Pantry_Product.query(
            Pantry_Product.user_id == user_id,
            Pantry_Product.barcode == barcode).get(keys_only=True):
        Pantry_Product(user_id = user_id, barcode = barcode).put()
        return HttpResponse('{"result": "success"}', content_type='application/json')
        
    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Adds a product to the Shopping_List_Product table
"""
def add_to_shopping_list(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    barcode = request.POST.get('barcode', '')

    if user and barcode and not Shopping_List_Product.query(
            Shopping_List_Product.user_id == user_id,
            Shopping_List_Product.barcode == barcode).get(keys_only=True):
        Shopping_List_Product(user_id = user_id, barcode = barcode).put()
        return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Get credentials from Google using code from client,
and then check if the user already exists in ndb.
"""
def authenticate(request):
    try:
        oauth_flow = OAuth2WebServerFlow(
            client_id=settings.GOOGLE_CLIENT['web']['client_id'],
            client_secret=settings.GOOGLE_CLIENT['web']['client_secret'],
            auth_uri=settings.GOOGLE_CLIENT['web']['auth_uri'],
            token_uri=settings.GOOGLE_CLIENT['web']['token_uri'],    
            redirect_uri='postmessage',
            scope='openid email',
        )
        credentials = json.loads(oauth_flow.step2_exchange(request.body).to_json())
    except FlowExchangeError:
        return HttpResponse('{"result":"failure"}', content_type='application/json')
    else:
        user = User.get_by_id(credentials['id_token']['sub'])
        if not user:
            refr_token = credentials['refresh_token'] if 'refresh_token' in credentials else None
            user = User(
                id = credentials['id_token']['sub'],
                email = credentials['id_token']['email'],
                nutrients = map(lambda x: x['name'], settings.LABEL_DEFAULT_PROFILE['nutrients']),
                allergens = map(lambda x: x['name'], settings.LABEL_DEFAULT_PROFILE['allergens']),
                additives = map(lambda x: x['name'], settings.LABEL_DEFAULT_PROFILE['additives']),
                ingredients = map(lambda x: [x['ingredientid'], x['name']], settings.LABEL_DEFAULT_PROFILE['myingredients']),
                refresh_token = refr_token)
            user.put()

        if user:
            session = label.create_session(user_id=user.key.id())
            session_id = session['session_id'] if 'session_id' in session else None

            # Must set profile before adding ingredients
            label.set_profile(session_id, user)

            for ingredient in user.ingredients:
                label.add_ingredient(session_id, ingredient[0])

            response = HttpResponse(json.dumps({"result": "success", "euid": crypto.encrypt(user.key.id())}), content_type='application/json')
            response.set_signed_cookie('session_id', session_id)
            return response
        
    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Returns the categories page
"""
def categories(request):    
    return render_to_response('categories.html', {'categories': mark_safe(json.dumps(constants.categories))}, RequestContext(request))


"""
Returns the contact form page.
"""
def contact(request):
    return render_to_response('contact.html', {'recaptcha_public_key': settings.RECAPTCHA_PUBLIC_KEY}, RequestContext(request))


"""
Deletes a user's pantry
"""
def delete_pantry(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None

    if user_id:
        Pantry_Product.query(Pantry_Product.user_id == user_id).map(lambda key: key.delete(), keys_only=True)
        return redirect('/user/pantry')

    return redirect('/')


"""
Deletes a user's shopping list
"""
def delete_shopping_list(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None

    if user_id:
        Shopping_List_Product.query(Shopping_List_Product.user_id == user_id).map(lambda key: key.delete(), keys_only=True)
        return redirect('/user/shopping_list')
 
    return redirect('/')


"""
Returns the web home page
"""
def index(request):    
    return render_to_response(
        'index.html', 
        {
            'nutrients': mark_safe(json.dumps(map(lambda x: x[0], constants.known_nutrients))),
            'allergens': mark_safe(json.dumps(map(lambda x: x[0], constants.known_allergens))),
            'additives': mark_safe(json.dumps(map(lambda x: x[0], constants.known_additives))),
        },
        RequestContext(request))


"""
Returns the privacy policy page
"""
def privacy_policy(request):
    return render_to_response('privacy_policy.html')


"""
Removes an additive from a user's additive list
"""
def remove_additive(request):
    session_id = request.get_signed_cookie('session_id', default=None)
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    additive = request.POST.get('additive', '')

    if session_id and user and additive in user.additives:
        user.additives.remove(additive)
        set_profile = label.set_profile(session_id, user)
        if 'result' in set_profile and set_profile['result']  == 'success':
            user.put()
            return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Removes an allergen from a user's allergen list
"""
def remove_allergen(request):
    session_id = request.get_signed_cookie('session_id', default=None)
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    allergen = request.POST.get('allergen', '')

    if session_id and user and allergen in user.allergens:
        user.allergens.remove(allergen)
        set_profile = label.set_profile(session_id, user)
        if 'result' in set_profile and set_profile['result']  == 'success':
            user.put()
            return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Removes a nutrient from a user's nutrient list
"""
def remove_nutrient(request):
    session_id = request.get_signed_cookie('session_id', default=None)
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    nutrient = request.POST.get('nutrient', '')

    if session_id and user and nutrient in user.nutrients:
        user.nutrients.remove(nutrient)
        set_profile = label.set_profile(session_id, user)
        if 'result' in set_profile and set_profile['result']  == 'success':
            user.put()
            return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Removes an ingredient from a user's ingredient list
"""
def remove_ingredient(request):
    session_id = request.get_signed_cookie('session_id', default=None)
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    pair = [request.POST.get('ingredient_id', ''), request.POST.get('ingredient_name', '')]

    try:
        pair[0] = int(pair[0])
    except ValueError:
        return HttpResponse('{"result": "failure"}', content_type='application/json')

    if session_id and user and pair in user.ingredients:
        user.ingredients.remove(pair)
        status = label.remove_ingredient(session_id, pair[0])
        if 'result' in status and status['result']  == 'success':
            user.put()
            return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Removes a product from the Pantry_Product table
"""
def remove_from_pantry(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    barcode = request.POST.get('barcode', '')

    if user_id and barcode:
        # Should get 1 key only
        Pantry_Product.query(
            Pantry_Product.user_id == user_id,
            Pantry_Product.barcode == barcode
        ).map(lambda key: key.delete(), keys_only=True)
        return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Removes a product from the Shopping_List_Product table
"""
def remove_from_shopping_list(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    barcode = request.POST.get('barcode', '')

    if user_id and barcode:
        # Should get 1 key only
        Shopping_List_Product.query(
            Shopping_List_Product.user_id == user_id,
            Shopping_List_Product.barcode == barcode
        ).map(lambda key: key.delete(), keys_only=True)
        return HttpResponse('{"result": "success"}', content_type='application/json')
    
    return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Returns do-not-crawl messages to web-crawler programs for
development and test environments
"""
def robots(request):
    return render_to_response('robots.txt')


"""
Returns a list of search results.
"""
def search(request):
    search_term = request.GET.get('q', '').lower()
    start = request.GET.get('start', '0')
    mobile = request.GET.get('mobile', '')
    user = User.get_by_id(crypto.decrypt(request.COOKIES['euid'])) if 'euid' in request.COOKIES else None
    session_id = request.get_signed_cookie('session_id', default=None)

    if not session_id:
        session = {}
        temp_user = Temp_User()
        temp_user.put()
        while 'session_id' not in session:
            session = label.create_session(user_id='Temp_User_{0}'.format(temp_user.key.id()))
        session_id = session['session_id']
        label.set_profile(session_id)

    products = [] # list of product info dictionaries
    pages = [] # list of (page_start, page_label) tuples
    total_found = 0

    # If start is not an integer, set start to 0
    try:
        start = int(start)
    except ValueError:
        start = 0

    nutr = user.nutrients if user else map(lambda x: x['name'], settings.LABEL_DEFAULT_PROFILE['nutrients'])
    allg = user.allergens if user else map(lambda x: x['name'], settings.LABEL_DEFAULT_PROFILE['allergens'])
    addt = user.additives if user else map(lambda x: x['name'], settings.LABEL_DEFAULT_PROFILE['additives'])
    ingr = user.ingredients if user else []

    in_cache = Search.query(Search.search_term == search_term,
                            Search.start == start,
                            Search.nutrients == nutr,
                            Search.allergens == allg,
                            Search.additives == addt,
                            Search.ingredients == ingr).get()

    # Data in cache and less than 30 days old
    if in_cache and (datetime.utcnow() - in_cache.update_datetime).days < 30:
        products = in_cache.products
        pages = in_cache.pages
        total_found = in_cache.nfound

    else:
        search_result = {}

        while 'numFound' not in search_result:
            search_result = label.search_products(session_id, search_term, start=start)

        total_found = search_result['numFound']

        if total_found > 0:
            products = search_result['productsArray']
            pages = get_pages(start, total_found)

        # Get product details
        for product in products:
            if product['product_size'].strip() == 'none':
                product['product_size'] = ''

            prod_details = label.label_array(session_id, product['upc'])

            if 'productsArray' in prod_details:
                product['details'] = prod_details['productsArray'][0]
                product['contains'] = []
                product['may_contain'] = []

                # Get nutrient percentage value
                for nutrient in product['details']['nutrients']:
                    if nutrient['nutrient_name'] in constants.DAILY_VALUES and nutrient['nutrient_uom'] in constants.UNIT_MULTIPLIER:
                        try:
                            nutrient['percentage_value'] = '{:.0%}'.format(float(nutrient['nutrient_value']) * constants.UNIT_MULTIPLIER[nutrient['nutrient_uom']] / constants.DAILY_VALUES[nutrient['nutrient_name']][1])
                        except ValueError:
                            nutrient['percentage_value'] = ''

                for allergen in product['details']['allergens']:
                    if allergen['allergen_value'] == '2':
                        product['contains'].append(allergen['allergen_name'])
                    elif allergen['allergen_value'] == '1':
                        product['may_contain'].append(allergen['allergen_name'])

                for additive in product['details']['additives']:
                    if additive['additive_value'] == '2':
                        product['contains'].append(additive['additive_name'])
                    elif additive['additive_value'] == '1':
                        product['may_contain'].append(additive['additive_name'])

                for ingredient in product['details']['procingredients']:
                    if ingredient['value'] == 2:
                        product['contains'].append(ingredient['name'])
                    elif ingredient['value'] == 1:
                        product['may_contain'].append(ingredient['name'])

        # Add to cache
        Search(search_term = search_term,
               start = start,
               nutrients = nutr,
               allergens = allg,
               additives = addt,
               ingredients = ingr,
               products = products,
               pages = pages,
               nfound = total_found).put()

    for product in products:
        # Check if product is on user shopping list
        if user and Shopping_List_Product.query(
                Shopping_List_Product.user_id == user.key.id(),
                Shopping_List_Product.barcode == product['upc']
        ).get(keys_only=True):
            product['on_shopping_list'] = 'true'

        # Check if product is on user shopping list
        if user and Pantry_Product.query(
                Pantry_Product.user_id == user.key.id(),
                Pantry_Product.barcode == product['upc']
        ).get(keys_only=True):
            product['in_pantry'] = 'true'

    response = render_to_response(
        'search.html', 
        {
            'search_term': search_term,
            'products': products,
            'products_len': len(products),
            'pages': pages,
            'start': start,
            'total_found': total_found,
        },
        RequestContext(request))

    response.set_signed_cookie('session_id', session_id)

    return response


"""
Searches Label API for ingredients by name and returns JSON
"""
def search_ingredients(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    session_id = request.get_signed_cookie('session_id', default=None)
    search_term = request.GET.get('ingredient', '')

    if user_id and session_id and search_term:
        start = request.GET.get('start', '0')
        try:
            start = int(start)
        except ValueError:
            start = 0

        search_result = label.ingredient_search(session_id, search_term, start=start)

        if 'error' not in search_result:
            return HttpResponse(
                json.dumps(
                    {
                        'result': 'success',
                        'start': start,
                        'total_found': search_result['numFound'],
                        'ingredients': search_result['arrayIngredients']
                    }), 
                content_type='application/json')
    
    return HttpResponse('{"result": "failure"}', content_type='application/json')

"""
Verifies reCaptcha and sends email to the designated email
"""
def send_contact_message(request):
    recaptcha_challenge_field = request.POST.get('recaptcha_challenge_field', '')
    recaptcha_response_field = request.POST.get('recaptcha_response_field', '')
    sender_email = request.POST.get('sender_email', '').strip()
    subject = request.POST.get('subject', '').strip()
    body = request.POST.get('body', '').strip()

    if not sender_email:
        return HttpResponse('empty_sender_email', content_type='text/plain')

    if sender_email.find('@') == -1 or sender_email.find('.') == -1:
        return HttpResponse('sender_email_not_email', content_type='text/plain')

    if not subject:
        return HttpResponse('empty_subject', content_type='text/plain')

    if not body:
        return HttpResponse('empty_body', content_type='text/plain')

    if len(body) > 3000:
        return HttpResponse('over_max_body', content_type='text/plain')
    
    recaptcha_response = captcha.submit(
        recaptcha_challenge_field,
        recaptcha_response_field,
        settings.RECAPTCHA_PRIVATE_KEY,
        request.META['REMOTE_ADDR'])

    if recaptcha_response.is_valid:
        body_wrapper = u'A message from ' + sender_email + ":\n\n"
        mail.send_mail(
            sender=settings.MAILER_EMAIL,
            to=settings.CONTACT_RECIPIENT_EMAIL,
            subject=subject,
            body=body_wrapper+body)

        return HttpResponse('sent', content_type='text/plain')

    return HttpResponse('recaptcha_failed', content_type='text/plain')


"""
Returns user signin page
"""
def signin(request):
    return render_to_response('signin.html', context_instance=RequestContext(request))


"""
Returns a sitemap XML
"""
def sitemap(request):
    return render_to_response('sitemap.xml', {'categories': constants.categories}, RequestContext(request))


"""
Returns the terms of service page
"""
def terms_of_service(request):
    return render_to_response('terms_of_service.html')


"""
Returns the user pantry page
"""
def user_pantry(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    session_id = request.get_signed_cookie('session_id', default=None)

    if user_id and session_id:
        user = User.get_by_id(user_id)
        start = request.GET.get('start', '0')
        label_error = False

        try:
            start = int(start)
        except ValueError:
            start = 0

        # Get shopping list products by user_id        
        prod_entities = Pantry_Product.query(Pantry_Product.user_id == user_id).order(-Pantry_Product.add_datetime).fetch(limit=10, offset=start)

        # Get total number of shopping list
        total = Pantry_Product.query(Pantry_Product.user_id == user_id).count()

        products = []
        length = 0
        now = datetime.utcnow()

        for entity in prod_entities:
            # Get product detailed info
            prod_details = label.label_array(session_id, entity.barcode)

            if 'productsArray' in prod_details:
                products.append(prod_details['productsArray'][0])
                length += 1
                products[length-1]['contains'] = []
                products[length-1]['may_contain'] = []

                # Get nutrient percentage value
                for nutrient in products[length-1]['nutrients']:
                    if nutrient['nutrient_name'] in constants.DAILY_VALUES and nutrient['nutrient_uom'] in constants.UNIT_MULTIPLIER:
                        try:
                            nutrient['percentage_value'] = '{:.0%}'.format(float(nutrient['nutrient_value']) * constants.UNIT_MULTIPLIER[nutrient['nutrient_uom']] / constants.DAILY_VALUES[nutrient['nutrient_name']][1])
                        except ValueError:
                            nutrient['percentage_value'] = ''

                for allergen in products[length-1]['allergens']:
                    if allergen['allergen_value'] == '2':
                        products[length-1]['contains'].append(allergen['allergen_name'])
                    elif allergen['allergen_value'] == '1':
                        products[length-1]['may_contain'].append(allergen['allergen_name'])

                for additive in products[length-1]['additives']:
                    if additive['additive_value'] == '2':
                        products[length-1]['contains'].append(additive['additive_name'])
                    elif additive['additive_value'] == '1':
                        products[length-1]['may_contain'].append(additive['additive_name'])

                for ingredient in products[length-1]['procingredients']:
                    if ingredient['value'] == 2:
                        products[length-1]['contains'].append(ingredient['name'])
                    elif ingredient['value'] == 1:
                        products[length-1]['may_contain'].append(ingredient['name'])

            else:
                label_error=True
                break

            # Check if product is on user shopping list
            if Shopping_List_Product.query(
                    Shopping_List_Product.user_id == user_id,
                    Shopping_List_Product.barcode == entity.barcode
            ).get(keys_only=True):
                products[length-1]['on_shopping_list'] = 'true'

            # Get time between now when product was added
            products[length-1]['t_delta'] = utils.get_time_delta_str(now - entity.add_datetime)

        pages = get_pages(start, total)

        return render_to_response(
            'user_pantry.html',
            {
                'products': products,
                'products_len': len(products),
                'total': total,
                'start': start,
                'pages': pages,
                'label_error': label_error,
            },
            RequestContext(request))

    return redirect('/signin')


"""
Returns user profile page
"""
def user_profile(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None

    if user_id:
        user = User.get_by_id(user_id)
        upgrade_token = None

        if not user.is_premium:
            upgrade_token = jwt.encode(
                {
                    'iss': settings.GOOGLE_SELLER_ID,
                    'aud': 'Google', # Must be Google
                    'typ': 'google/payments/inapp/item/v1', # Must be google/payments/inapp/item/v1
                    'exp': int(time.time()+3600), # expiration time
                    'iat': int(time.time()), # issue time
                    'request': {
                        'name': 'Classifood Upgrade',
                        'description': 'Upgrade for premium features on Classifood',
                        'price': '3.00',
                        'currencyCode': 'USD',
                        'sellerData': 'user_id:{0}'.format(user_id)
                    }
                }, settings.GOOGLE_SELLER_SECRET)

        return render_to_response(
            'user_profile.html',
            {
                'user': user,
                'upgrade_token': upgrade_token,
                'known_nutrients': constants.known_nutrients,
                'known_allergens': constants.known_allergens,
                'known_additives': constants.known_additives
            },
            RequestContext(request))

    return redirect('/signin')    


"""
Returns the user shopping list
"""
def user_shopping_list(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    session_id = request.get_signed_cookie('session_id', default=None)
    
    if user_id and session_id:
        user = User.get_by_id(user_id)
        start = request.GET.get('start', '0')
        label_error = False

        try:
            start = int(start)
        except ValueError:
            start = 0

        # Get shopping list products by user_id        
        prod_entities = Shopping_List_Product.query(Shopping_List_Product.user_id == user_id).order(-Shopping_List_Product.add_datetime).fetch(limit=10, offset=start)

        # Get total number of shopping list
        total = Shopping_List_Product.query(Shopping_List_Product.user_id == user_id).count()

        products = []
        length = 0
        now = datetime.utcnow()

        for entity in prod_entities:
            # Get product detailed info
            prod_details = label.label_array(session_id, entity.barcode)

            if 'productsArray' in prod_details:
                products.append(prod_details['productsArray'][0])
                length += 1
                products[length-1]['contains'] = []
                products[length-1]['may_contain'] = []

                # Get nutrient percentage value
                for nutrient in products[length-1]['nutrients']:
                    if nutrient['nutrient_name'] in constants.DAILY_VALUES and nutrient['nutrient_uom'] in constants.UNIT_MULTIPLIER:
                        try:
                            nutrient['percentage_value'] = '{:.0%}'.format(float(nutrient['nutrient_value']) * constants.UNIT_MULTIPLIER[nutrient['nutrient_uom']] / constants.DAILY_VALUES[nutrient['nutrient_name']][1])
                        except ValueError:
                            nutrient['percentage_value'] = ''

                for allergen in products[length-1]['allergens']:
                    if allergen['allergen_value'] == '2':
                        products[length-1]['contains'].append(allergen['allergen_name'])
                    elif allergen['allergen_value'] == '1':
                        products[length-1]['may_contain'].append(allergen['allergen_name'])

                for additive in products[length-1]['additives']:
                    if additive['additive_value'] == '2':
                        products[length-1]['contains'].append(additive['additive_name'])
                    elif additive['additive_value'] == '1':
                        products[length-1]['may_contain'].append(additive['additive_name'])

                for ingredient in products[length-1]['procingredients']:
                    if ingredient['value'] == 2:
                        products[length-1]['contains'].append(ingredient['name'])
                    elif ingredient['value'] == 1:
                        products[length-1]['may_contain'].append(ingredient['name'])

            else:
                label_error=True
                break

            # Check if product is on user shopping list
            if Pantry_Product.query(
                    Pantry_Product.user_id == user_id,
                    Pantry_Product.barcode == entity.barcode
            ).get(keys_only=True):
                products[length-1]['in_pantry'] = 'true'

            # Get time between now when product was added
            products[length-1]['t_delta'] = utils.get_time_delta_str(now - entity.add_datetime)

        pages = get_pages(start, total)

        return render_to_response(
            'user_shopping_list.html',
            {
                'products': products,
                'products_len': len(products),
                'total': total,
                'start': start,
                'pages': pages,
                'label_error': label_error,
            },
            RequestContext(request))

    return redirect('/signin')


"""
Verifies Google Checkout purchase
"""
@csrf_exempt
def verify_purchase(request):
    if request.method == 'POST':
        data = jwt.decode(request.POST.get('jwt', None), settings.GOOGLE_SELLER_SECRET)

	if data and data['request']['name'] == 'Classifood Upgrade' and data['request']['sellerData'].find('user_id') != -1:
	    user = User.get_by_id(data['request']['sellerData'][8:])
	    if user:
	        user.is_premium = True
	        user.put()
		Order(id = data['response']['orderId'],
                      user_id = user.key.id(),
                      name = data['request']['name'],
                      description = data['request']['description'],
                      price = data['request']['price'],
                      currency = data['request']['currencyCode']).put()

                return HttpResponse(data['response']['orderId'], content_type='text/plain')

    return HttpResponse('error', content_type='text/plain')


"""
Returns the 404 error - not found - page
"""
def err404(request):
    return render_to_response('404.html')


"""
Returns the 500 error - internal server error - page
"""
def err500(request):
    return render_to_response('500.html')


"""
Returns (start, label) tuples for pagination
"""
def get_pages(start, total):
    pages = []

    # Start row of a 5-page batch    
    first_page_start = start / 50 * 50

    # Is there a previous batch of pages?
    if first_page_start - 50 >= 0:
        previous_start = first_page_start - 50
        previous_label = previous_start / 10 + 1
        pages.append((previous_start, '%i - %i' % (previous_label, previous_label + 4)))

    # Current pages
    page_start = first_page_start
    page_label = page_start / 10 + 1
    i = 0
    while i < 5 and page_start < total:
        pages.append((page_start, str(page_label)))
        page_start += 10
        page_label += 1
        i += 1

    # Is there a next batch of pages?
    if first_page_start + 50 < total:
        next_start = first_page_start + 50
        next_label = next_start / 10 + 1
        pages.append((next_start, "%i - %i" % (next_label, next_label + 4)))

    return pages
