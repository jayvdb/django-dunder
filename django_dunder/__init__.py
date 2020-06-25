__version__ = VERSION = (0, 2, 1)

# Force the meta options to be added early
import django_dunder._meta_options  # noqa

default_app_config = 'django_dunder.apps.DunderConfig'
