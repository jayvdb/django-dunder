import sys
import warnings

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.db.models.signals import class_prepared
from django.dispatch import receiver

from . import app_settings
from .core import (
    _dunder_applied_counter,
    _model_name_counter,
    _model_repr,
    _model_str,
)

PY3 = sys.version_info[0] == 3
DJ2_UNICODE_MSG = (
    'For compatability with Django 2, add @six.python_2_unicode_compatible '
    'to the class'
)


def _has_default_repr(model):
    for cls in model.__mro__:
        if '__repr__' in cls.__dict__:
            if cls.__repr__ == Model.__repr__:
                return True
            else:
                return False


# This also patches model.__str__ if a __unicode__ is found first
def _has_default_str(model):
    for cls in model.__mro__:
        if cls == Model:
            return True

        unicode_func = cls.__dict__.get('__unicode__', None)

        # Copy the __unicode__ to __str__ on the appropriate class.
        # Subsequent models inheriting from that class will skip the
        # copy, but still warn.
        str_func = cls.__dict__.get('__str__', None)

        if unicode_func:
            from_model = ''
            if cls != model:
                from_model = ' (inherited from {})'.format(cls)

            if PY3 and app_settings.REJECT_UNICODE:
                raise ImproperlyConfigured(
                    '{}.__unicode__{} detected.  {}'
                    .format(model._meta.label, from_model, DJ2_UNICODE_MSG)
                )

            warn_unicode = app_settings.WARN_UNICODE
            copy_unicode = app_settings.COPY_UNICODE if PY3 else False

            if unicode_func == str_func:
                copied = getattr(str_func, '_copied', False)
                if not copied and warn_unicode and PY3:
                    warnings.warn(
                        '{}.__unicode__{} is duplicating its __str__ method, '
                        'and is unwanted on Python 3.  {}'
                        .format(model._meta.label, from_model, DJ2_UNICODE_MSG)
                    )
                return False

            if str_func and PY3:
                warnings.warn(
                    '{}.__unicode__{} is different to its __str__. '
                    'The __unicode__ should be removed on Python 3.  {}'
                    .format(model._meta.label, from_model, DJ2_UNICODE_MSG)
                )
                return False

            elif not str_func:
                warnings.warn(
                    '{}.__unicode__{} will not be used on Python 3; '
                    'Inform owner of model to add a __str__, and remove '
                    'the __unicode__ on Python 3.  {}'
                    .format(model._meta.label, from_model, DJ2_UNICODE_MSG)
                )

            if copy_unicode:
                # Tag the method so that it wont be the subject of warnings
                cls.__unicode__._copied = True
                _patch_model_cls(model, '__str__', cls.__unicode__)
                return False

            if not PY3:
                return False

        if str_func:
            return False


def _should_force_repr(label, model, has_default_func):
    if label in app_settings.REPR_EXCLUDE:
        return False

    if label in app_settings.FORCE_REPR:
        return True

    if app_settings.AUTO_REPR and has_default_func(model):
        return True

    return False


def _should_force_str(label, model, has_default_func):
    if label in app_settings.STR_EXCLUDE:
        return False

    if label in app_settings.FORCE_STR:
        return True

    if app_settings.AUTO_STR or app_settings.REJECT_UNICODE:
        if has_default_func(model):
            return True

    return False


def _patch_model_cls(model, method_name, new_func):
    global _dunder_applied_counter
    # TODO: Use __unicode__ on PY2
    setattr(model, method_name, new_func)
    _dunder_applied_counter += 1


def _model_cls_patcher(sender, **kwargs):
    global _dunder_applied_counter, _model_name_counter

    # This is used to prefix duplicated names
    _model_name_counter[sender.__class__.__name__] += 1

    if not app_settings._ANY_REGISTER:
        return

    label = sender._meta.label

    if sender.__repr__ != _model_repr:
        if _should_force_repr(label, sender, _has_default_repr):
            _patch_model_cls(sender, '__repr__', _model_repr)

    if sender.__str__ != _model_str:
        if _should_force_str(label, sender, _has_default_str):
            _patch_model_cls(sender, '__str__', _model_str)


def _register_models_receiver():
    receiver(class_prepared)(_model_cls_patcher)
