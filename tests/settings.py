SECRET_KEY = 'not-so-secret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

ROOT_URLCONF = 'tests.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'worklog',
)

USE_TZ = True

GITHUB_USER = ''
GITHUB_PASS = ''
