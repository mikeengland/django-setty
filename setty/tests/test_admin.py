from unittest.mock import patch

from django.forms import fields
from django.test import TestCase, override_settings
from setty.admin import SettingsForm
from setty.models import SettySettings


@override_settings(SETTY_BACKEND='DatabaseBackend')
class AdminSettingsFormTests(TestCase):
    def _validate_invalid_form(self, data_type):
        form = SettingsForm(data={'name': 'mysetting', 'type': data_type, 'value_unpacked': 'invalid'})
        self.assertFalse(form.is_valid())

    def _save_form(self, data_type, value, name='mysetting'):
        form = SettingsForm(data={'name': name, 'type': data_type, 'value_unpacked': value})
        form.save()

    def test_form_is_not_valid_if_dict_serialization_fails(self):
        self._validate_invalid_form('dict')

    def test_form_is_not_valid_if_list_serialization_fails(self):
        self._validate_invalid_form('list')

    def test_form_is_not_valid_if_bool_serialization_fails(self):
        self._validate_invalid_form('bool')

    def test_form_is_not_valid_if_integer_serialization_fails(self):
        self._validate_invalid_form('integer')

    def test_form_is_not_valid_if_float_serialization_fails(self):
        self._validate_invalid_form('float')

    def test_form_has_name_field(self):
        self.assertIsInstance(SettingsForm({}).fields['name'], fields.CharField)

    def test_form_has_type_field(self):
        self.assertIsInstance(SettingsForm({}).fields['type'], fields.ChoiceField)

    def test_form_has_value_unpacked_field(self):
        self.assertIsInstance(SettingsForm({}).fields['value_unpacked'], fields.CharField)

    def test_form_saves_True_boolean_correctly(self):
        for val in ('y', 'yes', 't', 'true', 'on', '1'):
            with self.subTest('with {} value'.format(val)):
                self._save_form('bool', val, name=val)
                self.assertEquals(SettySettings.objects.get(name=val).value, True)

    def test_form_saves_False_boolean_correctly(self):
        for val in ('n', 'no', 'f', 'false', 'off', '0'):
            with self.subTest('with {} value'.format(val)):
                self._save_form('bool', val, name=val)
                self.assertEquals(SettySettings.objects.get(name=val).value, False)

    def test_form_saves_float_correctly(self):
        self._save_form('float', 1.234)

        self.assertEquals(SettySettings.objects.get(name='mysetting').value, 1.234)

    def test_form_saves_integer_correctly(self):
        self._save_form('integer', 12)

        self.assertEquals(SettySettings.objects.get(name='mysetting').value, 12)

    def test_form_saves_string_correctly(self):
        self._save_form('string', 'my string')

        self.assertEquals(SettySettings.objects.get(name='mysetting').value, 'my string')

    def test_form_saves_dict_correctly(self):
        self._save_form('dict', '{"a": 1, "b": 2}')

        self.assertEquals(SettySettings.objects.get(name='mysetting').value, {'a': 1, 'b': 2})

    def test_form_saves_list_correctly(self):
        self._save_form('list', '[1, 2, 3, 4]')

        self.assertEquals(SettySettings.objects.get(name='mysetting').value, [1, 2, 3, 4])

    @patch('setty.backend.cache')
    def test_save_calls_cache_set_with_correct_args_if_cachebackend_not_used(self, mock_cache):
        self._save_form('list', '[1, 2, 3, 4]')

        mock_cache.assert_not_called()

    @override_settings(SETTY_BACKEND='CacheBackend')
    @patch('setty.backend.cache')
    def test_save_calls_cache_set_with_correct_args_if_cachebackend_used(self, mock_cache):
        self._save_form('list', '[1, 2, 3, 4]')

        mock_cache.set.assert_called_once_with('_dyn_settings_:mysetting', [1, 2, 3, 4], 3600)
