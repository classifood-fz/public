from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, redirect
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.http import HttpResponse

from google.appengine.api import mail
from google.appengine.ext import ndb

from classifood import label_api, utils, settings, crypto, constants
from classifood.models import User, Order, Search_Cache, Shopping_List_Product, Pantry_Product, Label

from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError

from recaptcha.client import captcha
from datetime import datetime
from datetime import timedelta

import stripe
import json
import time

def about(request):
    """
    Returns the about page
    """
    return render_to_response('about.html')


def add_additive(request):
    """
    Adds an additive to a user's additive list
    """
    try:
        session_id = request.get_signed_cookie('session_id', default=None)
        euid = request.COOKIES.get('euid')
        user = User.get_by_id(crypto.decrypt(euid))
        additive_name = request.POST.get('additive', '')
        additive = Label.query(
            Label.user_id == user.key.id(),
            Label.name == additive_name).get(keys_only=True)

        if session_id and not additive:
            profile = user.get_profile()

            for a in profile['additives']:
                if a['name'] == additive_name: a['value'] = 'true'

            response = label_api.set_profile(session_id, profile)
            if response.get('result')  == 'success':
                Label(user_id=user.key.id(), name=additive_name).put_async()
                return HttpResponse('{"result": "success"}', content_type='application/json')
    except:
        pass

    return HttpResponse('{"result": "failure"}', content_type='application/json')


def add_allergen(request):
    """
    Adds an allergen to a user's allergen list
    """
    try:
        session_id = request.get_signed_cookie('session_id', default=None)
        euid = request.COOKIES.get('euid')
        user = User.get_by_id(crypto.decrypt(euid))
        allergen_name = request.POST.get('allergen', '')
        allergen = Label.query(
            Label.user_id == user.key.id(),
            Label.name == allergen_name).get(keys_only=True)

        if session_id and not allergen:
            profile = user.get_profile()

            for a in profile['allergens']:
                if a['name'] == allergen_name: a['value'] = 'true'

            response = label_api.set_profile(session_id, profile)

            if response.get('result')  == 'success':
                Label(user_id = user.key.id(), name = allergen_name).put_async()
                return HttpResponse('{"result": "success"}', content_type='application/json')
    except:
        pass

    return HttpResponse('{"result": "failure"}', content_type='application/json')


def add_ingredient(request):
    """
    Adds an ingredient to a user's ingredient list
    """
    try:
        session_id = request.get_signed_cookie('session_id', default=None)
        user_id = crypto.decrypt(request.COOKIES.get('euid', ''))
        ingredient_id = request.POST.get('ingredient_id', '')
        ingredient_name = request.POST.get('ingredient_name', '')
        ingredient = Label.query(
            Label.user_id == user_id,
            Label.name == ingredient_name,
            Label.sub_id == ingredient_id).get(keys_only=True)

        if session_id and not ingredient:
            response = label_api.add_ingredient(session_id, ingredient_id)

            if response.get('result')  == 'success':
                Label(user_id=user_id, name=ingredient_name, sub_id=ingredient_id).put_async()
                return HttpResponse('{"result": "success"}', content_type='application/json')

    except:
        pass

    return HttpResponse('{"result": "failure"}', content_type='application/json')


def add_nutrient(request):
    """
    Adds a nutrient to a user's nutrient list
    """
    try:
        session_id = request.get_signed_cookie('session_id', default=None)
        euid = request.COOKIES.get('euid')
        user = User.get_by_id(crypto.decrypt(euid))
        nutrient_name = request.POST.get('nutrient', '')
        nutrient = Label.query(
            Label.user_id == user.key.id(),
            Label.name == nutrient_name).get(keys_only=True)

        if session_id and not nutrient:
            profile = user.get_profile()

            for n in profile['nutrients']:
                if n['name'] == nutrient_name: n['value'] = 'true'

            response = label_api.set_profile(session_id, profile)

            if response.get('result')  == 'success':
                Label(user_id = user.key.id(), name = nutrient_name).put_async()
                return HttpResponse('{"result": "success"}', content_type='application/json')
    except:
        pass

    return HttpResponse('{"result": "failure"}', content_type='application/json')


