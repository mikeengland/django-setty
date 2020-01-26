from unittest.mock import patch, call

from django.test import TestCase
from django.test import override_settings
from setty.backend import DatabaseBackend, CacheBackend
from setty.exceptions import SettingDoesNotExistError
from setty.models import SettySettings


class BaseBackendTestsMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        SettySettings.objects.create(name='mybool', type='bool', value=True)
        SettySettings.objects.create(name='mydict', type='dict', value={'a': 1, 'b': 2})
        SettySettings.objects.create(name='myfloat', type='float', value=3.142)
        SettySettings.objects.create(name='myinteger', type='integer', value=123)
        SettySettings.objects.create(name='mylist', type='list', value=[1, 2, 3, 4])
        SettySettings.objects.create(name='mystring', type='string', value='test_string')


@override_settings(SETTY_BACKEND='DatabaseBackend')
class DatabaseBackendTests(BaseBackendTestsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.all_settings = SettySettings.objects.all()
        cls.backend = DatabaseBackend()

    def test_get_all_returns_all_settings(self):
        settings = self.backend.get_all()
        self.assertEqual(list(settings), list(self.all_settings))

    def test_missing_item_returns_none_if_not_found_setting_undefined(self):
        self.assertIsNone(self.backend.get('missing'))

    @override_settings(SETTY_NOT_FOUND_VALUE='__notfound__')
    def test_missing_item_returns_not_found_setting_value_if_not_found_setting_defined(self):
        self.assertEqual(self.backend.get('missing'), '__notfound__')

    def test_get_returns_bool(self):
        self.assertEqual(self.backend.get('mybool'), True)

    def test_get_returns_float(self):
        self.assertEqual(self.backend.get('myfloat'), 3.142)

    def test_get_returns_integer(self):
        self.assertEqual(self.backend.get('myinteger'), 123)

    def test_get_returns_string(self):
        self.assertEqual(self.backend.get('mystring'), 'test_string')

    def test_get_returns_list(self):
        self.assertEqual(self.backend.get('mylist'), [1, 2, 3, 4])

    def test_get_returns_dict(self):
        self.assertEqual(self.backend.get('mydict'), {'a': 1, 'b': 2})

    def test_set_invalid_setting_raises_exception(self):
        with self.assertRaisesMessage(
            SettingDoesNotExistError,
            f'Error setting value for invalid - ' f'this setting does not exist in the database!',
        ):
            self.backend.set('invalid', True)

    def test_set_updates_bool(self):
        self.backend.set('mybool', False)
        self.assertEqual(SettySettings.objects.get(name='mybool').value, False)

    def test_set_updates_float(self):
        self.backend.set('myfloat', 2.1)
        self.assertEqual(SettySettings.objects.get(name='myfloat').value, 2.1)

    def test_set_updates_integer(self):
        self.backend.set('myinteger', 111)
        self.assertEqual(SettySettings.objects.get(name='myinteger').value, 111)

    def test_set_updates_string(self):
        self.backend.set('mystring', 'abcde')
        self.assertEqual(SettySettings.objects.get(name='mystring').value, 'abcde')

    def test_set_updates_list(self):
        self.backend.set('mylist', ['a', 'b'])
        self.assertEqual(SettySettings.objects.get(name='mylist').value, ['a', 'b'])

    def test_set_updates_dict(self):
        self.backend.set('mydict', {'a': 1, 'b': 2})
        self.assertEqual(SettySettings.objects.get(name='mydict').value, {'a': 1, 'b': 2})


@override_settings(SETTY_BACKEND='CacheBackend', SETTY_CACHE_PREFIX='_mock_key_')
@patch('setty.backend.cache')
class CacheBackendTest(BaseBackendTestsMixin, TestCase):
    def setUp(self):
        self.backend = CacheBackend()

    def test_load_all_settings_into_cache_calls_set_for_all_settings(self, mock_cache):
        self.backend.load_all_settings_into_cache()

        mock_cache.set.assert_has_calls(
            [
                call('_mock_key_:mybool', True, 3600),
                call('_mock_key_:mydict', {'a': 1, 'b': 2}, 3600),
                call('_mock_key_:myfloat', 3.142, 3600),
                call('_mock_key_:myinteger', 123, 3600),
                call('_mock_key_:mylist', [1, 2, 3, 4], 3600),
                call('_mock_key_:mystring', 'test_string', 3600),
            ]
        )

    @override_settings(SETTY_CACHE_TTL=5)
    def test_set_method(self, mock_cache):
        self.backend.set('mybool', False)

        with self.subTest('updates database value'):
            self.assertEqual(SettySettings.objects.get(name='mybool').value, False)

        with self.subTest('uses ttl setting if set'):
            mock_cache.set.assert_called_once_with('_mock_key_:mybool', False, 5)

    def test_get_calls_cache_get_method_with_expected_cache_key(self, mock_cache):
        self.backend.get('test')

        mock_cache.get.assert_called_once_with('_mock_key_:test', '__expired__')

    def test_value_returned_if_key_found_in_cache(self, mock_cache):
        mock_cache.get.return_value = True

        result = self.backend.get('test')

        self.assertEqual(result, True)

    def test_value_not_found_in_cache(self, mock_cache):
        # Django cache framework will return a given value (we specify this) if if nothing is found
        mock_cache.get.return_value = '__expired__'
        result = self.backend.get('mylist')

        with self.subTest('cache set called'):
            mock_cache.set.assert_called_once_with('_mock_key_:mylist', [1, 2, 3, 4], 3600)

        with self.subTest('correct value returned'):
            self.assertEqual(result, [1, 2, 3, 4])
