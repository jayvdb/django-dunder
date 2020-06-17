import collections
import functools

from django.db import models
from django.db.models import fields, options

# Django doesn't support adding third-party fields to model class Meta.
if 'repr_fields' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + (
        'repr_fields', 'str_fields')

_model_name_counter = collections.Counter()
_dunder_applied_counter = 0

FIELD_REPR_FMT="{}={!r}"
FIELD_STR_FMT="{}={}"


def field_value(model, field):
    value = getattr(model, field.name)

    default = field.default
    if value == default:
        return None
    elif default is models.NOT_PROVIDED:
        if isinstance(field, models.CharField) and value == '':
            return None

    return value


def _format_field(model, field, fmt=FIELD_REPR_FMT):
    """Obtain either "bar_id=9" or "bar='bar_value'" str.

    field is a Django Field object.
    """
    if isinstance(field, models.ForeignKey):
        field_name = field.name + '_id'
    else:
        field_name = field.name
    return _format_field_raw(model, field, field_name, fmt=fmt)


def _format_field_raw(model, field, field_name=None, fmt=FIELD_REPR_FMT):
    """Obtain "bar='bar_value'" str.

    field is a Django Field object.
    field_name is either field.name or field.name + '_id'
    """
    value = field_value(model, field)
    if not value:
        return ""

    return fmt.format(field_name or field.name, value)


def _to_string(model, meta_field_name, fmt):
    self = model
    cls = type(self)
    meta_fields = cls._meta.fields
    has_autofield = isinstance(meta_fields[0], fields.AutoField)
    selected_field_names = None
    if hasattr(cls._meta, meta_field_name):
        selected_field_names = getattr(cls._meta, meta_field_name)
    elif cls._meta.unique_together:
        selected_field_names = cls._meta.unique_together[0]
    elif len(meta_fields) > 1:
        uniq_fields = [f for f in (meta_fields[1:] if has_autofield else meta_fields) if f.unique]
        if uniq_fields:
            # TODO: determine which is best
            selected_field_names = [uniq_fields[0].name]

    if selected_field_names:
        meta_fields_filtered = [f for f in meta_fields if f.name in selected_field_names]
        meta_fields_filtered.sort(key=lambda f: selected_field_names.index(f.name))

        func = functools.partial(_format_field_raw, self, fmt=fmt)
        parts = filter(None, map(func, meta_fields_filtered))
    elif len(meta_fields) < 3:
        # _raw shows 'other=Foo' instead of other_id=3
        func = functools.partial(_format_field_raw, self, fmt=fmt)
        parts = filter(None, map(func, meta_fields))
    else:
        func = functools.partial(_format_field, self, fmt=fmt)
        parts = filter(None, map(func, meta_fields))

    parts = list(parts)

    if has_autofield and len(meta_fields) == 2 and len(parts) == 2:
        # Ignore unnecessary 'id'
        parts = [parts[1]]

    attrs = ', '.join(parts)

    if not attrs and has_autofield:
        attrs = _format_field_raw(self, meta_fields[0], fmt=fmt)

    if _model_name_counter[cls.__name__] > 1:
        model_name = cls._meta.label
    else:
        model_name = cls.__name__

    rv = '{}({})'.format(model_name, attrs)
    return rv
