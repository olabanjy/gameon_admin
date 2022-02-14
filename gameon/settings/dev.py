from .base import *

DEBUG = True

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = []


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db2.sqlite3",
    }
}
