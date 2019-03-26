import json
from distutils.util import strtobool

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import TypeChoices, SettySettings

SERIALIZERS = {
    TypeChoices.BOOL: lambda x: strtobool(x),
    TypeChoices.DICT: lambda x: json.loads(x),
    TypeChoices.FLOAT: lambda x: float(x),
    TypeChoices.INTEGER: lambda x: int(x),
    TypeChoices.LIST: lambda x: json.loads(x),
    TypeChoices.STRING: lambda x: str(x),
}


class SettingsForm(forms.ModelForm):

    def __init__(self, *args, instance=None, **kwargs):
        # Loading the stringified value does not work without manually passing this in as initial data.
        # This is due to it being a model property. We can safely ignore the provided inital kwarg as it is merged later
        kwargs.pop('initial', None)
        initial_data = {'value_unpacked': getattr(instance, 'value_unpacked', None)}
        super().__init__(*args, initial=initial_data, instance=instance, **kwargs)

    value_unpacked = forms.CharField(label='Value',
                                     help_text='The value to store. '
                                               'List and Dict data types should be defined as JSON strings.')

    def clean_value_unpacked(self):
        serializer = SERIALIZERS[self.cleaned_data['type']]
        try:
            serialized_value = serializer(self.cleaned_data['value_unpacked'])
        except Exception as e:
            raise ValidationError('An error occurred storing the value: {}'.format(e))

        return serialized_value

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.value = self.cleaned_data['value_unpacked']
        instance.save()

        # Reset item in cache if changed in the admin
        if settings.SETTY_BACKEND == 'CacheBackend':
            from setty.backend import CacheBackend
            CacheBackend().set_in_cache(instance.name, instance.value)

        return instance

    class Meta:
        model = SettySettings
        fields = ['name', 'type', 'value_unpacked']
        read_only_fields = ['created_time', 'updated_time']

        help_texts = {
            'name': _('The setting name.'),
            'type': _('The data type of the setting being stored.'),
        }


@admin.register(SettySettings)
class SettyAdmin(admin.ModelAdmin):
    form = SettingsForm
    list_display = ['name', 'type', 'value_unpacked', 'created_time', 'updated_time']
    readonly_fields = ['created_time', 'updated_time']
