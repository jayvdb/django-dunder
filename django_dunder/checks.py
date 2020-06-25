import sys

from django.apps import apps
from django.core.checks import Error, Info, register, Warning

from .app_settings import CHECK_INACTIVE_UNICODE
from ._register import DJ2_UNICODE_MSG

PY3 = sys.version_info[0] == 3

@register()
def check_py2_unicode(app_configs, **kwargs):
    errors = []
    if not PY3 or not CHECK_INACTIVE_UNICODE:
        return

    if not app_configs:
        app_configs = apps.get_app_configs()

    check_cls = Error if CHECK_INACTIVE_UNICODE == 'error' else Warning
    check_prefix = 'E' if CHECK_INACTIVE_UNICODE == 'error' else 'W'
    check_id = 'django_under.{}001'.format(check_prefix)

    for app in app_configs:
        for model in app.models.values():
            unicode_func = getattr(model, '__unicode__', None)
            if unicode_func:
                str_func = getattr(model, '__str__', None)
                if unicode_func == str_func:
                    errors.append(
                        Info(
                            'Unnecessary {}.__unicode__ found'
                            .format(model._meta.label),
                            hint=DJ2_UNICODE_MSG,
                            obj=model,
                            id='django_under.I001',
                        )
                    )
                else:
                    errors.append(
                        check_cls(
                            'Custom {}.__unicode__ found but unused on Python 3'
                            .format(model._meta.label),
                            hint='Rename to __str__ or remove it',
                            obj=model,
                            id=check_id,
                        )
                    )

    return errors
