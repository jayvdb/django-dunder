from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


def get_setting_safe(name, default):
    try:
        return getattr(django_settings, 'DUNDER_' + name, default)
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
    global WRAPPER_CLASS

    if isinstance(FORCE_REPR, list) and isinstance(FORCE, list):
        FORCE_REPR += FORCE
    elif isinstance(FORCE_REPR, bool):
        FORCE_REPR = _AlwaysContains(FORCE_REPR)

    if isinstance(FORCE_STR, list) and isinstance(FORCE, list):
        FORCE_STR += FORCE
    elif isinstance(FORCE_STR, bool):
        FORCE_STR = _AlwaysContains(FORCE_STR)

    _ANY_REGISTER = (
        WARN_UNICODE or COPY_UNICODE or REJECT_UNICODE or
        AUTO or AUTO_REPR or AUTO_STR or FORCE or FORCE_REPR or FORCE_STR)

    if isinstance(REPR_EXCLUDE, bool):
        REPR_EXCLUDE = _AlwaysContains(REPR_EXCLUDE)

    if isinstance(STR_EXCLUDE, bool):
        STR_EXCLUDE = _AlwaysContains(STR_EXCLUDE)

    if isinstance(WRAPPER_CLASS, str):
        WRAPPER_CLASS = import_string(WRAPPER_CLASS)

AUTO = get_setting_safe('AUTO', True)

AUTO_REPR = get_setting_safe('AUTO_REPR', AUTO)
AUTO_STR = get_setting_safe('AUTO_STR', AUTO)

FORCE = get_setting_safe('FORCE', False)

FORCE_REPR = get_setting_safe('FORCE_REPR', FORCE)
FORCE_STR = get_setting_safe('FORCE_STR', FORCE)

REPR_EXCLUDE = get_setting_safe('REPR_EXCLUDE', False)
STR_EXCLUDE = get_setting_safe('STR_EXCLUDE', False)

WARN_UNICODE = get_setting_safe('WARN_UNICODE', True)

# Only in effect on Python 3
# Could be a list
COPY_UNICODE = get_setting_safe('COPY_UNICODE', AUTO_STR)

REJECT_UNICODE = get_setting_safe('REJECT_UNICODE',
    not django_settings.DEBUG and not COPY_UNICODE)

CHECK_INACTIVE_UNICODE = get_setting_safe(
    'CHECK_INACTIVE_UNICODE', 'error' if not COPY_UNICODE or REJECT_UNICODE else 'warn')

REPR_ATTR_FMT = get_setting_safe('REPR_ATTR_FMT', '{name}={value!r}')
STR_ATTR_FMT = get_setting_safe('STR_ATTR_FMT', '{name}={value}')

REPR_FMT = get_setting_safe('REPR_FMT', '{}({})')
STR_FMT = get_setting_safe('STR_FMT', '<{}: {}>')

WRAPPER_CLASS = get_setting_safe('WRAPPER_CLASS', 'django_dunder._formatter.FormattableObjectWrapper')

_post_process()
