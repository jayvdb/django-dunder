# django-dunder

django-dunder is an installable app to automatically provide usable
`__repr__` and `__str__` for other Django third-party installable apps
and for project apps.

The motivation for this app came while consulting for
https://github.com/viper-development/ , which builds apps quickly,
developing custom functionality instead of writing boilerplate code.

By default, it will detect and attach to existing models that are using
the default `__repr__` and `__str__`.

It can be instructed to overwrite the `__repr__` and `__str__` of specific
models, useful if the model has dedicated methods, but the output is not
desirable.

It will look for primary and unique keys, in an attempt to show the minimum
necessary for the user to recognise the record.

## Install

1. `pip install django-dunder`
2. Add `django_dunder` to `INSTALLED_APPS` *before* models that need
   dunders added.

To catch all models missing `__str__` or `__repr__`, put it at the top
of `INSTALLED_APPS`.

To quickly see how it improves the Django admin, install
[`django-data-browser`](https://github.com/tolomea/django-data-browser)
in development before and after, and click its "admin" column on
any model that was using the Django default string representation.

## Configure

For more control, in your `settings`, toggle these "auto", "force" and
"exclude" settings.

To disable the automatic attaching for one or both of `__str__` and `__repr__`,
set one of

- `DUNDER_AUTO = False`
- `DUNDER_AUTO_REPR = False`
- `DUNDER_AUTO_STR = False`

To force all models to use these methods, use `DUNDER_FORCE = True`, or
set `DUNDER_FORCE_REPR` or `DUNDER_FORCE_STR` to `True`.

To force specific models only, `DUNDER_FORCE_REPR` and `DUNDER_FORCE_STR`
may be defined as a list of model labels, e.g. `auth.User`.

When using either auto or force modes, specific models can be excluded
by providing a list of model labels to the exclude settings:

```py
DUNDER_REPR_EXCLUDE = ['auth.User']
DUNDER_STR_EXCLUDE = ['myapp.Person']
```

## Explicit fields

To show specific fields in either `str()` or `repr()`, two extra model meta
options are automatically available:

```py
from django.db import models

class MyModel(models.Model):
    uuid = models.TextField()
    first_name = models.TextField()
    last_name = models.TextField()
    ...

    Meta:
        str_fields = ('first_name', 'last_name')
        repr_fields = ('uuid', )
```

## Explicit mixins

Alternatively disable auto mode (`DUNDER_AUTO = False`), and use the
mixins, and set the :

```py
from django_dunder.mixins import DunderModel

class MyModel(DunderModel):
    first_name = models.TextField()
    last_name = models.TextField()
    ...

    Meta:
        repr_fields = ('first_name', 'last_name')
```

Adding Meta options can cause exceptions if django-dunders is removed
from `INSTALLED_APPS`.

To avoid that, use [djsommo](https://github.com/jayvdb/djsommo)

## Alternatives

django-dunder is especially useful when a project uses third-party apps
that do not provide these dunder methods that are suitable for the project.
In fact, several `django.contrib` models do not provide these dunder methods.

If that is not relevant, and if the project is using sentry, and the project
only wants a sane `__repr__`, incorporate the decorator in
[`sentry.db.models`](https://github.com/getsentry/sentry/blob/master/src/sentry/db/models/base.py)
into a base mixin model used throughout the project.

Inspiration was drawn from
- [django-model-repr](https://github.com/relip/django-model-repr)
- [django-auto-repr](https://github.com/dan-passaro/django-auto-repr)

They may be sufficient for some projects.
