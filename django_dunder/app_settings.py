import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def get_setting_safe(name, default):
    try:
        return getattr(settings, 'DUNDER_' + name, default)
    except ImproperlyConfigured:
        return default

_PYTEST = 'pytest' in sys.modules

AUTO = get_setting_safe('AUTO', False if _PYTEST else True)

AUTO_REPR = get_setting_safe('AUTO_REPR', AUTO)
AUTO_STR = get_setting_safe('AUTO_STR', AUTO)

FORCE = get_setting_safe('FORCE', False)

FORCE_REPR = get_setting_safe('FORCE_REPR', False)
FORCE_STR = get_setting_safe('FORCE_STR', False)

_ANY_REGISTER = (
    AUTO or AUTO_REPR or AUTO_STR or FORCE or FORCE_REPR or FORCE_STR)

REPR_EXCLUDE = get_setting_safe('REPR_EXCLUDE', False)
STR_EXCLUDE = get_setting_safe('STR_EXCLUDE', False)
