from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.db import models

try:
    from django.utils.encoding import python_2_unicode_compatible
except ImportError:
    from six import python_2_unicode_compatible

import django_dunder.app_settings as app_settings
from django_dunder._register import _has_default_str, PY3

from django_fake_model import models as f

if PY3:
    # Quieten pyflakes
    unicode = ''.__class__


class StrHasDunderUnicode(f.FakeModel):
    name = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return 'model.__unicode__'


@StrHasDunderUnicode.fake_me
def test_unicode_dunder_only():
    # Default, c.f. conftest
    assert not app_settings.COPY_UNICODE
    assert app_settings.WARN_UNICODE
    assert not app_settings.REJECT_UNICODE

    # Django doesnt provide __unicode__ even on Python 2
    assert not hasattr(models.Model, '__unicode__')

    if PY3:
        assert _has_default_str(StrHasDunderUnicode)
    else:
        assert not _has_default_str(StrHasDunderUnicode)

    item = StrHasDunderUnicode.objects.create()

    if not PY3:
        assert str(item) == 'model.__unicode__'


@StrHasDunderUnicode.fake_me
def test_unicode_dunder_copy():
    app_settings.COPY_UNICODE = True

    assert not _has_default_str(StrHasDunderUnicode)

    item = StrHasDunderUnicode.objects.create()
    assert str(item) == 'model.__unicode__'

    app_settings.COPY_UNICODE = False


class StrDualDunder(f.FakeModel):
    name = models.TextField(null=True, blank=True)

    def __str__(self):
        return 'model.__str__'

    def __unicode__(self):
        return 'model.__unicode__'


@StrDualDunder.fake_me
def test_unicode_dunder_ignored():
    # Default, c.f. conftest
    assert not app_settings.COPY_UNICODE

    assert not _has_default_str(StrDualDunder)

    item = StrDualDunder.objects.create()

    assert str(item) == 'model.__str__'

    app_settings.COPY_UNICODE = True

    # Dont copy if __str__ was present
    assert not _has_default_str(StrDualDunder)

    item = StrDualDunder.objects.create()
    assert str(item) == 'model.__str__'
    if not PY3:
        assert unicode(item) == 'model.__unicode__'

    app_settings.COPY_UNICODE = False


class StrDunderDupped(f.FakeModel):
    name = models.TextField(null=True, blank=True)

    def __str__(self):
        return 'model.__str__'

    __unicode__ = __str__


@StrDunderDupped.fake_me
def test_unicode_dunder_dupped():
    # Default, c.f. conftest
    assert not app_settings.COPY_UNICODE

    assert not _has_default_str(StrDunderDupped)

    item = StrDunderDupped.objects.create()

    assert str(item) == 'model.__str__'

    app_settings.REJECT_UNICODE = True

    try:
        _has_default_str(StrDunderDupped)
    except ImproperlyConfigured:
         if not PY3:
             raise
    else:
         if PY3:
             assert False, 'ImproperlyConfigured not raised'

    app_settings.REJECT_UNICODE = False


class StrDunderUnicodeParent(f.FakeModel):
    name = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return 'model.__unicode__'

    class Meta:
        abstract = True


class StrDunderUnicodeChildOne(StrDunderUnicodeParent):
    pass


class StrDunderUnicodeChildTwo(StrDunderUnicodeParent):

    def __str__(self):
        return 'model.__str__'


@StrDunderUnicodeChildOne.fake_me
@StrDunderUnicodeChildTwo.fake_me
def test_unicode_dunder_inherited():
    app_settings.COPY_UNICODE = True

    assert not _has_default_str(StrDunderUnicodeChildOne)
    assert not _has_default_str(StrDunderUnicodeChildTwo)

    item = StrDunderUnicodeChildOne.objects.create()

    assert str(item) == 'model.__unicode__'
    if not PY3:
        assert unicode(item) == 'model.__unicode__'

    # Dont copy if __str__ was present
    assert not _has_default_str(StrDunderUnicodeChildTwo)

    item = StrDunderUnicodeChildTwo.objects.create()
    assert str(item) == 'model.__str__'

    if not PY3:
        assert unicode(item) == 'model.__unicode__'

    app_settings.COPY_UNICODE = False


class StrHasDunderUnicodeCompat(f.FakeModel):

    def __str__(self):
        return 'model.__str__'


@StrHasDunderUnicodeCompat.fake_me
def test_unicode_dunder_compat():
    app_settings.COPY_UNICODE = False

    assert hasattr(StrHasDunderUnicodeCompat, '__str__')
    assert not hasattr(StrHasDunderUnicodeCompat, '__unicode__')

    orig_str_func = StrHasDunderUnicodeCompat.__str__

    StrHasDunderUnicodeWrapped = python_2_unicode_compatible(
        StrHasDunderUnicodeCompat)

    assert hasattr(StrHasDunderUnicodeWrapped, '__str__')
    if PY3:
        assert not hasattr(StrHasDunderUnicodeWrapped, '__unicode__')
    else:
        assert hasattr(StrHasDunderUnicodeWrapped, '__unicode__')

    # python_2_unicode_compatible moves __str__ to __unicode__,
    # and creates a safe __str__
    if PY3:
        assert StrHasDunderUnicodeWrapped.__str__ == orig_str_func
        assert not hasattr(StrHasDunderUnicodeWrapped, '__unicode__')
    else:
        assert StrHasDunderUnicodeWrapped.__unicode__ == orig_str_func
        assert StrHasDunderUnicodeWrapped.__str__ != orig_str_func

    str_func = StrHasDunderUnicodeCompat.__str__
    if not PY3:
        unicode_func = StrHasDunderUnicodeCompat.__unicode__

    assert not _has_default_str(StrHasDunderUnicodeWrapped)

    assert StrHasDunderUnicodeCompat.__str__ == str_func
    if PY3:
        assert not hasattr(StrHasDunderUnicodeWrapped, '__unicode__')
    else:
        assert StrHasDunderUnicodeCompat.__unicode__ == unicode_func

    item = StrHasDunderUnicodeWrapped.objects.create()

    assert str(item) == 'model.__str__'
    if not PY3:
        assert unicode(item) == 'model.__str__'

    app_settings.COPY_UNICODE = True

    assert not _has_default_str(StrHasDunderUnicodeWrapped)

    # Check nothing changed
    assert StrHasDunderUnicodeCompat.__str__ == str_func
    if PY3:
        assert not hasattr(StrHasDunderUnicodeWrapped, '__unicode__')
    else:
        assert StrHasDunderUnicodeCompat.__unicode__ == unicode_func

    app_settings.COPY_UNICODE = False
