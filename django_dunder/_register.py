from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.db.models.signals import class_prepared
from django.dispatch import receiver

from .app_settings import (
    _ANY_REGISTER,
    AUTO,
    AUTO_REPR,
    AUTO_STR,
    FORCE,
    FORCE_REPR,
    FORCE_STR,
    REPR_EXCLUDE,
    STR_EXCLUDE,
)
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


def _should_force_repr(label):
    if FORCE_REPR is False:
        return False

    if isinstance(FORCE_REPR, list):
        return label in FORCE_REPR

    if REPR_EXCLUDE:
        return label not in REPR_EXCLUDE

    return FORCE

def _should_force_str(label):
    if FORCE_STR is False:
        return False

    if isinstance(FORCE_STR, list):
        return label in FORCE_STR

    if STR_EXCLUDE:
        return label not in STR_EXCLUDE

    return FORCE


@receiver(class_prepared)
def _patch_model_cls(sender, **kwargs):
    global _dunder_applied_counter, _model_name_counter

    # This is used to prefix duplicated names
    _model_name_counter[sender.__class__.__name__] += 1

    if not _ANY_REGISTER:
        return

    label = sender._meta.label

    if sender.__repr__ != _model_repr:
        if _should_force_repr(sender) or (AUTO_REPR and _has_default_repr(sender)):
            if not REPR_EXCLUDE or label not in REPR_EXCLUDE:
                _dunder_applied_counter += 1
                sender.__repr__ = _model_repr

    if sender.__str__ != _model_str:
        if _should_force_str(label) or (AUTO_STR and _has_default_str(sender)):
            if not STR_EXCLUDE or label not in STR_EXCLUDE:
                _dunder_applied_counter += 1
                sender.__str__ = _model_str