def add_to_pantry(request):
    """
    Adds a product to the Pantry_Product table
    """
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    barcode = request.POST.get('barcode', '')

    if user and barcode and not Pantry_Product.query(
            Pantry_Product.user_id == user_id,
            Pantry_Product.barcode == barcode).get(keys_only=True):
        Pantry_Product(user_id = user_id, barcode = barcode).put()
        return HttpResponse('{"result": "success"}', content_type='application/json')
        
    return HttpResponse('{"result": "failure"}', content_type='application/json')


def add_to_shopping_list(request):
    """
    Adds a product to the Shopping_List_Product table
    """
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    barcode = request.POST.get('barcode', '')

    if user and barcode and not Shopping_List_Product.query(
            Shopping_List_Product.user_id == user_id,
            Shopping_List_Product.barcode == barcode).get(keys_only=True):
        Shopping_List_Product(user_id = user_id, barcode = barcode).put()
        return HttpResponse('{"result": "success"}', content_type='application/json')

    return HttpResponse('{"result": "failure"}', content_type='application/json')


def authenticate(request):
    """
    Get credentials from Google using code from client,
    and then check if the user already exists in ndb.
    """
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
            user = User(
                id = credentials['id_token']['sub'],
                email = credentials['id_token']['email'],
                refresh_token = credentials.get('refresh_token'))
            user.put()

        try:
            uid = user.key.id()
            session = label_api.create_session(user_id=uid, app_id=uid, device_id=uid)
            session_id = session.get('session_id')

            if not session_id:
                raise Exception

            # Must set profile before adding ingredients
            response = label_api.set_profile(session_id, user.get_profile())

            if response.get('result') != 'success':
                raise Exception

            for label in Label.query(Label.user_id == uid, Label.sub_id != '').fetch():
                label_api.add_ingredient(session_id, label.sub_id)

            response = HttpResponse(json.dumps({
                "success": True,
                "euid": crypto.encrypt(uid)
            }), content_type='application/json')

            response.set_signed_cookie('session_id', session_id)

            return response
        except:
            pass

    return HttpResponse('{"success": false}', content_type='application/json')


def categories(request):    
    """
    Returns the categories page
    """
    return render_to_response(
        'categories.html', {
            'categories': mark_safe(json.dumps(constants.categories))}, 
        RequestContext(request))


def contact(request):
    """
    Returns the contact form page.
    """
    return render_to_response(
        'contact.html', {
            'recaptcha_public_key': settings.RECAPTCHA_PUBLIC_KEY}, 
        RequestContext(request))


def checkout(request):
    """
    Stripe checkout
    """
    user_id = crypto.decrypt(request.COOKIES.get('euid', ''))
    user = User.get_by_id(user_id)

    if not user:
        return redirect('/')

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        charge = stripe.Charge.create(
            amount=800, # amount in cents
            currency='usd',
            source=request.POST.get('stripeToken', ''),
            description='Classifood upgrade for {0}'.format(request.POST.get('stripeEmail'))
        )

        if charge.get('status') != 'succeeded':
            raise Exception
    except:
        print 'Stripe Error: Failed to charge user {0}'.format(user_id)
        return redirect('/user/profile?upgrade_status=0')
    else:
        Order(user_id = user_id,
              name = request.POST.get('name'),
              description = request.POST.get('description'),
              price = int(request.POST.get('price'))).put()
        user.group_id = 2
        user.upgrade_exp = datetime.utcnow() + timedelta(days=180)
        user.put()

    return redirect('/user/profile')

def delete_pantry(request):
    """
    Deletes a user's pantry
    """
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None

    if user_id:
        Pantry_Product.query(Pantry_Product.user_id == user_id).map(
            lambda key: key.delete(), keys_only=True)
        return redirect('/user/pantry')

    return redirect('/')


def delete_shopping_list(request):
    """
    Deletes a user's shopping list
    """
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None

    if user_id:
        Shopping_List_Product.query(Shopping_List_Product.user_id == user_id).map(
            lambda key: key.delete(), keys_only=True)
        return redirect('/user/shopping_list')
 
    return redirect('/')


