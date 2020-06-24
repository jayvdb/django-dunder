from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from .app_settings import _ANY_REGISTER


class DunderConfig(AppConfig):
    """The default dunder configuration."""

    label = 'dunder'
    name = 'django_dunder'
    verbose_name = _('Django dunders')

    def ready(self):
        # The registration should already have been done
        if _ANY_REGISTER:
            import django_dunder._register  # noqa

        from .checks import check_py2_unicode  # noqa

    def get_models(self, *args, **kwargs):
        # The following is used to prevent the .models from being loaded
        # especially by test harnesses
        return []
