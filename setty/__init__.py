from django.utils.functional import LazyObject


class LazyConfig(LazyObject):
    def _setup(self):
        from .wrapper import Settings
        self._wrapped = Settings()


config = LazyConfig()
