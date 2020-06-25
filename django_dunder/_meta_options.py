from django.db.models import options

# Django doesn't support adding third-party fields to model class Meta.
if 'repr_fields' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + (
        'repr_fields', 'str_fields')
