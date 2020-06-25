import datetime

from django.db import models

try:
    from datatype_tools.lib import *  # noqa
    datatype_tools = True
except ImportError as e:
    datatype_tools = False

from django_dunder import app_settings
from django_dunder.mixins import DunderModel
from django_dunder._formatter import _get_one_invoke
from django_dunder._register import PY3

from django_fake_model import models as f

if PY3:
    round_expected_id_alt = '1'
    if datatype_tools:
        round_expected_float = '5.13'
    else:
        round_expected_float = '5'
else:
    round_expected_id_alt = '1.0'  # FIXME!
    round_expected_float = '5.0'


def test_invoke_parse_brackets():
    name, args, remainder = _get_one_invoke('one()')
    assert (name, tuple(args), remainder) == ('one', tuple(), None)

    name, args, remainder = _get_one_invoke('one')
    assert (name, tuple(args), remainder) == ('one', tuple(), None)

    name, args, remainder = _get_one_invoke('one(a)')
    assert (name, tuple(args), remainder) == ('one', tuple(['a']), None)

    name, args, remainder = _get_one_invoke('one(1)')
    assert (name, tuple(args), remainder) == ('one', tuple([1]), None)

    name, args, remainder = _get_one_invoke('one(a, 1)')
    assert (name, tuple(args), remainder) == ('one', tuple(['a', 1]), None)

    name, args, remainder = _get_one_invoke('one().two()')
    assert (name, tuple(args), remainder) == ('one', tuple(), 'two()')

    name, args, remainder = _get_one_invoke('one(a).two(b)')
    assert (name, tuple(args), remainder) == ('one', tuple(['a']), 'two(b)')

    name, args, remainder = _get_one_invoke('one(a). two(b)')
    assert (name, tuple(args), remainder) == ('one', tuple(['a']), 'two(b)')

    name, args, remainder = _get_one_invoke('one(a), two(b)')
    assert (name, tuple(args), remainder) == ('one', tuple(['a']), 'two(b)')

    name, args, remainder = _get_one_invoke('one(a)__two(b)')
    assert (name, tuple(args), remainder) == ('one', tuple(['a']), 'two(b)')


def test_invoke_parse_underscore():
    name, args, remainder = _get_one_invoke('one_a')
    assert (name, tuple(args), remainder) == ('one', tuple(['a']), None)

    name, args, remainder = _get_one_invoke('one__two')
    assert (name, tuple(args), remainder) == ('one', tuple(), 'two')

    name, args, remainder = _get_one_invoke('one__two')
    assert (name, tuple(args), remainder) == ('one', tuple(), 'two')

    name, args, remainder = _get_one_invoke('one_a__two_b')
    assert (name, tuple(args), remainder) == ('one', tuple(['a']), 'two_b')

    name, args, remainder = _get_one_invoke('one_a_1__two_b')
    assert (name, tuple(args), remainder) == ('one', tuple(['a', 1]), 'two_b')


def test_invoke_parse_mixed():
    name, args, remainder = _get_one_invoke('one_a__two(b)')
    assert (name, tuple(args), remainder) == ('one', tuple(['a']), 'two(b)')

    name, args, remainder = _get_one_invoke('one(a)__two_b')
    assert (name, tuple(args), remainder) == ('one', tuple(['a']), 'two_b')


class FmtDefault(DunderModel, f.FakeModel):
    name1 = models.TextField(null=True, blank=True)
    name2 = models.TextField(null=True, blank=True)
    decimal1 = models.DecimalField(null=True, blank=True, decimal_places=3)
    date1 = models.DateField(null=True, blank=True)


