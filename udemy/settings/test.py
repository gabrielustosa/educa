from ._base import *

DEBUG = False

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

INSTALLED_APPS.extend(
    [
        'udemy.apps.core',
    ]
)
