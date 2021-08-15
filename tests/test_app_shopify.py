import json
from copy import deepcopy
from unittest.mock import patch

from app import app
from models.profile import Profile

from tests import const
from tests.base_case import BaseCase


class ShopifyTest(BaseCase):

    @patch('app_shopify.views.customer_service.create_customer')
    def test_to_complete_onboarding(self, mock_tx_service):
        with app.app_context():
            profile = Profile.query.filter_by(
                shop_unique_id=const.SHOP_SHOPIFY).first()

        name_of_user = "kg"
        contact_email = "new_email@demo.com"

        payload = {
            "nameOfUser": name_of_user,
            "contactEmail": contact_email,
            "shop": profile.shop_unique_id,
        }
        mocked_customer_id = "b6c9a69e-1b6e-4a5e-9787-b9574e5f3aaa"
        mock_tx_service.return_value = mocked_customer_id
        response_for_unauthorized = self.app.post('/shopify/profile',
                                                  headers={
                                                      "Content-Type": "application/json"
                                                  }, data=json.dumps(payload))
        self.assertEqual(401, response_for_unauthorized.status_code)

        response = self.app.post('/shopify/profile',
                                 headers={
                                     "Content-Type": "application/json",
                                     "Authorization": "Bearer {}".format(profile.auth_token)
                                 }, data=json.dumps(payload))
        self.assertEqual(200, response.status_code)
        with app.app_context():
            profile_after = Profile.query.filter_by(
                shop_unique_id=const.SHOP_SHOPIFY).first()
        self.assertEqual(name_of_user, profile_after.name,
                         msg="Failed to update name")
        self.assertEqual(contact_email, profile_after.contact_email,
                         msg="Failed to update contact email")

    @patch('app_shopify.views.verify_webhook')
    @patch('app_shopify.webhooks.tx_service')
    def test_order_paid_webook_no_compensation(self, mock_tx, mock_hmac):
        mock_tx.create_tx.return_value = "core-transaction-id"
        order = get_order_paid_webhook_data()
        del order['line_items'][0]

        order_id = str(order['id'])
        response = self.app.post('/shopify/webhook', headers={
            "Content-Type": "application/json",
            "X_SHOPIFY_TOPIC": "orders/paid",
            "X-SHOPIFY-HMAC-SHA256": "bla-bla-bla",
            "X-SHOPIFY_SHOP_DOMAIN": const.SHOP_SHOPIFY
        }, data=json.dumps(order))
        self.assertEqual(200, response.status_code)

    @patch('app_shopify.views.verify_webhook')
    @patch('app_shopify.webhooks.tx_service')
    def test_order_paid_webook_failed_charge(self, mock_tx, mock_hmac):
        mock_tx.create_tx.return_value = "core-transaction-id"
        mock_tx.create_usage_charge.side_effect = Exception("failed!")
        order = get_order_paid_webhook_data()

        order_id = str(order['id'])
        response = self.app.post('/shopify/webhook', headers={
            "Content-Type": "application/json",
            "X_SHOPIFY_TOPIC": "orders/paid",
            "X-SHOPIFY-HMAC-SHA256": "bla-bla-bla",
            "X-SHOPIFY_SHOP_DOMAIN": const.SHOP_SHOPIFY
        }, data=json.dumps(order))
        self.assertEqual(200, response.status_code)

        mock_tx.fail_order.assert_called_once_with(const.SHOP_SHOPIFY, order_id)

    @patch('app_shopify.views.verify_webhook')
    def test_uninstall_webhook(self, mock_webhook_hmac):
        response = self.app.post('/shopify/webhook', headers={
            "Content-Type": "application/json",
            "X_SHOPIFY_TOPIC": "app/uninstalled",
            "X-SHOPIFY-HMAC-SHA256": "bla-bla-bla",
            "X-SHOPIFY_SHOP_DOMAIN": const.SHOP_SHOPIFY
        }, data=json.dumps({}))
        self.assertEqual(200, response.status_code)
        with app.app_context():
            profile = Profile.query.filter_by(
                shop_unique_id=const.SHOP_SHOPIFY).first()
        self.assertFalse(profile.status,
                         msg="Profile wasnt uninstalled properly")


