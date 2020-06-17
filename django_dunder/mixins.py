from django.db import models

from .core import _to_string, FIELD_REPR_FMT, FIELD_STR_FMT

__all__ = [
    'DunderReprModel',
    'DunderStrModel',
    'DunderModel',
]


class DunderReprModel(models.Model):
    class Meta:
        abstract = True

    def __repr__(self):
        return _to_string(
            model=self,
            meta_field_name='repr_fields',
            fmt=FIELD_REPR_FMT,
        )


class DunderStrModel(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return _to_string(
            model=self,
            meta_field_name='str_fields',
            fmt=FIELD_STR_FMT,
        )


class DunderModel(DunderReprModel, DunderStrModel):
    class Meta:
        abstract = True
