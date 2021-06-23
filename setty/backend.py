import logging
from typing import Optional, Iterable, Any, TypeVar

from django.conf import settings
from django.core.cache import cache
from setty.exceptions import SettingDoesNotExistError

from .models import SettySettings

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DatabaseBackend:
    """
    The simple DatabaseBackend is backed by the Django model storing these settings
    """

    def get_all(self, app_name: Optional[str] = None) -> Iterable:
        if app_name:
            return SettySettings.objects.filter(app_name=app_name).all()
        return SettySettings.objects.all()

    def get(self, name: str) -> Any:
        try:
            setting = SettySettings.objects.get(name=name).value
        except SettySettings.DoesNotExist:
            setting = getattr(settings, 'SETTY_NOT_FOUND_VALUE', None)

        return setting

    def set(self, name: str, value: T) -> T:
        updated_count = SettySettings.objects.filter(name=name).update(value=value)
        if not updated_count:
            raise SettingDoesNotExistError(
                f'Error setting value for {name} - ' f'this setting does not exist in the database!'
            )
        return value


class CacheBackend(DatabaseBackend):
    """
    CacheBackend uses the Django cache setup to cache values instead of accessing the
    database on each get call.
    """

    def get(self, name: str) -> Any:
        cache_key = self._make_cache_key(name)
        setting_value = cache.get(cache_key, '__expired__')
        if setting_value != '__expired__':
            logger.debug('From Cache:', setting_value)
            return setting_value
        logger.debug('From Database:', setting_value)
        return self._retrieve_and_cache_setting(name)

    def _retrieve_and_cache_setting(self, name: str) -> Any:
        value = super().get(name)
        self.set_in_cache(name, value)
        return value

    def set(self, name: str, value: T) -> T:
        super().set(name, value)
        self.set_in_cache(name, value)
        return value

    def set_in_cache(self, name: str, value: Any) -> None:
        cache.set(self._make_cache_key(name), value, getattr(settings, 'SETTY_CACHE_TTL', 3600))

    def load_all_settings_into_cache(self) -> None:
        for setting in self.get_all():
            self.set_in_cache(setting.name, setting.value)

    @staticmethod
    def _make_cache_key(name: str) -> str:
        return ':'.join([getattr(settings, 'SETTY_CACHE_PREFIX', '_dyn_settings_'), name])
