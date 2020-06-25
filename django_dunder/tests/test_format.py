from django.db import models

from django_dunder import app_settings
from django_dunder.mixins import DunderModel
from django_dunder._register import PY3

from django_fake_model import models as f

if PY3:
    round_expected = '5'
else:
    round_expected = '5.0'

class FmtDefault(DunderModel, f.FakeModel):
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)
    decimal1 = models.DecimalField(null=True, blank=True, decimal_places=2)


@FmtDefault.fake_me
def test_str_fmt_item():
    item = FmtDefault.objects.create(name1='1234567890')

    #if not PY3:
    #    return
    app_settings.STR_ATTR_FMT = '{name}={value[4]}'
    assert str(item) == '<FmtDefault: id=1, name1=5>'

    app_settings.STR_ATTR_FMT = '{name}={value[0:5]}'
    if not PY3:
        return

    try:
        assert str(item) == '<FmtDefault: id=1, name1=12345>'
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    # TODO: Also try value[(0, 5)] and explicit slice to get it working on PY2


@FmtDefault.fake_me
def test_str_fmt_round():
    item = FmtDefault.objects.create(name1='abc', decimal1=5.12)

    app_settings.STR_ATTR_FMT = '{name}={value.round}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=abc, decimal1={}>'.format(round_expected)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_str_fmt_title():
    item = FmtDefault.objects.create(name1='abc')

    app_settings.STR_ATTR_FMT = '{name}={value.title}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Abc>'
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_str_fmt_title_func():
    item = FmtDefault.objects.create(name1='abc')

    app_settings.STR_ATTR_FMT = '{name}={value.title()}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Abc>'
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_str_fmt_multi():
    item = FmtDefault.objects.create(name1='abc', decimal1=5.12)

    app_settings.STR_ATTR_FMT = '{name}={value.title__round}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Abc, decimal1={}>'.format(round_expected)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.round__title}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Abc, decimal1={}>'.format(round_expected)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_str_fmt_chain():
    item = FmtDefault.objects.create(name1='abcdefghij', decimal1=5.12)

    app_settings.STR_ATTR_FMT = '{name}={value.title__round__replace_a_f}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Abcdefghij, decimal1={}>'.format(round_expected)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.title__round__replace_A_f}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=fbcdefghij, decimal1={}>'.format(round_expected)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.replace_a_f__round__title}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Fbcdefghij, decimal1={}>'.format(round_expected)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_str_fmt_ellipsis():
    item = FmtDefault.objects.create(name1='a' * 200, decimal1=5.12)

    app_settings.STR_ATTR_FMT = '{name}={value.ellipsis_10__round}'
    try:
        assert str(item) == (
            '<FmtDefault: id=1, name1={}..., decimal1={}>'.format('a' * 7, round_expected))
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    item = FmtDefault.objects.create(name1='a' * 200, decimal1=5.12)

    app_settings.STR_ATTR_FMT = '{name}={value.round__ellipsis_10}'
    try:
        assert str(item) == (
            '<FmtDefault: id=2, name1={}..., decimal1={}>'.format('a' * 7, round_expected))
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_repr_fmt_ellipsis():
    item = FmtDefault.objects.create(name1='a' * 200, decimal1=5.12)

    app_settings.REPR_ATTR_FMT = '{name}={value.ellipsis_10__round!r}'
    try:
        assert repr(item) == (
            "FmtDefault(id=1, name1='{}...', decimal1={})".format('a' * 7, round_expected))
    finally:
        app_settings.REPR_ATTR_FMT = '{name}={value!r}'

    item = FmtDefault.objects.create(name1='a' * 200, decimal1=5.12)

    app_settings.REPR_ATTR_FMT = '{name}={value.round__ellipsis_10!r}'
    try:
        assert repr(item) == (
            "FmtDefault(id=2, name1='{}...', decimal1={})".format('a' * 7, round_expected))
    finally:
        app_settings.REPR_ATTR_FMT = '{name}={value!r}'
