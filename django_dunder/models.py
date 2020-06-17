from .app_settings import _ANY_REGISTER

# Start registration of models appearing after this app in INSTALLED_APPS
if _ANY_REGISTER:
    from ._register import _dunder_applied_counter
else:
    _dunder_applied_counter = 0

__all__ = [
    '_dunder_applied_counter',
]

