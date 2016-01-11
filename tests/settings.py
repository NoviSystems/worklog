import os
import socket

PROJECT_PATH = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.dirname(__file__)

SITE_URL = socket.gethostname()

SECRET_KEY = 'not-so-secret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'TEST': {
            'NAME': 'test.sqlite3',
        },
    }
}

ROOT_URLCONF = 'tests.urls'

DEFAULT_FROM_EMAIL = 'webmaster@lab.oscar.ncsu.edu'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'worklog',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
      # os.path.join(PROJECT_PATH, 'worklog', 'templates'),
      os.path.join(BASE_DIR, 'templates'),
)

STATIC_URL = '/static/'

USE_TZ = True

GITHUB_USER = 'itng-deploy'
GITHUB_PASS = ''

# WORKLOG SETTINGS
WORKLOG_SEND_REMINDERS = True

WORKLOG_SEND_REMINDERS_HOUR = 18

WORKLOG_EMAIL_REMINDERS_EXPIRE_AFTER = 4


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework_filters.backends.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.SessionAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'PAGINATE_BY': None,
}
