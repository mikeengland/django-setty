from unittest.mock import patch

from django.test import TestCase, override_settings

from setty.backend import DatabaseBackend, CacheBackend
from setty.exceptions import InvalidConfigurationError
from setty.models import SettySettings as SettySettingsModel
from setty.wrapper import Settings, _load_backend_class


class WrapperTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        SettySettingsModel.objects.create(name='mybool', type='bool', value=True)
        SettySettingsModel.objects.create(name='mydict', type='dict', value={'a': 1, 'b': 2})

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = Settings()

    def test_dir_returns_all_settings(self):
        result = dir(Settings())

        self.assertEqual(result, ['mybool', 'mydict'])

    @patch.object(DatabaseBackend, 'get')
    def test_getattr_calls_backend_get_with_correct_args(self, mock_get):
        self.settings.foo

        mock_get.assert_called_once_with('foo')

    @patch.object(DatabaseBackend, 'set')
    def test_setattr_calls_backend_get_with_correct_args(self, mock_set):
        self.settings.foo = 'bar'

        mock_set.assert_called_once_with('foo', 'bar')


class LoadBackendTests(TestCase):
    @override_settings(SETTY_BACKEND='DatabaseBackend')
    def test_load_database_backend_returns_correct_class(self):
        klass = _load_backend_class()

        self.assertIsInstance(klass, DatabaseBackend)

    @override_settings(SETTY_BACKEND='CacheBackend')
    def test_load_cache_backend_returns_correct_class(self):
        klass = _load_backend_class()

        self.assertIsInstance(klass, CacheBackend)

    @override_settings(SETTY_BACKEND=None)
    def test_backend_setting_undefined_raises_InvalidConfigurationError_exception(self):
        with self.assertRaises(InvalidConfigurationError):
            _load_backend_class()
