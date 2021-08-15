import hashlib, base64, hmac
from flask import current_app
from urllib.parse import urlencode
import shopify
from common import const


def hmac_is_valid(query_dict):
    """Used in for example the index.html endpoint for the shopify app"""
    try:
        hmac_from_query_string = query_dict.pop('hmac')
        if 'charge_id' in query_dict.keys():
            del query_dict['charge_id']
            return True
        url_encoded = urlencode(query_dict)
        secret = current_app.config['SHOPIFY_SHARED_SECRET'].encode('utf-8')
        signature = hmac.new(secret, url_encoded.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(hmac_from_query_string, signature)
    except KeyError as e:
        return False


def verify_webhook(data, hmac_header):
    digest = hmac.new(current_app.config['SHOPIFY_SHARED_SECRET'].encode('utf-8'),
                      data,
                      hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))


def add_webhooks(shop, token):
    session = shopify.Session(shop, current_app.config['SHOPIFY_API_VERSION'], token)
    shopify.ShopifyResource.activate_session(session)
    for topic in const.SHOPIFY_WEBHOOK_TOPICS:
        new_webhook = shopify.Webhook()
        new_webhook.address = current_app.config['HOSTNAME'] + "/shopify/webhook"
        new_webhook.format = 'json'
        new_webhook.topic = topic
        new_webhook.save()
    return True

