from .base import *  # noqa


DEBUG = config("DEBUG", default=False, cast=bool)
ENABLE_DEBUG_TOOLBAR = True

if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS += [  # noqa
        "debug_toolbar",
    ]

    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa

    INTERNAL_IPS = [
        "127.0.0.1",
    ]

    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _request: ENABLE_DEBUG_TOOLBAR}
