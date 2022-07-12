from .base import *

DEBUG = True

# ALLOWED_HOSTS = ["*"]
ALLOWED_HOSTS = ["159.89.228.221", "admin.gameon.com.ng"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db2.sqlite3",
    }
}


# DATABASES = {
#     "default": {
#         # 'ENGINE': 'django.db.backends.postgresql',
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": "gameon_admin",
#         "USER": "olabanji",
#         "PASSWORD": "olabanji",
#         "HOST": "localhost",
#         "PORT": "5432",
#     }
# }

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.zoho.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True


DEFAULT_FROM_EMAIL = config("EMAIL_HOST_USER")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
ADMINS = (("Support", f"{config('ADMINS_USER')}"),)
