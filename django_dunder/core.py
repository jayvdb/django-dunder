import collections
import functools

from django.db import models
from django.db.models import fields

from . import app_settings

from ._formatter import FormattableObjectWrapper

_model_name_counter = collections.Counter()
_dunder_applied_counter = 0


def field_value(model, field):
    value = getattr(model, field.name)

    default = field.default
    if value == default:
        return None
    elif default is models.NOT_PROVIDED:
        if isinstance(field, models.CharField) and value == '':
            return None

    return value


def _format_field(model, field, fmt=None, wrap=True):
    """Obtain either "bar_id=9" or "bar='bar_value'" str.

    field is a Django Field object.
    """
    if isinstance(field, models.ForeignKey):
        field_name = field.name + '_id'
    else:
        field_name = field.name
    return _format_field_raw(model, field, field_name, fmt=fmt, wrap=wrap)


def _format_field_raw(model, field, field_name=None, fmt=None, wrap=True):
    """Obtain "bar='bar_value'" str.

    field is a Django Field object.
    field_name is either field.name or field.name + '_id'
    """
    if not fmt:
        fmt = app_settings.STR_ATTR_FMT

    value = field_value(model, field)
    if not value:
        return ''

    if wrap:
        value = app_settings.WRAPPER_CLASS(value)

    return fmt.format(name=field_name or field.name, value=value)


def _to_string(model, meta_field_name, instance_fmt, field_fmt, wrap=False):
	
    self = model
    fmt = field_fmt
    cls = type(self)
    meta_fields = cls._meta.fields
    has_autofield = isinstance(meta_fields[0], fields.AutoField)
    selected_field_names = None
    if hasattr(cls._meta, meta_field_name):
        selected_field_names = getattr(cls._meta, meta_field_name)
    elif cls._meta.unique_together:
        selected_field_names = next(iter(cls._meta.unique_together))
    elif len(meta_fields) > 1:
        uniq_fields = [f for f in (meta_fields[1:] if has_autofield else meta_fields) if f.unique]
        if uniq_fields:
            # TODO: determine which is best
            selected_field_names = [uniq_fields[0].name]

    if selected_field_names:
        meta_fields_filtered = [f for f in meta_fields if f.name in selected_field_names]
        meta_fields_filtered.sort(key=lambda f: selected_field_names.index(f.name))

        func = functools.partial(_format_field_raw, self, fmt=fmt, wrap=wrap)
        parts = filter(None, map(func, meta_fields_filtered))
    elif len(meta_fields) < 3:
        # _raw shows 'other=Foo' instead of other_id=3
        func = functools.partial(_format_field_raw, self, fmt=fmt, wrap=wrap)
        parts = filter(None, map(func, meta_fields))
    else:
        func = functools.partial(_format_field, self, fmt=fmt, wrap=wrap)
        parts = filter(None, map(func, meta_fields))

    parts = list(parts)

    if has_autofield and len(meta_fields) == 2 and len(parts) == 2:
        # Ignore unnecessary 'id'
        parts = [parts[1]]

    attrs = ', '.join(parts)

    if not attrs and has_autofield:
        attrs = _format_field_raw(self, meta_fields[0], fmt=fmt, wrap=wrap)

    if _model_name_counter[cls.__name__] > 1:
        model_name = cls._meta.label
    else:
        model_name = cls.__name__

    rv = instance_fmt.format(model_name, attrs)
    return rv


def _model_repr(self):
    return _to_string(
        model=self,
        meta_field_name='repr_fields',
        instance_fmt=app_settings.REPR_FMT,
        field_fmt=app_settings.REPR_ATTR_FMT,
        wrap=True,
    )


def _model_str(self):
    return _to_string(
        model=self,
        meta_field_name='str_fields',
        instance_fmt=app_settings.STR_FMT,
        field_fmt=app_settings.STR_ATTR_FMT,
        wrap=True,
    )
