from django.utils import http
from classifood import settings
from classifood import crypto

"""
    # Get similar items from Amazon Product Advertising API
    query_str = "AWSAccessKeyId=%s&AssociateTag=%s&Availability=Available&Condition=All&Keywords=%s&Operation=ItemSearch&ResponseGroup=Images%%2CItemAttributes%%2COfferSummary&SearchIndex=Grocery&Service=AWSECommerceService&Timestamp=%s&Version=2013-08-01" % (settings.AWS_ACCESS_KEY, settings.AMAZON_ASSOCIATE_TAG, re.sub('\+', '%20', http.urlencode({'s': food.name_search})[2:]), datetime.utcnow().strftime('%Y-%m-%dT%H%%3A%M%%3A%SZ'))

    amazon_url = amazon_products.get_signed_url('POST', settings.AWS_DOMAIN, settings.AWS_PATH, query_str)

    try:
        amazon_response = urlfetch.fetch(amazon_url, method='POST', deadline=2, follow_redirects=False)

    # If any error occurs, the view page will not show any amazon items.
    except urlfetch.InvalidURLError():
        pass
    except urlfetch.DeadlineExceededError():
        pass
    except urlfetch.DownloadError():
        pass
    except urlfetch.ResponseTooLargeError():
        pass
    
    amazon_items = []
    more_items_url = ''

    if amazon_response.status_code == 200:
        # amazon_response.content is an xml document
        # find('ELEMENT') returns a tree where ELEMENT is the root
        tag_prefix = settings.TREE_TAG_PREFIX
        items_tree = ElementTree.fromstring(amazon_response.content).find(tag_prefix+'Items')

        # If request is valid...
        if items_tree.find(tag_prefix+'Request').find(tag_prefix+'IsValid').text.lower() == 'true':
            # Find all Items
            item_elements = items_tree.findall(tag_prefix+'Item')

            # Show at most 5 items
            if len(item_elements) > 5:
                item_elements = item_elements[:5]

            # Get name, price, small image url, and page url
            for i in range(0, len(item_elements)):
                amazon_items.append({})
                amazon_items[i]['name'] = item_elements[i].find(tag_prefix+'ItemAttributes').find(tag_prefix+'Title').text
                amazon_items[i]['page_url'] = item_elements[i].find(tag_prefix+'DetailPageURL').text

                amazon_items[i]['img_url_sm'] = '/img/no_image_53x75.png'
                amazon_items[i]['price'] = ''

                # If item has small image
                if item_elements[i].find(tag_prefix+'SmallImage'):
                    amazon_items[i]['img_url_sm'] = item_elements[i].find(tag_prefix+'SmallImage').find(tag_prefix+'URL').text

                # If item has price...
                if int(item_elements[i].find(tag_prefix+'OfferSummary').find(tag_prefix+'TotalNew').text) > 0:
                    amazon_items[i]['price'] = item_elements[i].find(tag_prefix+'OfferSummary').find(tag_prefix+'LowestNewPrice').find(tag_prefix+'FormattedPrice').text
"""

def get_signed_url(http_method, domain, path, query_str):
    str_to_sign = http_method + "\n" + domain + "\n" + path + "\n" + query_str

    # Signature is an HMAC SHA256 hash made with the AWS SECRET ACCESS KEY.
    # It must also be encode in Base 64 and then url-escaped.
    signature = crypto.b64_encode(crypto.get_hmac_sha256_hash(str_to_sign, settings.AWS_SECRET_ACCESS_KEY))
    signature = http.urlencode({'s':signature})[2:]

    return 'https://%s%s?%s' % (settings.AWS_DOMAIN, 
                                settings.AWS_PATH, 
                                query_str+'&Signature='+signature)
    