@FmtDefault.fake_me
def test_fmt_str_item():
    item = FmtDefault.objects.create(name1='1234567890')

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
def test_fmt_str_round():
    item = FmtDefault.objects.create(name1='abc', decimal1=5.129)

    app_settings.STR_ATTR_FMT = '{name}={value.round}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=abc, decimal1={}>'.format(
            round_expected_float)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.round(1)}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=abc, decimal1=5.1>'
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_fmt_str_title():
    item = FmtDefault.objects.create(name1='abc')

    app_settings.STR_ATTR_FMT = '{name}={value.title}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Abc>'
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_fmt_str_title_func():
    item = FmtDefault.objects.create(name1='abc')

    app_settings.STR_ATTR_FMT = '{name}={value.title()}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Abc>'
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_fmt_str_multi():
    item = FmtDefault.objects.create(name1='abc', decimal1=5.129)

    app_settings.STR_ATTR_FMT = '{name}={value.title__round}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Abc, decimal1={}>'.format(
            round_expected_float)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.round__title}'
    try:
        assert str(item) == '<FmtDefault: id={}, name1=Abc, decimal1={}>'.format(
            round_expected_id_alt, round_expected_float)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.round()__title()}'
    try:
        assert str(item) == '<FmtDefault: id={}, name1=Abc, decimal1={}>'.format(
            round_expected_id_alt, round_expected_float)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.round(), title()}'
    try:
        assert str(item) == '<FmtDefault: id={}, name1=Abc, decimal1={}>'.format(
            round_expected_id_alt, round_expected_float)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_fmt_str_multi_dot():
    item = FmtDefault.objects.create(name1='abc', decimal1=5.129)

    app_settings.STR_ATTR_FMT = '{name}={value.round().title()}'
    try:
        assert str(item) == '<FmtDefault: id=1, name1=Abc, decimal1={}>'.format(
            round_expected_float)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_fmt_str_chain():
    item = FmtDefault.objects.create(name1='abcdefghij', decimal1=5.129)

    app_settings.STR_ATTR_FMT = '{name}={value.title__round__replace_a_f}'
    try:
        assert str(item) == '<FmtDefault: id={}, name1=Abcdefghij, decimal1={}>'.format(
            round_expected_id_alt, round_expected_float)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.title__round__replace_A_f}'
    try:
        assert str(item) == '<FmtDefault: id={}, name1=fbcdefghij, decimal1={}>'.format(
            round_expected_id_alt, round_expected_float)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.replace_a_f__round__title}'
    try:
        assert str(item) == '<FmtDefault: id={}, name1=Fbcdefghij, decimal1={}>'.format(
            round_expected_id_alt, round_expected_float)
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_fmt_str_ellipsis():
    item = FmtDefault.objects.create(name1='a' * 200, decimal1=5.129)

    app_settings.STR_ATTR_FMT = '{name}={value.ellipsis_10__round}'
    try:
        assert str(item) == (
            '<FmtDefault: id=1, name1={}..., decimal1={}>'.format(
                'a' * 7, round_expected_float))
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'

    app_settings.STR_ATTR_FMT = '{name}={value.round__ellipsis_10}'
    try:
        assert str(item) == (
            '<FmtDefault: id={}, name1={}..., decimal1={}>'.format(
                round_expected_id_alt, 'a' * 7, round_expected_float))
    finally:
        app_settings.STR_ATTR_FMT = '{name}={value}'


@FmtDefault.fake_me
def test_fmt_repr_ellipsis():
    item = FmtDefault.objects.create(name1='a' * 200, decimal1=5.129)

    app_settings.REPR_ATTR_FMT = '{name}={value.ellipsis_10__round!r}'
    try:
        assert repr(item) == (
            "FmtDefault(id=1, name1='{}...', decimal1={})".format(
                'a' * 7, round_expected_float))
    finally:
        app_settings.REPR_ATTR_FMT = '{name}={value!r}'

    app_settings.REPR_ATTR_FMT = '{name}={value.round__ellipsis_10!r}'
    try:
        assert repr(item) == (
            "FmtDefault(id={}, name1='{}...', decimal1={})".format(
                round_expected_id_alt, 'a' * 7, round_expected_float))
    finally:
        app_settings.REPR_ATTR_FMT = '{name}={value!r}'


if datatype_tools:
    @FmtDefault.fake_me
    def test_fmt_str_datatype_tools():
        item = FmtDefault.objects.create(name1='a', date1=datetime.date.today())

        app_settings.STR_ATTR_FMT = '{name}={value.title__format_date(yyyymmdd)}'
        try:
            assert str(item) == (
                '<FmtDefault: id=1, name1=A, date1={year}-{month:02d}-{day:02d}>'.format(
                    day=item.date1.day, month=item.date1.month, year=item.date1.year))
        finally:
            app_settings.STR_ATTR_FMT = '{name}={value}'