def index(request):    
    """
    Returns the web home page
    """
    return render_to_response(
        'index.html', 
        {
            'nutrients': mark_safe(json.dumps(map(lambda x: x[0], constants.known_nutrients))),
            'allergens': mark_safe(json.dumps(map(lambda x: x[0], constants.known_allergens))),
            'additives': mark_safe(json.dumps(map(lambda x: x[0], constants.known_additives))),
        },
        RequestContext(request))


def privacy_policy(request):
    """
    Returns the privacy policy page
    """
    return render_to_response('privacy_policy.html')


def remove_additive(request):
    """
    Removes an additive from a user's additive list
    """
    try:
        session_id = request.get_signed_cookie('session_id', default=None)
        euid = request.COOKIES.get('euid')
        user = User.get_by_id(crypto.decrypt(euid))
        additive_name = request.POST.get('additive', '')
        additive = Label.query(
            Label.user_id == user.key.id(),
            Label.name == additive_name).get(keys_only=True)

        if session_id and additive:
            profile = user.get_profile()

            for a in profile['additives']:
                if a['name'] == additive_name: a['value'] = 'false'

            response = label_api.set_profile(session_id, profile)

            if response.get('result')  == 'success':
                additive.delete_async()
                return HttpResponse('{"result": "success"}', content_type='application/json')
    except:
        pass

    return HttpResponse('{"result": "failure"}', content_type='application/json')


def remove_allergen(request):
    """
    Removes an allergen from a user's allergen list
    """
    try:
        session_id = request.get_signed_cookie('session_id', default=None)
        euid = request.COOKIES.get('euid')
        user = User.get_by_id(crypto.decrypt(euid))
        allergen_name = request.POST.get('allergen', '')
        allergen = Label.query(
            Label.user_id == user.key.id(),
            Label.name == allergen_name).get(keys_only=True)

        if session_id and allergen:
            profile = user.get_profile()

            for a in profile['allergens']:
                if a['name'] == allergen_name: a['value'] = 'false'

            response = label_api.set_profile(session_id, profile)

            if response.get('result')  == 'success':
                allergen.delete_async()
                return HttpResponse('{"result": "success"}', content_type='application/json')
    except:
        pass

    return HttpResponse('{"result": "failure"}', content_type='application/json')


def remove_ingredient(request):
    """
    Removes an ingredient from a user's ingredient list
    """
    try:
        session_id = request.get_signed_cookie('session_id', default=None)
        user_id = crypto.decrypt(request.COOKIES.get('euid', ''))
        ingredient_id = request.POST.get('ingredient_id')
        ingredient_name = request.POST.get('ingredient_name')
        ingredient = Label.query(
            Label.user_id == user_id,
            Label.name == ingredient_name,
            Label.sub_id == ingredient_id).get(keys_only=True)

        if session_id and ingredient:
            response = label_api.remove_ingredient(session_id, ingredient_id)

            if response.get('result') == 'success':
                ingredient.delete_async()
                return HttpResponse('{"result": "success"}', content_type='application/json')    

    except:
        pass

    return HttpResponse('{"result": "failure"}', content_type='application/json')


def remove_nutrient(request):
    """
    Removes a nutrient from a user's nutrient list
    """
    try:
        session_id = request.get_signed_cookie('session_id', default=None)
        euid = request.COOKIES.get('euid')
        user = User.get_by_id(crypto.decrypt(euid))
        nutrient_name = request.POST.get('nutrient', '')
        nutrient = Label.query(
            Label.user_id == user.key.id(),
            Label.name == nutrient_name).get(keys_only=True)

        if session_id and nutrient:
            profile = user.get_profile()

            for n in profile['nutrients']:
                if n['name'] == nutrient_name: n['value'] = 'false'

            response = label_api.set_profile(session_id, profile)

            if response.get('result')  == 'success':
                nutrient.delete_async()
                return HttpResponse('{"result": "success"}', content_type='application/json')
    except:
        pass

    return HttpResponse('{"result": "failure"}', content_type='application/json')


