import unittest
from app import app
from common.extensions import db
from models.profile import Profile
from tests import const


class BaseCase(unittest.TestCase):

    def setUp(self):
        self.db = db
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = const.DB_URI
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
        self.setup_shops()

    def tearDown(self):
        # Delete Database collections after the test is complete
        with app.app_context():
            self.db.drop_all()

    def setup_shops(self):
        profile_shopify_not_installed = Profile(
            shop_unique_id=const.SHOP_SHOPIFY_NOT_INSTALLED,
            contact_email='not-installed@shopify.com',
            name="Shopify Not installed",
            shop_url="https://not-installed-store.myshopify.com",
        )
        profile_shopify = Profile(
            shop_unique_id=const.SHOP_SHOPIFY,
            contact_email='shopify@hello.com',
            name="Shopify Name",
            shop_url="https://super-store.myshopify.com",
            customer_id=const.CUSTOMER_ID_SHOPIFY,
        )
        profile_shopify_blacklisted = Profile(
            shop_unique_id=const.SHOP_SHOPIFY_BLACKLISTED,
            contact_email='shopify2@hello.com',
            name="Shopify 2 Name",
            shop_url="https://blacklisted.myshopify.com",
            customer_id=const.CUSTOMER_ID_SHOPIFY_BLACKLISTED,
        )

        with app.app_context():
            db.session.add(profile_shopify_not_installed)
            db.session.add(profile_shopify)
            db.session.add(profile_shopify_blacklisted)
            db.session.commit()
