"""
Django settings for weixin_inner project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vu4*8!tm@!v-o!gk%5+1yer71&e$un&*72b@)peh*@wd-i7&dl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inner_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'weixin_inner.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'weixin_inner.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'ibm_db_django',
        'NAME': 'nxwxdb',
        'USER': 'nanxun',
        'PASSWORD': 'qwe123',
        'HOST': 'localhost',
        'PORT': '60000',
	    'PCONNECT': True,
    },
    'old_credits': {
        'ENGINE': 'ibm_db_django',
        'NAME': 'nxwxdb',
        'USER': 'ydw',
        'PASSWORD': 'qwe123',
        'HOST': 'localhost',
        'PORT': '60000',
        'PCONNECT': True,
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'django': {
            'format': '[%(asctime)s] %(message)s',
        },
        'developer': {
            'format': '[%(asctime)s] %(levelname)s: %(filename)s:%(lineno)d\n%(message)s',
        },
    },
    'handlers': {
        'django': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.environ['WXBANK_HOME'] + '/log/django/weixin_inner.log',
            'formatter': 'django',
        },
        'developer': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',#'logging.FileHandler',
            #'filename': os.environ['WXBANK_HOME'] + '/log/django/weixin_inner.log',
            'formatter': 'developer',
        },
    },
    'loggers': {
        #'django': {
        #    'handlers': ['django'],
        #    'level': 'INFO',
        #},
        'developer': {
            'handlers': ['developer'],
            'level': 'DEBUG',
        },
    },
}
