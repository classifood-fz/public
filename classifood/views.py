from django.shortcuts import render_to_response, redirect
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import http

from google.appengine.api import mail, users, images, urlfetch
from google.appengine.ext import ndb, blobstore

from classifood import label, utils, settings, crypto, amazon, categories
from classifood.models import User, Shopping_List_Product, Pantry_Product

from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError

from recaptcha.client import captcha
from datetime import datetime

import httplib2
import json


"""
Returns the about page
"""
def about(request):
    return render_to_response('about.html', {})


"""
Adds an additive to a user's additive list
"""
def add_additive(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    additive = request.POST.get('additive', '')
    description = label.get_property_description('additive', additive)

    if user and additive and additive not in user.additives and description and 'error' not in description:
        user.additives.append(additive)
        user.put()
        return HttpResponse('{"result": "success"}', content_type='application/json')

    elif user and additive and additive not in user.additives and not description:
        return HttpResponse('{"result": "not found"}', content_type='application/json')

    elif user and additive and additive in user.additives:
        return HttpResponse('{"result": "exists"}', content_type='application/json')

    else:
        return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Adds an allergen to a user's allergen list
"""
def add_allergen(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    allergen = request.POST.get('allergen', '')
    description = label.get_property_description('allergen', allergen)

    if user and allergen and allergen not in user.allergens and description and 'error' not in description:
        user.allergens.append(allergen)
        user.put()
        return HttpResponse('{"result": "success"}', content_type='application/json')

    elif user and allergen and allergen not in user.allergens and not description:
        return HttpResponse('{"result": "not found"}', content_type='application/json')

    elif user and allergen and allergen in user.allergens:
        return HttpResponse('{"result": "exists"}', content_type='application/json')

    else:
        return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Adds a nutrient to a user's nutrient list
"""
def add_nutrient(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    nutrient = request.POST.get('nutrient', '')
    description = label.get_property_description('nutrient', nutrient)

    if user and nutrient and nutrient not in user.nutrients and description and 'error' not in description:
        user.nutrients.append(nutrient)
        user.put()
        return HttpResponse('{"result": "success"}', content_type='application/json')

    elif user and nutrient and nutrient not in user.nutrients and not description:
            return HttpResponse('{"result": "not found"}', content_type='application/json')

    elif user and nutrient and nutrient in user.nutrients:
        return HttpResponse('{"result": "exists"}', content_type='application/json')

    else:
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

    elif user and barcode:
        return HttpResponse('{"result": "found"}', content_type='application/json')

    else:
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

    elif user and barcode:
        return HttpResponse('{"result": "found"}', content_type='application/json')

    else:
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
                nutrients = [
                    'Calories',
                    'Total Fat',
                    'Cholesterol',
                    'Sodium',
                    'Potassium',
                    'Total Carbohydrate',
                    'Dietary Fiber',
                    'Sugars',
                    'Protein',
                    'Vitamin A',
                    'Vitamin C',
                    'Calcium'
                ],
                allergens = ['Gluten'],
                additives = [],
                ingredients = [],
                is_admin = False,
                is_advertiser = False,
                is_paying = False,
                refresh_token = refr_token)
            user.put()

        session = label.create_session(user_id=user.key.id())
        session_id = session['session_id'] if 'session_id' in session else None

        if user and session_id:
            response = HttpResponse(
                json.dumps({"result": "success", "euid": crypto.encrypt(user.key.id())}), 
                content_type='application/json')

            response.set_signed_cookie('session_id', session_id)

            return response

        else:
            return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Returns the contact form page.
"""
def contact(request):
    return render_to_response(
        'contact.html',
        {'recaptcha_public_key': settings.RECAPTCHA_PUBLIC_KEY},
        context_instance=RequestContext(request))


"""
Deletes a user's pantry
"""
def delete_pantry(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None

    if user_id:
        user = User.get_by_id(user_id)
        Pantry_Product.query(Pantry_Product.user_id == user_id).map(lambda key: key.delete(), keys_only=True)
        return redirect('/user/pantry')

    else:
        return redirect('/')


"""
Deletes a user's shopping list
"""
def delete_shopping_list(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None

    if user_id:
        user = User.get_by_id(user_id)
        Shopping_List_Product.query(Shopping_List_Product.user_id == user_id).map(lambda key: key.delete(), keys_only=True)
        return redirect('/user/shopping_list')

    else:
        return redirect('/')


"""
Serves the web home page
"""
def index(request):
    return render_to_response(
        'index.html', 
        {'categories': mark_safe(json.dumps(categories.categories))},
        context_instance=RequestContext(request))


"""
Returns the privacy policy page
"""
def privacy_policy(request):
    return render_to_response(
        'privacy_policy.html', {}, context_instance=RequestContext(request))


"""
Removes an additive from a user's additive list
"""
def remove_additive(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    additive = request.POST.get('additive', '')

    if user and additive in user.additives:
        user.additives.remove(additive)
        user.put()
        return HttpResponse('{"result": "success"}', content_type='application/json')

    else:
        return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Removes an allergen from a user's allergen list
"""
def remove_allergen(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    allergen = request.POST.get('allergen', '')

    if user and allergen in user.allergens:
        user.allergens.remove(allergen)
        user.put()
        return HttpResponse('{"result": "success"}', content_type='application/json')

    else:
        return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Removes a nutrient from a user's nutrient list
"""
def remove_nutrient(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    user = User.get_by_id(user_id) if user_id else None
    nutrient = request.POST.get('nutrient', '')

    if user and nutrient in user.nutrients:
        user.nutrients.remove(nutrient)
        user.put()
        return HttpResponse('{"result": "success"}', content_type='application/json')

    else:
        return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Removes a product from the Pantry_Product table
"""
def remove_from_pantry(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    barcode = request.POST.get('barcode', '')

    if User.get_by_id(user_id) and barcode:
        # Should get 1 key only
        Pantry_Product.query(
            Pantry_Product.user_id == user_id,
            Pantry_Product.barcode == barcode
        ).map(lambda key: key.delete(), keys_only=True)

        return HttpResponse('{"result": "success"}', content_type='application/json')

    else:
        return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Removes a product from the Shopping_List_Product table
"""
def remove_from_shopping_list(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    barcode = request.POST.get('barcode', '')

    if User.get_by_id(user_id) and barcode:
        # Should get 1 key only
        Shopping_List_Product.query(
            Shopping_List_Product.user_id == user_id,
            Shopping_List_Product.barcode == barcode
        ).map(lambda key: key.delete(), keys_only=True)

        return HttpResponse('{"result": "success"}', content_type='application/json')

    else:
        return HttpResponse('{"result": "failure"}', content_type='application/json')


"""
Returns do-not-crawl messages to web-crawler programs for
development and test environments
"""
def robots(request):
    return render_to_response(
        'robots.txt', {}, context_instance=RequestContext(request))


"""
Returns a list of search results.
"""
def search(request):
    search_term = request.GET.get('q', '')
    start = request.GET.get('start', '0')
    mobile = request.GET.get('mobile', '')
    user = User.get_by_id(crypto.decrypt(request.COOKIES['euid'])) if 'euid' in request.COOKIES else None
    session_id = request.get_signed_cookie('session_id', default=None)
    label_error = False

    if not session_id:
        session = label.create_session(user_id=user.key.id()) if user else label.create_session()
        if 'session_id' in session:
            session_id = session['session_id']
        else:
            label_error = True

    if user and session_id:
        # Set user's diet profile
        label.set_profile(session_id, user)
    
    products = [] # list of product info dictionaries
    pages = [] # list of (page_start, page_label) tuples
    total_found = 0

    # If start is not an integer, set start to 0
    try:
        start = int(start)
    except ValueError:
        start = 0

    if session_id:
        # Search products by keywords
        search_result = label.search_products(session_id, search_term, start=start)

        if 'numFound' in search_result and search_result['numFound'] > 0:
            products = search_result['productsArray']
            total_found = search_result['numFound']
            pages = get_pages(start, total_found)
        else:
            label_error = True

        # Get product score and product details
        for product in products:
            # Set none to empty-string for product_size
            if product['product_size'].strip() == 'none':
                product['product_size'] = ''

            # Get product details
            prod_details = label.label_array(session_id, product['upc'])

            if 'productsArray' in prod_details:
                product['details'] = prod_details['productsArray'][0]

                # Get nutrient percentage value
                for nutrient in product['details']['nutrients']:
                    if nutrient['nutrient_name'] in settings.DAILY_VALUES and nutrient['nutrient_uom'] in settings.UNIT_MULTIPLIER:
                        try:
                            nutrient['percentage_value'] = '{:.0%}'.format(float(nutrient['nutrient_value']) * settings.UNIT_MULTIPLIER[nutrient['nutrient_uom']] / settings.DAILY_VALUES[nutrient['nutrient_name']][1])
                        except ValueError:
                            nutrient['percentage_value'] = ''
            else:
                label_error = True
                break

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
            'label_error': label_error
        },
        context_instance=RequestContext(request))

    response.set_signed_cookie('session_id', session_id)

    return response


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

    else:
        return HttpResponse('recaptcha_failed', content_type='text/plain')


"""
Returns user signin page
"""
def signin(request):
    return render_to_response(
        'signin.html', {}, context_instance=RequestContext(request))


"""
Returns a sitemap XML
"""
def sitemap(request):
    return render_to_response(
        'sitemap.xml', {'categories': categories.categories}, 
        context_instance=RequestContext(request))


"""
Returns the terms of service page
"""
def terms_of_service(request):
    return render_to_response(
        'terms_of_service.html', {}, context_instance=RequestContext(request))


"""
Returns the user pantry page
"""
def user_pantry(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    
    if user_id:
        user = User.get_by_id(user_id)
        start = request.GET.get('start', '0')
        session_id = request.get_signed_cookie('session_id', default=None)
        label_error = False

        if not session_id:
            session = label.create_session(user_id=user_id)

            if 'session_id' in session:
                session_id = session['session_id']
            else:
                label_error = True

        if session_id:
            # Set diet profile
            label.set_profile(session_id, user)

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

                # Get nutrient percentage value
                for nutrient in products[length-1]['nutrients']:
                    if nutrient['nutrient_name'] in settings.DAILY_VALUES and nutrient['nutrient_uom'] in settings.UNIT_MULTIPLIER:
                        try:
                            nutrient['percentage_value'] = '{:.0%}'.format(float(nutrient['nutrient_value']) * settings.UNIT_MULTIPLIER[nutrient['nutrient_uom']] / settings.DAILY_VALUES[nutrient['nutrient_name']][1])
                        except ValueError:
                            nutrient['percentage_value'] = ''
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

        response =  render_to_response(
            'user_pantry.html',
            {
                'products': products,
                'products_len': len(products),
                'total': total,
                'start': start,
                'pages': pages,
                'label_error': label_error,
            },
            context_instance=RequestContext(request))

        response.set_signed_cookie('session_id', session_id)

        return response

    else:
        return redirect('/signin')


"""
Returns user profile page
"""
def user_profile(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None

    if user_id:
        user = User.get_by_id(user_id)

        return render_to_response(
            'user_profile.html', {'user': user}, context_instance=RequestContext(request))

    else:
        return redirect('/signin')    


"""
Returns the user shopping list
"""
def user_shopping_list(request):
    user_id = crypto.decrypt(request.COOKIES['euid']) if 'euid' in request.COOKIES else None
    
    if user_id:
        user = User.get_by_id(user_id)
        start = request.GET.get('start', '0')
        session_id = request.get_signed_cookie('session_id', default=None)
        label_error = False

        if not session_id:
            session = label.create_session(user_id=user_id)

            if 'session_id' in session:
                session_id = session['session_id']
            else:
                label_error = True

        if session_id:
            # Set diet profile
            label.set_profile(session_id, user)

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

                # Get nutrient percentage value
                for nutrient in products[length-1]['nutrients']:
                    if nutrient['nutrient_name'] in settings.DAILY_VALUES and nutrient['nutrient_uom'] in settings.UNIT_MULTIPLIER:
                        try:
                            nutrient['percentage_value'] = '{:.0%}'.format(float(nutrient['nutrient_value']) * settings.UNIT_MULTIPLIER[nutrient['nutrient_uom']] / settings.DAILY_VALUES[nutrient['nutrient_name']][1])
                        except ValueError:
                            nutrient['percentage_value'] = ''
            else:
                label_error=True

            # Check if product is on user shopping list
            if Pantry_Product.query(
                    Pantry_Product.user_id == user_id,
                    Pantry_Product.barcode == entity.barcode
            ).get(keys_only=True):
                products[length-1]['in_pantry'] = 'true'

            # Get time between now when product was added
            products[length-1]['t_delta'] = utils.get_time_delta_str(now - entity.add_datetime)

        pages = get_pages(start, total)

        response =  render_to_response(
            'user_shopping_list.html',
            {
                'products': products,
                'products_len': len(products),
                'total': total,
                'start': start,
                'pages': pages,
                'label_error': label_error,
            },
            context_instance=RequestContext(request))

        response.set_signed_cookie('session_id', session_id)

        return response

    else:
        return redirect('/signin')


"""
Returns the 404 error - not found - page
"""
def err404(request):
    return render_to_response('404.html', {})


"""
Returns the 500 error - internal server error - page
"""
def err500(request):
    return render_to_response('500.html', {})


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
