from functools import partial

from django_dunder import app_settings

from django_dunder._register import _should_force_repr


simple_should_force_repr = partial(
   _should_force_repr, model=None, has_default_func=lambda x: None)


def test_AlwaysContains():
    obj = app_settings._AlwaysContains(True)
    assert obj
    assert 'a' in obj

    obj = app_settings._AlwaysContains(False)
    # Ensure test framework is sane
    if obj:
        assert False
    else:
        assert True

    assert bool(obj) is False
    assert obj == False
    # The following does not work: 'assert obj is False'

    assert 'a' not in obj


def test_force():
    app_settings.AUTO_REPR = False
    app_settings.FORCE = True
    app_settings.FORCE_REPR = app_settings.FORCE
    app_settings.REPR_EXCLUDE = []

    app_settings._post_process()

    assert simple_should_force_repr('a')

    app_settings.REPR_EXCLUDE = ['b']
    assert not simple_should_force_repr('b')

    app_settings.FORCE = ['z']

    assert simple_should_force_repr('z')
    assert not simple_should_force_repr('b')


def test_force_repr():
    app_settings.FORCE = False
    app_settings.AUTO_REPR = False
    app_settings.REPR_EXCLUDE = []

    app_settings.FORCE_REPR = ['a']
    assert simple_should_force_repr('a')
    assert not simple_should_force_repr('b')

    app_settings.FORCE_REPR = app_settings._AlwaysContains(False)
    assert not simple_should_force_repr('a')
    assert not simple_should_force_repr('b')

    app_settings.FORCE_REPR = app_settings._AlwaysContains(True)
    assert simple_should_force_repr('a')
    assert simple_should_force_repr('b')

    app_settings.REPR_EXCLUDE = ['b']
    assert not simple_should_force_repr('b')

def test_auto_repr():
    app_settings.FORCE = False
    app_settings.FORCE_REPR = []
    app_settings.AUTO_REPR = True
    app_settings.REPR_EXCLUDE = []

    assert _should_force_repr('a', None, lambda x: True)
    assert not _should_force_repr('a', None, lambda x: False)

    app_settings.REPR_EXCLUDE = ['a']
    assert not _should_force_repr('a', None, lambda x: True)
    assert _should_force_repr('b', None, lambda x: True)
