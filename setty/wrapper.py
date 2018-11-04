from importlib import import_module

from django.conf import settings

from .exceptions import InvalidConfigurationError


def _load_backend_class():
    backend = getattr(settings, 'SETTY_BACKEND', None)
    if backend is None:
        raise InvalidConfigurationError('The SETTY_BACKEND setting needs to be defined.')

    return getattr(import_module('setty.backend'), backend)()


class Settings:
    """
    Wrapper class used for accessing/updating setty settings
    """
    _backend = _load_backend_class()

    def __getattr__(self, key):
        return self._backend.get(key)

    def __setattr__(self, key, value):
        self._backend.set(key, value)

    def __dir__(self):
        return [setting.name for setting in self._backend.get_all()]
