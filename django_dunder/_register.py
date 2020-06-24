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


def _has_default_repr(model):
    for cls in model.__mro__:
        if '__repr__' in cls.__dict__:
            if cls.__repr__ == Model.__repr__:
                return True
            else:
                return False


def _has_default_str(model):
    for cls in model.__mro__:
        if '__str__' in cls.__dict__:
            if cls.__str__ == Model.__str__:
                return True
            else:
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

    if app_settings.AUTO_STR and has_default_func(model):
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
