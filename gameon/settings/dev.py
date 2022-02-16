from .base import *

DEBUG = True

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ["52.91.98.88", "admin.gameon.com.ng"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db2.sqlite3",
    }
}
