from pytest_djangoapp import configure_djangoapp_plugin

settings = {
    'DEBUG': True,
    'DUNDER_AUTO': False,
}

pytest_plugins = configure_djangoapp_plugin(settings)
