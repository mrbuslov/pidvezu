from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

import dotenv # чтобы можно было брать переменные из .env
if os.path.isfile(os.path.join(".env")):
    dotenv.load_dotenv(os.path.join(".env"))

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = '/static/'
STATIC_ROOT = "/ABSOLUTE/PATH/TO/STATIC_PARENT_FLD"
# STATICFILES_DIRS = (
#   os.path.join(BASE_DIR, 'static'),
# )
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL='/'
MEDIA_ROOT = '/ABSOLUTE/PATH/TO/MEDIA_FLD/'

SECRET_KEY = os.environ['SECRET_KEY']
TOKEN = os.environ['TELEGRAM_TOKEN']
BUSLOV_TELEGRAM = os.environ['BUSLOV_TELEGRAM']
ADMIN_GROUP_TELEGRAM = os.environ['ADMIN_GROUP_TELEGRAM']
DEBUG = False
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ["pidvezu.com.ua", "www.pidvezu.com.ua"] # в django версии 4 добавь в начало https://     у тебя версия 
SITE_ID = 1
AUTH_USER_MODEL = 'account.Account'

TIME_ZONE = 'Europe/Kiev'
USE_I18N = True #будет активизирована встроенная в Django система автоматического перевода на язык, записанный в параметре LANGUAGE CODE
USE_L10N = True # тrue, числа, значения даты и времени при выводе будут форматироваться по правилам языка из параметра LANGUAGE CODE
LANGUAGE_CODE = 'ru'
USE_TZ = True

LOGIN_URL="/login/" # перенаправление на страницу, при попытке авторизоваться в админке
LOGIN_REDIRECT_URL="/" # перенаправление на адрес после успешной попытки входа на сайт
LOGOUT_REDIRECT_URL = '/'

EMAIL_HOST = 'VPS.PROVIDER.SMTP.SERVER'
EMAIL_USE_SSL = True
EMAIL_PORT = 465 # 2525
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
SERVER_EMAIL = os.environ['EMAIL_HOST_USER']
DEFAULT_FROM_EMAIL = os.environ['EMAIL_HOST_USER']


# lang
# https://automationpanda.com/2018/04/21/django-admin-translations/   --- иконки в админке для перехода между языками
LANGUAGE_CODE = 'uk'
# rosetta
# http://127.0.0.1:8000/rosetta/files/project/
# python manage.py makemessages --all   (python manage.py makemessages --locale uk)
# python manage.py compilemessages 
LANGUAGES = (
    ('uk', _('Ukrainian')),
    ('ru', _('Russian'))
)
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
MODELTRANSLATION_LANGUAGES = ('uk','ru')
MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 1500 # default 1000
# rosetta сколько может быть для перевода
ROSETTA_MESSAGES_PER_PAGE = 50

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',

    'autostop',
    'account',
    'django_cleanup.apps.CleanupConfig', # для удаления изображений после удаления объекта
    'django_filters',
    'rosetta',
    'ckeditor',
    'ckeditor_uploader',
]
CKEDITOR_UPLOAD_PATH = 'images/social/'
# https://django-ckeditor.readthedocs.io/en/latest/
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['Image']
            # ['RemoveFormat', 'Source']
        ],
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # lang
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'autostop.middleware.MyMiddleware', # логгер
]

ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'autostop/templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'DB_NAME',
        'USER': 'YOUR_USERNAME', # postgres
        'PASSWORD': os.environ['PG_PASSWORD'],
        'HOST': 'YOUR_HOST',
        'PORT': 'YOUR_PORT',
        'ATOMIC_REQUESTS': True, # если у нас произошла ошибка при создании записи в БД, то она откатится (не создастся)  https://django.fun/docs/django/ru/3.2/topics/db/transactions/
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
