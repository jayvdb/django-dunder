import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def get_setting_safe(name, default):
    try:
        return getattr(settings, 'DUNDER_' + name, default)
    except ImproperlyConfigured:
        return default


class _AlwaysContains(object):

    def __init__(self, value):
        self.value = bool(value)

    def __contains__(self, value):
        return self.value

    def __bool__(self):
        return self.value

    def __eq__(self, other):
        return self.value == bool(other)

    __nonzero__ = __bool__

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    __str__ = __repr__


def _post_process():
    global FORCE_REPR, FORCE_STR, REPR_EXCLUDE, STR_EXCLUDE, _ANY_REGISTER

    if isinstance(FORCE_REPR, list) and isinstance(FORCE, list):
        FORCE_REPR += FORCE
    elif isinstance(FORCE_REPR, bool):
        FORCE_REPR = _AlwaysContains(FORCE_REPR)

    if isinstance(FORCE_STR, list) and isinstance(FORCE, list):
        FORCE_STR += FORCE
    elif isinstance(FORCE_STR, bool):
        FORCE_STR = _AlwaysContains(FORCE_STR)

    _ANY_REGISTER = (
        AUTO or AUTO_REPR or AUTO_STR or FORCE or FORCE_REPR or FORCE_STR)

    if isinstance(REPR_EXCLUDE, bool):
        REPR_EXCLUDE = _AlwaysContains(REPR_EXCLUDE)

    if isinstance(STR_EXCLUDE, bool):
        STR_EXCLUDE = _AlwaysContains(STR_EXCLUDE)


AUTO = get_setting_safe('AUTO', False)

AUTO_REPR = get_setting_safe('AUTO_REPR', AUTO)
AUTO_STR = get_setting_safe('AUTO_STR', AUTO)

FORCE = get_setting_safe('FORCE', False)

FORCE_REPR = get_setting_safe('FORCE_REPR', FORCE)
FORCE_STR = get_setting_safe('FORCE_STR', FORCE)

REPR_EXCLUDE = get_setting_safe('REPR_EXCLUDE', False)
STR_EXCLUDE = get_setting_safe('STR_EXCLUDE', False)

_post_process()
