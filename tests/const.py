import os
SHOP_SHOPIFY = "some-random-shopify-store.myshopify.com"
SHOP_SHOPIFY_BLACKLISTED = "blacklisted.myshopify.com"
SHOP_SHOPIFY_NOT_INSTALLED = "not-installed-shopify-store.myshopify.com"

CUSTOMER_ID_SHOPIFY = "d0e60383-1746-4089-bc86-4d238eb2012d"
CUSTOMER_ID_SHOPIFY_BLACKLISTED = "d0e60383-1746-4089-bc86-4d238eb2012a"
CUSTOMER_ID_WOOCOMMERCE = "a6e1acfc-53ac-4922-8411-15d594d4ded8"

DB_URI = os.getenv("DATABASE_URL", "postgresql+psycopg2://test_user:password@localhost/testdb")
