# django-dunder

django-dunder is an installable app to automatically provide customisable
`__repr__` and `__str__` for other Django third-party installable apps
and for project apps.

On Python 3, it can use `__unicode__` if present and `__str__` is missing,
such as apps that work on Python 3, but havent been fully updated.

It emits warnings whenever `__unicode__` is encountered on an active model.
It does this even on Python 2 when the `__unicode__`
is identical to the `__str__`, providing custom warnings to indicate what
code changes are needed to finish the Python 3 port.

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

*Note*: On Python 2, it will add a `__str__` which may emit non-ascii for
model instances containing Unicode values in the fields it decides to
display.  De-select any such models using the settings.  I am willing to
review a PR to add proper Python 2 support, but I will reject any partial
Python 2 support.  I can be convinced to build it to my own standards,
but it isnt sensible to do it in 2020 without a good reason.

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

To disable unicode warnings, set `DUNDER_WARN_UNICODE = False`.

For more control, in your `settings`, toggle these "auto", "force" and
"exclude" settings.

To disable the automatic attaching for one or both of `__str__` and `__repr__`,
set one of

- `DUNDER_AUTO = False`
- `DUNDER_AUTO_REPR = False`
- `DUNDER_AUTO_STR = False`
- `DUNDER_COPY_UNICODE = False`

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

*Note* When the copying of `__unicode__` is disabled on Python 3, and the
Django setting `DEBUG` is also disabled, this app will raise
`ImproperlyConfigured` if it finds a `__unicode__`, as it assumes the app
intended for the `__unicode__` to be used, and running in production with
the default Django `__str__` would result in incorrect behaviour.
To disable this, re-enable copying of the unicode, or set

- `DUNDER_REJECT_UNICODE = False`

There is also a Django [check](https://docs.djangoproject.com/en/3.0/topics/checks/)
for inactive custom `__unicode__`, which runs seperately from the model
registration process, so it is safer to use.  It defaults to emit errors,
however it can be set to emit errors, or disabled by setting it to `False`.

- `DUNDER_CHECK_INACTIVE_UNICODE = 'warn'`

### Formatting

The default formatting of `__str__` and `__repr__` given below can be modified
globally in the settings.

- `DUNDER_REPR_ATTR_FMT = '{name}={value!r}'`
- `DUNDER_REPR_FMT = '{}({})'`

- `DUNDER_STR_ATTR_FMT = '{name}={value}'`
- `DUNDER_STR_FMT = '<{}: {}>'`

In addition to standard Python string Formatter syntax, some experimental magic
behind the scenes allows the chaining together of attribute modifiers.
This is only active for the two attribute formatters.  Methods of types are
transparently invoked, and as are builtins.

e.g. `DUNDER_STR_ATTR_FMT = '{name}={value.round__title}'` will apply
round up numbers and apply title case to strings.

In addition, there is one extra modifier `ellipsis` that can be used to truncate
long text fields, appending an `...` ellipsis.  It defaults to 100 characters.

e.g. `DUNDER_STR_ATTR_FMT = '{name}={value.round__ellipsis_20}'` will apply
round up numbers and shorten strings to at most 20 characters.

On CPython, it is possible to add methods to core types using the `forbiddenfruit`
library.  For example, if [`datatype-tools`](https://github.com/edmundpf/datatype_tools)
is installed as directed, with imports in `settings.py` or some other early
loading Django code, use `()` syntax to use method names containing a `_`.

- `DUNDER_STR_ATTR_FMT = '{name}={value.round__ellipsis_20__format_date()}'`

When installing custom methods for core types from libraries, be aware they
often reuse existing core methods or builtin names.
In the case of `datatype-tools`, it provides a `float.round()` which uses
two significant places by default while `round(float)` has zero as default.

When building custom methods for core types, avoid using method names
which conflict with Python names or conflict with Django names.  Otherwise
problems like https://github.com/havocesp/typext/issues/1 arise.

Want more?  If you can find the experimental magic, extend it and activate with:

- `DUNDER_WRAPPER_CLASS = 'your_magic.Wrapper'`

And please submit PRs to add your magic here for others to use.

## Explicit fields

To show specific fields in either `str()` or `repr()`, two extra
[model meta options](https://docs.djangoproject.com/en/dev/ref/models/options)
are automatically added by django-dunder:

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

## Extending to other types

It should be possible to apply the functionality here to types other than
Django models and instances.  Some other way of identifying the appropriate
classes to patch is need, perhaps with additional configuration.

The ultimate solution for CPython-only would be if
[its type dunders could be 'curse'd](https://github.com/clarete/forbiddenfruit/issues/11),
especially if `object.__str__` and `object.__repr__` could be replaced.

## Alternatives

django-dunder is especially useful when a project uses third-party apps
that do not provide these dunder methods that are suitable for the project.
In fact, several `django.contrib` models do not provide these dunder methods.

Inspiration was drawn from
- [django-model-repr](https://github.com/relip/django-model-repr)
- [django-auto-repr](https://github.com/dan-passaro/django-auto-repr)

They may be sufficient for some projects.

If that is not relevant, and if the project is using sentry, and the project
only wants a sane `__repr__`, incorporate the decorator in
[`sentry.db.models`](https://github.com/getsentry/sentry/blob/master/src/sentry/db/models/base.py)
into a base mixin model used throughout the project.

Starting a new project, and only interested in your own models?
[pydantic](https://github.com/samuelcolvin/pydantic) provides default and customisable
dunders, and
[django-ninja](https://github.com/vitalik/django-ninja) provides a Django REST
interface on top, and there are lots of other tools layered on top of pydantic, like
[pydantic-ui](https://github.com/prismaticd/pydantic-ui) providing a Django Admin-like
interface.
