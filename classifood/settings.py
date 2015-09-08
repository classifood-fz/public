# Django settings for Classifood.

import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

CONTACT_RECIPIENT_EMAIL = 'felix.zheng@classifood.com'
MAILER_EMAIL = 'Classifood <classifood.noreply@gmail.com>'

GOOGLE_CLIENT = {}

LABEL_API_HOST = ''
LABEL_API_KEY = ''

STRIPE_SECRET_KEY = ''
STRIPE_PUBLIC_KEY = ''

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

AES_SECRET_KEY=''

SECRET_KEY = ''

# Clickjacking protection
# Deny all frame or iframe resources from loading
X_FRAME_OPTIONS = 'DENY'

ADMINS = (
    ('fzheng', 'felix.zheng@classifood.com')
)

MANAGERS = ADMINS

DATABASES = {}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'google.appengine.ext.ndb.django_middleware.NdbDjangoMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'classifood.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'classifood.wsgi.application'

TEMPLATE_DIRS = (
#    Template directory path is not required when app has been added to
#      settings.INSTALLED_APPS and /templates is inside app directory
    os.path.dirname(os.path.abspath(__file__)) + '/templates',
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'classifood',
#     'django.contrib.messages',
#     'django.contrib.auth',
#     'django.contrib.sessions',
#     'django.contrib.sites',
#     'django.contrib.staticfiles',
#     'django.contrib.admin',
#     'django.contrib.admindocs',
)
