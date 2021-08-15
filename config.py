import os
import multiprocessing

PORT = int(os.getenv("PORT", 5000))
DEBUG_MODE = int(os.getenv("DEBUG_MODE", 0))

# Gunicorn config
bind = ":" + str(PORT)
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2 * multiprocessing.cpu_count()


class DefaultConfig(object):

    PROJECT = "Tigers & Tacos for Shopify"
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "super-random-key")
    PREFERRED_URL_SCHEME = "https"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
    SHOPIFY_SHARED_SECRET = os.getenv("SHOPIFY_SHARED_SECRET")
    SHOPIFY_API_VERSION = '2020-07'
    HOSTNAME = os.getenv("HOSTNAME_FOR_SHOPIFY", None)
    WEBHOOK_TEST_MODE = os.getenv("WEBHOOK_TEST_MODE", False).lower() in ('true', '1', 't')
