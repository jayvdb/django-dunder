from django.db import models

from .core import _model_repr, _model_str

__all__ = [
    'DunderReprModel',
    'DunderStrModel',
    'DunderModel',
]


class DunderReprModel(models.Model):
    class Meta:
        abstract = True

    __repr__ = _model_repr


class DunderStrModel(models.Model):
    class Meta:
        abstract = True

    __str__ = _model_str


class DunderModel(DunderReprModel, DunderStrModel):
    class Meta:
        abstract = True