def remove_from_pantry(request):
    """
    Removes a product from the Pantry_Product table
    """
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


def remove_from_shopping_list(request):
    """
    Removes a product from the Shopping_List_Product table
    """
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


def robots(request):
    """
    Returns do-not-crawl messages to web-crawler programs for
    development and test environments
    """
    return render_to_response('robots.txt')


def search(request):
    """
    Returns a list of search results.
    """
    search_term = request.GET.get('q').lower()
    start = request.GET.get('start', '0')
    mobile = request.GET.get('mobile')
    user = User.get_by_id(crypto.decrypt(request.COOKIES['euid'])) if 'euid' in request.COOKIES else None
    session_id = request.get_signed_cookie('session_id', default=None)

    if not session_id:
        session = {}
        while 'session_id' not in session:
            session = label_api.create_session()
        session_id = session['session_id']
        label_api.set_profile(session_id)

    products = [] # list of product info dictionaries
    pages = [] # list of (page_start, page_label) tuples
    total_found = 0

    # If start is not an integer, set start to 0
    try:
        start = int(start)
    except ValueError:
        start = 0

    if user:
        profile_hash = crypto.get_hmac_sha256_hash(json.dumps(user.get_profile(), sort_keys=True))
    else:
        profile_hash = crypto.get_hmac_sha256_hash(json.dumps({
            "nutrients": [
                {"name": "Calories", "value": "true"},
                {"name": "Total Fat", "value": "true"},
                {"name": "Cholesterol", "value": "true"},
                {"name": "Sodium", "value": "true"},
                {"name": "Total Carbohydrate", "value": "true"},
                {"name": "Dietary Fiber", "value": "true"},
                {"name": "Sugars", "value": "true"},
                {"name": "Protein", "value": "true"}
            ],
            "allergens": [
                {"name": "Gluten", "value": "true"}
            ],
            "additives": [
                {"name": "Preservatives", "value": "true"}
            ],
            "myingredients": [],
            "mysort": [
                {
                    "sort_variable": "Calories",
                    "sort_order": 1,
                    "variable_type": 1
                }
            ],
        }, sort_keys=True))

    cached = Search_Cache.query(
        Search_Cache.profile_hash == profile_hash,
        Search_Cache.search_term == search_term,
        Search_Cache.start == start).get()

    # Data in cache and less than 5 days old
    if cached and (datetime.utcnow() - cached.updated_on).days < 5:
        products = cached.products
        pages = cached.pages
        total_found = cached.nfound

    else:
        if cached: cached.key.delete()

        search_result = {}

        while 'numFound' not in search_result:
            search_result = label_api.search_products(session_id, search_term, start=start)

        total_found = search_result['numFound']

        if total_found > 0:
            products = search_result['productsArray']
            pages = get_pages(start, total_found)

        # Get product details
        for product in products:
            if product['product_size'].strip() == 'none':
                product['product_size'] = ''

            prod_details = label_api.label_array(session_id, product['upc'])

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
        Search_Cache(profile_hash = profile_hash,
               search_term = search_term,
               start = start,
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


def search_ingredients(request):
    """
    Searches Label API for ingredients by name and returns JSON
    """
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    session_id = request.get_signed_cookie('session_id', default=None)
    search_term = request.GET.get('ingredient', '')

    if user_id and session_id and search_term:
        start = request.GET.get('start', '0')
        try:
            start = int(start)
        except ValueError:
            start = 0

        search_result = label_api.ingredient_search(session_id, search_term, start=start)

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


def send_contact_message(request):
    """
    Verifies reCaptcha and sends email to the designated email
    """
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


def signin(request):
    """
    Returns user signin page
    """
    return render_to_response('signin.html', {
        'google_client_id': settings.GOOGLE_CLIENT['web']['client_id']
    }, context_instance=RequestContext(request))


def sitemap(request):
    """
    Returns a sitemap XML
    """
    return render_to_response('sitemap.xml', {
        'categories': constants.categories}, RequestContext(request))


def terms_of_service(request):
    """
    Returns the terms of service page
    """
    return render_to_response('terms_of_service.html')


def user_pantry(request):
    """
    Returns the user pantry page
    """
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
        prod_entities = Pantry_Product.query(
            Pantry_Product.user_id == user_id).order(
                -Pantry_Product.added_on).fetch(limit=5, offset=start)

        # Get total number of shopping list
        total = Pantry_Product.query(Pantry_Product.user_id == user_id).count()

        products = []
        length = 0
        now = datetime.utcnow()

        for entity in prod_entities:
            # Get product detailed info
            prod_details = label_api.label_array(session_id, entity.barcode)

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
            products[length-1]['t_delta'] = utils.get_time_delta_str(now - entity.added_on)

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


def user_profile(request):
    """
    Returns user profile page
    """
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    session_id = request.get_signed_cookie('session_id', default=None)

    if user_id and session_id:
        user = User.get_by_id(user_id)
        profile = user.get_profile()
        show_expired = False
        show_failed_upgrade = False

        if user.group_id == 2: # Upgraded user
            now = datetime.utcnow()
            if user.upgrade_exp < now:
                user.group_id = 1
                user.reset_profile(session_id)
                user.put()
                if (now - user.upgrade_exp).days < 3:
                    show_expired = True

        if request.GET.get('upgrade_status') == '0':
            show_failed_upgrade = True

        def filter_list(a_list):
            result = {}
            for x in a_list:
                if x['value'] == 'true':
                    result[x['name']] = True
            return result

        user_nutrients = filter_list(profile['nutrients'])
        user_allergens = filter_list(profile['allergens'])
        user_additives = filter_list(profile['additives'])
        user_ingredients = Label.query(
            Label.user_id == user_id,
            Label.sub_id != None).fetch()

        return render_to_response(
            'user_profile.html',
            {
                'user': user,
                'user_nutrients': user_nutrients,
                'user_allergens': user_allergens,
                'user_additives': user_additives,
                'user_ingredients': user_ingredients,
                'known_nutrients': constants.known_nutrients,
                'known_allergens': constants.known_allergens,
                'known_additives': constants.known_additives,
                'show_expired': show_expired,
                'show_failed_upgrade': show_failed_upgrade,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY
            },
            RequestContext(request))

    return redirect('/signin')    


def user_shopping_list(request):
    """
    Returns the user shopping list
    """
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
        prod_entities = Shopping_List_Product.query(
            Shopping_List_Product.user_id == user_id).order(
                -Shopping_List_Product.added_on).fetch(limit=5, offset=start)

        # Get total number of shopping list
        total = Shopping_List_Product.query(Shopping_List_Product.user_id == user_id).count()

        products = []
        length = 0
        now = datetime.utcnow()

        for entity in prod_entities:
            # Get product detailed info
            prod_details = label_api.label_array(session_id, entity.barcode)

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
            products[length-1]['t_delta'] = utils.get_time_delta_str(now - entity.added_on)

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

def err404(request):
    """
    Returns the 404 error - not found - page
    """
    return render_to_response('404.html')


def err500(request):
    """
    Returns the 500 error - internal server error - page
    """
    return render_to_response('500.html')


def get_pages(start, total):
    """
    Returns (start, label) tuples for pagination
    """
    pages = []

    # Start row of a 5-page batch    
    first_page_start = start / 25 * 25

    # Is there a previous batch of pages?
    if first_page_start - 25 >= 0:
        previous_start = first_page_start - 25
        previous_label = previous_start / 5 + 1
        pages.append((previous_start, '{0} - {1}'.format(previous_label, previous_label + 4)))

    # Current pages
    page_start = first_page_start
    page_label = page_start / 5 + 1
    i = 0
    while i < 5 and page_start < total:
        pages.append((page_start, str(page_label)))
        page_start += 5
        page_label += 1
        i += 1

    # Is there a next batch of pages?
    if first_page_start + 25 < total:
        next_start = first_page_start + 25
        next_label = next_start / 5 + 1
        pages.append((next_start, '{0} - {1}'.format(next_label, next_label + 4)))

    return pages
