from django.db import models

from django_nine.versions import DJANGO_GTE_2_0

from django_dunder.core import _model_name_counter
from django_dunder.mixins import DunderReprModel
from django_dunder._register import _has_default_repr

from django_fake_model import models as f


class ReprDefaultOrig(f.FakeModel):
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)


class ReprDefault(DunderReprModel, f.FakeModel):
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)


@ReprDefaultOrig.fake_me
@ReprDefault.fake_me
def test_repr_default():
    assert _has_default_repr(ReprDefaultOrig)
    assert not _has_default_repr(ReprDefault)

    item_orig = ReprDefaultOrig.objects.create(name1='a', name2='b')

    if DJANGO_GTE_2_0:
        assert repr(item_orig) == "<ReprDefaultOrig: ReprDefaultOrig object (1)>"
    else:
        assert repr(item_orig) == "<ReprDefaultOrig: ReprDefaultOrig object>"

    item = ReprDefault.objects.create(name1='a', name2='b')

    assert repr(item) == "ReprDefault(id=1, name1='a', name2='b')"


class Explicit(DunderReprModel, f.FakeModel):
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)

    class Meta:
        repr_fields = ('name2', 'name1')


@Explicit.fake_me
def test_repr_explicit():
    item = Explicit.objects.create(name1='a', name2='b')

    assert repr(item) == "Explicit(name2='b', name1='a')"

    item = Explicit.objects.create(name2='b')

    assert repr(item) == "Explicit(name2='b')"

    item = Explicit.objects.create(name1='a')

    assert repr(item) == "Explicit(name1='a')"


class UniqueTogether(DunderReprModel, f.FakeModel):
    name = models.TextField(null=True, blank=True)
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('name1', 'name2')


@UniqueTogether.fake_me
def test_repr_unique_together():
    item = UniqueTogether.objects.create(
        name="z", name1="a", name2="b")

    assert repr(item) == "UniqueTogether(name1='a', name2='b')"


class UniqueTogetherSet(DunderReprModel, f.FakeModel):
    name = models.TextField(null=True, blank=True)
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = set(['name1', 'name2'])


@UniqueTogether.fake_me
def test_repr_unique_together_set():
    item = UniqueTogether.objects.create(
        name="z", name1="a", name2="b")

    assert repr(item) == "UniqueTogether(name1='a', name2='b')"


class OneField(DunderReprModel, f.FakeModel):
    name = models.TextField(null=True, blank=True)


@OneField.fake_me
def test_repr_one_field():
    item = OneField.objects.create()

    assert repr(item) == 'OneField(id=1)'

    item = OneField.objects.create(name='a')

    assert repr(item) == "OneField(name='a')"


class NameConflict1(DunderReprModel, f.FakeModel):

    class Meta:
        app_label = 'myapp1'


class NameConflict2(DunderReprModel, f.FakeModel):

    class Meta:
        app_label = 'myapp2'


@NameConflict1.fake_me
@NameConflict2.fake_me
def test_repr_explicit_app():
    # Simulate them having the same name in different apps
    _model_name_counter['NameConflict1'] = 2
    _model_name_counter['NameConflict2'] = 2

    item1 = NameConflict1.objects.create()
    item2 = NameConflict2.objects.create()

    assert repr(item1) == 'myapp1.NameConflict1(id=1)'
    assert repr(item2) == 'myapp2.NameConflict2(id=1)'


class ReprHasDunderRepr(f.FakeModel):
    name = models.TextField(null=True, blank=True)

    def __repr__(self):
        return 'model.__repr__'


@ReprHasDunderRepr.fake_me
def test_auto_ignore_existing():
    assert not _has_default_repr(ReprHasDunderRepr)

    item = ReprHasDunderRepr.objects.create()

    assert repr(item) == 'model.__repr__'


class ReprHasDunderReprParent(f.FakeModel):
    name = models.TextField(null=True, blank=True)

    def __repr__(self):
        return 'model.__repr__'

    class Meta:
        abstract = True


class ReprHasDunderReprChild(ReprHasDunderReprParent):
    pass


@ReprHasDunderReprChild.fake_me
def test_auto_ignore_existing_inheritance():
    assert not _has_default_repr(ReprHasDunderReprChild)

    item = ReprHasDunderReprChild.objects.create()

    assert repr(item) == 'model.__repr__'
