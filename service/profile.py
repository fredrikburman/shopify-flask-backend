import logging
from common.extensions import db
from models.profile import Profile

log = logging.getLogger('werkzeug')


def create(shop_unique_id,
           contact_email=None,
           shop_url=None,
           shopify_access_token=None,
           name=None,
           accepted_terms_and_conditions=None,
           customer_id=None,
           platform="SHOPIFY"):
    """Create a profile"""
    profile = Profile.query.filter_by(shop_unique_id=shop_unique_id).first()
    if not profile:
        profile = Profile(shop_unique_id=shop_unique_id,
                          contact_email=contact_email,
                          name=name,
                          shop_url=shop_url,
                          shopify_access_token=shopify_access_token,
                          customer_id=customer_id)
        db.session.add(profile)
    else:
        profile.status = 1
        profile.shopify_access_token = shopify_access_token
        profile.name = name
        profile.contact_email = contact_email
        profile.shop_url = shop_url
        profile.timestamp_uninstall = None
        profile.platform = platform
    if accepted_terms_and_conditions:
        profile.accepted_tos = True
    try:
        db.session.commit()
    except Exception as e:  # NOQA
        log.exception(f'Failed to persist profile:')
    return profile


def update(shop_unique_id, data):
    profile = Profile.query.filter_by(shop_unique_id=shop_unique_id).update(data)
    db.session.commit()
    return profile


def get_tokens(shop_unique_id):
    profile = Profile.query.filter_by(shop_unique_id=shop_unique_id).first()
    if profile:
        return {"shopify_access_token": profile.shopify_access_token, "auth_token": profile.auth_token}
    return {}


def get(shop_unique_id):
    profile = Profile.query.filter_by(shop_unique_id=shop_unique_id).first()
    if profile:
        return profile.__dict__
    else:
        return {'shopify_access_token': None,
                'status': None,
                'shop_unique_id': None}