def get_order_paid_webhook_data():
    return deepcopy({
        "id": 2704107995290,
        "email": "this-should-be-removed@demo.com",
        "closed_at": "None",
        "created_at": "2020-09-16T02:32:46-04:00",
        "updated_at": "2020-09-16T02:32:47-04:00",
        "number": 8,
        "note": "None",
        "token": "82c7ea520c11c086a5659e6b03aa226a",
        "gateway": "bogus",
        "test": True,
        "total_price": "32.46",
        "subtotal_price": "15.20",
        "total_weight": 10000,
        "total_tax": "0.00",
        "taxes_included": True,
        "currency": "EUR",
        "financial_status": "paid",
        "confirmed": True,
        "total_discounts": "0.00",
        "total_line_items_price": "15.20",
        "cart_token": "a7927b2d5ee021b2d4f54225ab09c901",
        "buyer_accepts_marketing": False,
        "name": "#1008",
        "referring_site": "",
        "landing_site": "/",
        "cancelled_at": "None",
        "cancel_reason": "None",
        "total_price_usd": "38.52",
        "checkout_token": "68c914958c57087ccc66a9c89b41f439",
        "reference": "None",
        "user_id": "None",
        "location_id": "None",
        "source_identifier": "None",
        "source_url": "None",
        "processed_at": "2020-09-16T02:32:45-04:00",
        "device_id": "None",
        "phone": "None",
        "customer_locale": "en",
        "app_id": 580111,
        "browser_ip": "this.should.also.be.removed",
        "landing_site_ref": "None",
        "order_number": 1008,
        "discount_applications": [

        ],
        "discount_codes": [

        ],
        "note_attributes": [

        ],
        "payment_gateway_names": [
            "bogus"
        ],
        "processing_method": "direct",
        "checkout_id": 14907243888794,
        "source_name": "web",
        "fulfillment_status": "None",
        "tax_lines": [
        ],
        "tags": "",
        "contact_email": "this-should-be-removed@demo.com",
        "order_status_url": "https://some-random-store-about-nachos.myshopify.com/44984500378/orders/82c7ea520c11c086a5659e6b03aa226a/authenticate?key=99bc4875c9e777b68f971f90fe549f9b",
        "presentment_currency": "SEK",
        "total_line_items_price_set": {
            "shop_money": {
                "amount": "15.20",
                "currency_code": "EUR"
            },
            "presentment_money": {
                "amount": "158.37",
                "currency_code": "SEK"
            }
        },
        "total_discounts_set": {
            "shop_money": {
                "amount": "0.00",
                "currency_code": "EUR"
            },
            "presentment_money": {
                "amount": "0.00",
                "currency_code": "SEK"
            }
        },
        "total_shipping_price_set": {
            "shop_money": {
                "amount": "17.26",
                "currency_code": "EUR"
            },
            "presentment_money": {
                "amount": "179.72",
                "currency_code": "SEK"
            }
        },
        "subtotal_price_set": {
            "shop_money": {
                "amount": "15.20",
                "currency_code": "EUR"
            },
            "presentment_money": {
                "amount": "158.37",
                "currency_code": "SEK"
            }
        },
        "total_price_set": {
            "shop_money": {
                "amount": "32.46",
                "currency_code": "EUR"
            },
            "presentment_money": {
                "amount": "338.09",
                "currency_code": "SEK"
            }
        },
        "total_tax_set": {
            "shop_money": {
                "amount": "0.00",
                "currency_code": "EUR"
            },
            "presentment_money": {
                "amount": "0.00",
                "currency_code": "SEK"
            }
        },
        "line_items": [
            {
                "id": 5886999888026,
                "variant_id": 36237290471578,
                "title": "Tigers & Tacos",
                "quantity": 1,
                "sku": "",
                "variant_title": "e54cfba7-ce6f-4de1-a94b-7facca8a96ab",
                "vendor": "Tigers & Tacos",
                "fulfillment_service": "manual",
                "product_id": 5718277390490,
                "requires_shipping": True,
                "taxable": True,
                "gift_card": False,
                "name": "Nacho - e54cfba7-ce6f-4de1-a94b-7facca8a96ab",
                "variant_inventory_management": "shopify",
                "properties": [

                ],
                "product_exists": True,
                "fulfillable_quantity": 1,
                "grams": 0,
                "price": "5.05",
                "total_discount": "0.00",
                "fulfillment_status": "None",
                "price_set": {
                    "shop_money": {
                        "amount": "5.05",
                        "currency_code": "EUR"
                    },
                    "presentment_money": {
                        "amount": "52.65",
                        "currency_code": "SEK"
                    }
                },
                "total_discount_set": {
                    "shop_money": {
                        "amount": "0.00",
                        "currency_code": "EUR"
                    },
                    "presentment_money": {
                        "amount": "0.00",
                        "currency_code": "SEK"
                    }
                },
                "discount_allocations": [

                ],
                "duties": [

                ],
                "admin_graphql_api_id": "gid://shopify/LineItem/5886999888026",
                "tax_lines": [

                ],
                "origin_location": {
                    "id": 2300131606682,
                    "country_code": "SE",
                    "province_code": "",
                    "name": "some-random-store-about-nachos",
                    "address1": "Vasagatan 47",
                    "address2": "",
                    "city": "Helsinki",
                    "zip": "00130"
                }
            },
            {
                "id": 5886999953562,
                "variant_id": 35562416668826,
                "title": "Widgets",
                "quantity": 1,
                "sku": "100",
                "variant_title": "",
                "vendor": "some-random-store-about-nachos",
                "fulfillment_service": "manual",
                "product_id": 5578484154522,
                "requires_shipping": True,
                "taxable": True,
                "gift_card": False,
                "name": "Widgets",
                "variant_inventory_management": "None",
                "properties": [

                ],
                "product_exists": True,
                "fulfillable_quantity": 1,
                "grams": 10000,
                "price": "10.15",
                "total_discount": "0.00",
                "fulfillment_status": "None",
                "price_set": {
                    "shop_money": {
                        "amount": "10.15",
                        "currency_code": "EUR"
                    },
                    "presentment_money": {
                        "amount": "105.72",
                        "currency_code": "SEK"
                    }
                },
                "total_discount_set": {
                    "shop_money": {
                        "amount": "0.00",
                        "currency_code": "EUR"
                    },
                    "presentment_money": {
                        "amount": "0.00",
                        "currency_code": "SEK"
                    }
                },
                "discount_allocations": [

                ],
                "duties": [

                ],
                "admin_graphql_api_id": "gid://shopify/LineItem/5886999953562",
                "tax_lines": [

                ],
                "origin_location": {
                    "id": 2300131606682,
                    "country_code": "SE",
                    "province_code": "",
                    "name": "tigers & tacos",
                    "address1": "Vasagatan 47",
                    "address2": "",
                    "city": "Stockholm",
                    "zip": "00130"
                }
            }
        ],
        "fulfillments": [

        ],
        "refunds": [

        ],
        "total_tip_received": "0.0",
        "original_total_duties_set": "None",
        "current_total_duties_set": "None",
        "admin_graphql_api_id": "gid://shopify/Order/2704107995290",
        "shipping_lines": [
            {
                "id": 2246394249370,
                "title": "Standard",
                "price": "17.26",
                "code": "Standard",
                "source": "shopify",
                "phone": "None",
                "requested_fulfillment_service_id": "None",
                "delivery_category": "None",
                "carrier_identifier": "None",
                "discounted_price": "17.26",
                "price_set": {
                    "shop_money": {
                        "amount": "17.26",
                        "currency_code": "EUR"
                    },
                    "presentment_money": {
                        "amount": "179.72",
                        "currency_code": "SEK"
                    }
                },
                "discounted_price_set": {
                    "shop_money": {
                        "amount": "17.26",
                        "currency_code": "EUR"
                    },
                    "presentment_money": {
                        "amount": "179.72",
                        "currency_code": "SEK"
                    }
                },
                "discount_allocations": [

                ],
                "tax_lines": [

                ]
            }
        ],
        "billing_address": {
            "first_name": "Tiger",
            "address1": "Engelbrektsgatan 7",
            "phone": "None",
            "city": "Stockholm",
            "zip": "10500",
            "province": "None",
            "country": "Sweden",
            "last_name": "b",
            "address2": "",
            "company": "None",
            "latitude": "None",
            "longitude": "None",
            "name": "Tiger b",
            "country_code": "SE",
            "province_code": "None"
        },
        "shipping_address": {
            "first_name": "Tiger",
            "address1": "Engelbrektsgatan 7",
            "phone": "None",
            "city": "Stockholm",
            "zip": "10500",
            "province": "None",
            "country": "Sweden",
            "last_name": "b",
            "address2": "",


            "company": "None",
            "latitude": "None",
            "longitude": "None",
            "name": "Tiger b",
            "country_code": "SE",
            "province_code": "None"
        },
        "client_details": {
            "browser_ip": "this.should.also.be.removed",
            "accept_language": "en-GB,en-US;q=0.9,en;q=0.8",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
            "session_hash": "79191efdcc6b235e4cba38ff21ce9d8f",
            "browser_width": 1266,
            "browser_height": 483
        },
        "payment_details": {
            "credit_card_bin": "1",
            "avs_result_code": "None",
            "cvv_result_code": "None",
            "credit_card_number": "•••• •••• •••• 1",
            "credit_card_company": "Bogus"
        },
        "customer": {
            "id": 3856580083866,
            "email": "this-should-be-removed@demo.com",
            "accepts_marketing": False,
            "created_at": "2020-08-13T16:07:09-04:00",
            "updated_at": "2020-09-16T02:32:46-04:00",
            "first_name": "Tiger",
            "last_name": "b",
            "orders_count": 0,
            "state": "disabled",
            "total_spent": "0.00",
            "last_order_id": "None",
            "note": "None",
            "verified_email": True,
            "multipass_identifier": "None",
            "tax_exempt": False,
            "phone": "None",
            "tags": "",
            "last_order_name": "None",
            "currency": "EUR",
            "accepts_marketing_updated_at": "2020-08-13T16:07:09-04:00",
            "marketing_opt_in_level": "None",
            "admin_graphql_api_id": "gid://shopify/Customer/3856580083866",
            "default_address": {
                "id": 4582489161882,
                "customer_id": 3856580083866,
                "first_name": "Tiger",
                "last_name": "b",
                "company": "None",
                "address1": "Engelbrektsgatan 7",
                "address2": "",
                "city": "Stockholm",
                "province": "None",
                "country": "Sweden",
                "zip": "10500",
                "phone": "None",
                "name": "Tiger b",
                "province_code": "None",
                "country_code": "SE",
                "country_name": "Sweden",
                "default": True
            }
        }
    })
