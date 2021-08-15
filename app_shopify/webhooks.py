import datetime
from flask import current_app
import json
import logging
from common import const, parsers
from service import profile as profile_service

log = logging.getLogger('werkzeug')


def uninstall(data, shop_unique_url):
    profile_service.update(shop_unique_url, {'status': 0,
                                             'timestamp_uninstall': datetime.datetime.utcnow(),
                                             const.PROFILE_MODEL_FIELD_SHOPIFY_RECURRING_SUBSCRIPTION_ID: None,
                                             const.PROFILE_MODEL_FIELD_ONBOARDING_SHOPIFY_ADDED_WEBHOOK_UNINSTALL: False
                                             })


def order_paid(data, shop_url):
    log.info('got order paid webhook')
    try:
        parsed = parsers.shopify_order(json.loads(data), shop_url)
    except KeyError as e:
        raise parsers.ParserException
    log.info(f'this is the parsed order: {parsed}')


def order_fulfilled(data, shop_url):
    log.info(f'order is fulfilled')


def gdpr_data_request(data, shop_url):
    log.info(f'GDPR data_access_request:  {data}')


def gdpr_customer_data_erasure(data, shop_url):
    log.info(f'GDPR customer_data_erasure_request:  {data}')


def gdpr_shop_data_erasure(data, shop_url):
    log.info(f'GDPR shop_data_erasure_request:  {data}')


# Extend this to enable handling of other webhook topics that you subscribe to
handler = {
    'app/uninstalled': uninstall,
    'orders/paid': order_paid,
    'orders/fulfilled': order_fulfilled,
    'customers/redact': gdpr_customer_data_erasure,
    'shop/redact': gdpr_shop_data_erasure,
    'customers/data_request': gdpr_data_request
}

