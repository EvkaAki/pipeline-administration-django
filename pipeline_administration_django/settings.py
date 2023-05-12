from pathlib import Path
import environ
import os
import kfp


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
U_BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o4c+gl@ll&falq9p2qw1ih9!808u(1(+-4w338$st37y3-kyln'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEV_MODE = os.environ.get("DEV_MODE")
PIPELINE_URL = os.getenv("PIPELINE_URL")

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'app',
    'kubeflow_admin',
    'kubeflow_researcher',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
  'http://dp.host.haus',
)
X_FRAME_OPTIONS = 'ALLOW-FROM http://dp.host.haus'


ROOT_URLCONF = 'pipeline_administration_django.urls'

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

WSGI_APPLICATION = 'pipeline_administration_django.wsgi.application'


environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

env = environ.Env(
    DEBUG=(bool, True)
)

environ.Env.read_env()

DATABASES = {
    'default': env.db(),
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

DEFAULT_AUTO_FIELD = 'django.db.models.UUIDField'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
client = kfp.Client(host=PIPELINE_URL, credentials=credentials)

namespace = client.get_user_namespace()

STATIC_URL_LOCAL = 'static/'

if DEV_MODE == 'True':
    STATIC_URL = '/static/'
else:
    STATIC_URL = '/run-requests/' + namespace + '/static/'


STATIC_ROOT = os.path.join(BASE_DIR, 'static')


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'pipeline_administration_django/static'),
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


if DEV_MODE == 'True':
    DATAPROVIDER_API_ENDPOINT = 'http://localhost:8081'
else:
    DATAPROVIDER_API_ENDPOINT = 'http://data-provider-service.kubeflow.svc.cluster.local:5000'
