from flask import jsonify
import logging
from service import profile as profile_service
import random

import shopify
from flask import (
    Blueprint, render_template, current_app, request, redirect,
    url_for, make_response, abort)

from common import const, parsers
from common.auth import token_auth
from app_shopify.common import hmac_is_valid, \
    add_webhooks, verify_webhook
from app_shopify import webhooks

log = logging.getLogger('werkzeug')

shopify_bp = Blueprint('plugin_shopify', __name__,
                       url_prefix='/shopify',
                       static_folder='templates/static',
                       template_folder='templates')


@shopify_bp.route('/profile', methods=["GET", "POST"])
@token_auth.login_required
def profile_update():
    """
    This is how you can take a request from the Shopify admin side of things, provide the auth_token,
    make sure that the user is authenticated and then perform stuff with the data provided.
    For example update a profile.
    """
    if request.is_json:
        data = request.get_json()
        if 'get' in data.keys():
            profile = profile_service.get(data['shop'])
            return jsonify(_setup_profile_data(profile))
        try:
            profile_data = _parse_profile_data(data)
            shop = profile_data.pop('shop')
        except KeyError as e:
            log.error(f'Issue with parsing profile data {e} ')
            return make_response(jsonify({"message": "Could not process provided data"}), 400)
        try:
            profile = profile_service.get(shop)
            if "contact_email" not in profile.keys():
                log.info(f'Store {shop} not properly installed.')
                return install()
            profile_service.update(shop,
                                   profile_data)

        except Exception as e:  # NOQA
            log.exception(f'failed to persist profile: {e}')
            return make_response(jsonify({"message": "Failed to persist profile"}), 400)

        profile = profile_service.get(shop)
        return make_response(jsonify({"message": "OK", "data": _setup_profile_data(profile)}))
    return jsonify({"message": "Please try again..."})


@shopify_bp.route('/install')
def install():
    """
    Redirect user to the Shopify permission authorization page where they can give their access for our app.
    """
    shop_url = request.args.get("shop")
    if not shop_url:
        return render_template("400.html", message="No shop in query params"), 400
    shopify.Session.setup(
        api_key=current_app.config['SHOPIFY_API_KEY'],
        secret=current_app.config['SHOPIFY_SHARED_SECRET'])
    session = shopify.Session(shop_url, current_app.config['SHOPIFY_API_VERSION'])

    permission_url = session.create_permission_url(
        const.SHOPIFY_OAUTH_SCOPES, url_for("plugin_shopify.finalize",
                       _external=True,
                       _scheme='https'))
    return render_template('install.html',
                           permission_url=permission_url)


@shopify_bp.route('/finalize')
def finalize():
    """
    Generate shop token, store the shop information and show app dashboard page
    """
    shop_url = request.args.get("shop")
    shopify.Session.setup(
        api_key=current_app.config['SHOPIFY_API_KEY'],
        secret=current_app.config['SHOPIFY_SHARED_SECRET'])
    shopify_session = shopify.Session(shop_url, current_app.config['SHOPIFY_API_VERSION'])

    token = shopify_session.request_token(request.args)
    try:
        session = shopify.Session(shop_url,
                                  current_app.config['SHOPIFY_API_VERSION'],
                                  token)
        shopify.ShopifyResource.activate_session(session)
        shop = shopify.Shop.current()
        profile_service.create(shop_unique_id=shop_url,
                               shopify_access_token=token,
                               contact_email=shop.email,
                               name=shop.shop_owner)
    except Exception as e:  # NOQA
        log.error('Something went wrong when trying to crete the profile')
        return render_template("400.html", message="Failed to save profile"), 400
    profile = profile_service.get(shop_url)
    if not profile[const.PROFILE_MODEL_FIELD_ONBOARDING_SHOPIFY_ADDED_WEBHOOK_UNINSTALL]:
        add_webhooks(shop_url, token)
        profile_service.update(shop_url, {const.PROFILE_MODEL_FIELD_ONBOARDING_SHOPIFY_ADDED_WEBHOOK_UNINSTALL: True})
    return_url = "{}?{}".format(url_for('plugin_shopify.index'), request.query_string.decode('utf-8'))
    return redirect(return_url)


def _merchant_is_installed(profile):
    if not profile['shopify_access_token'] or not profile['status']:
        return False
    return True


@shopify_bp.route('/')
def index():
    """
    Render the index page of our application.
    """
    query_dict = request.args.to_dict()
    if not hmac_is_valid(query_dict):
        return render_template("400.html", message="Could not verify request"), 400
    tokens = profile_service.get_tokens(query_dict.get('shop'))
    profile = profile_service.get(query_dict.get('shop'))
    if not _merchant_is_installed(profile):
        return install()
    return render_template('index.html',
                           shopify_api_key=current_app.config['SHOPIFY_API_KEY'],
                           shop=query_dict.get('shop'),
                           backend=current_app.config["HOSTNAME"],
                           auth_token=tokens.get('auth_token'))


@shopify_bp.route('/webhook', methods=['POST'])
def parse_webhook():
    """
    Receive and process Shopify webhooks.
    This is a simple implementation that keeps the webhook in the request / response cycle.
    If we fail to handle the webhook then we return a http 500 to Shopify which means that they will resend the webhook.

    A more appropriate way to implement this would be to accept the webhook from Shopify and then process it in a
    queue / worker pattern or similar.
    """
    data = request.get_data()
    verified = verify_webhook(data, request.headers.get('X-SHOPIFY_HMAC_SHA256'))
    if not verified and current_app.config["WEBHOOK_TEST_MODE"] is True:
        log.warning('got webhook that failed hmac verification')
        abort(401)
    event = request.headers.get('X_SHOPIFY_TOPIC')
    shop_url = request.headers.get('X-SHOPIFY_SHOP_DOMAIN')
    try:
        webhooks.handler[event](data, shop_url)
    except parsers.ParserException:
        log.exception("Failed to parse order for shop: {}, {}".format(shop_url, data))
        abort(500)
    except Exception as e:  # NOQA
        log.exception("unhandled exception when parsing webhook for: {}, {}".format(shop_url, data))
        abort(500)
    return jsonify({"message": "Nom nom nom"})


@shopify_bp.route('/demo-post-request', methods=['POST'])
@token_auth.login_required
def demo_post_request():
    tacos = ["carne Asada", "shrimp taco", "fish Taco", "barbacoa", "tacos de Birria", "tacos Al Pastor", "carnitas", "nopales"]
    if request.is_json:
        data = request.get_json()
        log.info(f'post received: {data}')
    msg = f"I think you should try a {random.choice(tacos)}"
    return jsonify({
        "message": msg,
    })


def _parse_profile_data(data):
    return_data = {
        const.PROFILE_MODEL_FIELD_NAME: data[const.PROFILE_NAME],
        const.PROFILE_MODEL_FIELD_CONTACT_EMAIL: data[const.PROFILE_EMAIL],
        const.PROFILE_SHOP: data["shop"]
    }
    return return_data


def _setup_profile_data(profile):
    data = {
        const.PROFILE_NAME: profile[const.PROFILE_MODEL_FIELD_NAME],
        const.PROFILE_EMAIL: profile[const.PROFILE_MODEL_FIELD_CONTACT_EMAIL],
    }
    return data
