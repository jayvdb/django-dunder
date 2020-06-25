from django.db import models

from django_nine.versions import DJANGO_GTE_2_0

from django_dunder.core import _model_name_counter
from django_dunder.mixins import DunderStrModel
from django_dunder._register import _has_default_str

from django_fake_model import models as f


class StrDefaultOrig(f.FakeModel):
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)


class StrDefault(DunderStrModel, f.FakeModel):
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)


@StrDefaultOrig.fake_me
@StrDefault.fake_me
def test_str_default():
    assert _has_default_str(StrDefaultOrig)
    assert not _has_default_str(StrDefault)

    item_orig = StrDefaultOrig.objects.create(name1='a', name2='b')

    if DJANGO_GTE_2_0:
        assert str(item_orig) == "StrDefaultOrig object (1)"
    else:
        assert str(item_orig) == "StrDefaultOrig object"

    item = StrDefault.objects.create(name1='a', name2='b')

    assert str(item) == "<StrDefault: id=1, name1=a, name2=b>"


class StrUniqueOrig(f.FakeModel):
    name1 = models.TextField(unique=True)
    name2 = models.TextField(null=True, blank=True)


class StrUnique(DunderStrModel, f.FakeModel):
    name1 = models.TextField(unique=True)
    name2 = models.TextField(null=True, blank=True)


@StrUniqueOrig.fake_me
@StrUnique.fake_me
def test_str_unique():
    item_orig = StrUniqueOrig.objects.create(name1='a', name2='b')

    if DJANGO_GTE_2_0:
        assert str(item_orig) == "StrUniqueOrig object (1)"
    else:
        assert str(item_orig) == "StrUniqueOrig object"

    item = StrUnique.objects.create(name1='a', name2='b')

    assert str(item) == "<StrUnique: name1=a>"


class StrPrimaryKeyOrig(f.FakeModel):
    name1 = models.TextField(primary_key=True)
    name2 = models.TextField(null=True, blank=True)


class StrPrimaryKey(DunderStrModel, f.FakeModel):
    name1 = models.TextField(primary_key=True)
    name2 = models.TextField(null=True, blank=True)


@StrPrimaryKeyOrig.fake_me
@StrPrimaryKey.fake_me
def test_str_primary_key():
    item_orig = StrPrimaryKeyOrig.objects.create(name1='a', name2='b')

    if DJANGO_GTE_2_0:
        assert str(item_orig) == "StrPrimaryKeyOrig object (a)"
    else:
        assert str(item_orig) == "StrPrimaryKeyOrig object"

    item = StrPrimaryKey.objects.create(name1='a', name2='b')

    assert str(item) == "<StrPrimaryKey: name1=a>"


class StrExplicit(DunderStrModel, f.FakeModel):
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)

    class Meta:
        str_fields = ('name2', 'name1')


@StrExplicit.fake_me
def test_str_explicit():
    item = StrExplicit.objects.create(name1='a', name2='b')

    assert str(item) == "<StrExplicit: name2=b, name1=a>"

    item = StrExplicit.objects.create(name2='b')

    assert str(item) == "<StrExplicit: name2=b>"

    item = StrExplicit.objects.create(name1='a')

    assert str(item) == "<StrExplicit: name1=a>"


class StrUniqueTogether(DunderStrModel, f.FakeModel):
    name = models.TextField(null=True, blank=True)
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('name1', 'name2')


@StrUniqueTogether.fake_me
def test_str_unique_together():
    item = StrUniqueTogether.objects.create(
        name="z", name1="a", name2="b")

    assert str(item) == "<StrUniqueTogether: name1=a, name2=b>"


class StrOneField(DunderStrModel, f.FakeModel):
    name = models.TextField(null=True, blank=True)


@StrOneField.fake_me
def test_str_one_field():
    item = StrOneField.objects.create()

    assert str(item) == '<StrOneField: id=1>'

    item = StrOneField.objects.create(name='a')

    assert str(item) == "<StrOneField: name=a>"


class StrNameConflict1(DunderStrModel, f.FakeModel):

    class Meta:
        app_label = 'myapp1'


class StrNameConflict2(DunderStrModel, f.FakeModel):

    class Meta:
        app_label = 'myapp2'


@StrNameConflict1.fake_me
@StrNameConflict2.fake_me
def test_str_explicit_app():
    # Simulate them having the same name in different apps
    _model_name_counter['StrNameConflict1'] = 2
    _model_name_counter['StrNameConflict2'] = 2

    item1 = StrNameConflict1.objects.create()
    item2 = StrNameConflict2.objects.create()

    assert str(item1) == '<myapp1.StrNameConflict1: id=1>'
    assert str(item2) == '<myapp2.StrNameConflict2: id=1>'


class StrHasDunderStr(f.FakeModel):
    name = models.TextField(null=True, blank=True)

    def __str__(self):
        return 'model.__str__'


@StrHasDunderStr.fake_me
def test_auto_ignore_existing():
    assert not _has_default_str(StrHasDunderStr)

    item = StrHasDunderStr.objects.create()

    assert str(item) == 'model.__str__'


class StrHasDunderStrParent(f.FakeModel):
    name = models.TextField(null=True, blank=True)

    def __str__(self):
        return 'model.__str__'

    class Meta:
        abstract = True


class StrHasDunderStrChild(StrHasDunderStrParent):
    pass


@StrHasDunderStrChild.fake_me
def test_auto_ignore_existing_inheritance():
    assert not _has_default_str(StrHasDunderStrChild)

    item = StrHasDunderStrChild.objects.create()

    assert str(item) == 'model.__str__'
