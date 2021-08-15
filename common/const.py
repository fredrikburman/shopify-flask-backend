# This is a good place to put all your constants
PROFILE_NAME = "nameOfUser"
PROFILE_EMAIL = "contactEmail"
PROFILE_SHOP = "shop"

PROFILE_MODEL_FIELD_AUTH_TOKEN = "auth_token"
PROFILE_MODEL_FIELD_ACCESS_TOKEN = "access_token"
PROFILE_MODEL_FIELD_ACCEPTED_TOC = "accepted_tos"
PROFILE_MODEL_FIELD_NAME = "name"
PROFILE_MODEL_FIELD_CONTACT_EMAIL = "contact_email"
PROFILE_MODEL_FIELD_SHOPIFY_RECURRING_SUBSCRIPTION_ID = "shopify_recurring_subscription_id"
PROFILE_MODEL_FIELD_ONBOARDING_SHOPIFY_ADDED_WEBHOOK_UNINSTALL = "onboarding_shopify_added_webhooks"

SHOPIFY_WEBHOOK_TOPICS = ["app/uninstalled", "orders/paid"]
SHOPIFY_OAUTH_SCOPES = [
        "write_products",
        "read_products",
        "read_orders",
        "read_script_tags",
        "write_script_tags"]

# Blacklist
BLACKLIST_CACHE_AGE = 3600

# The order data
ORDER_SHOP_UNIQUE_ID = "shop_id"
ORDER_ID = "order_id"
