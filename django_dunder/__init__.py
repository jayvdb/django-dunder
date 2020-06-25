__version__ = VERSION = (0, 3, 0)

# Force the meta options to be added early
import django_dunder.core  # noqa

default_app_config = 'django_dunder.apps.DunderConfig'
