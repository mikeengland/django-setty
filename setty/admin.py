import json
from distutils.util import strtobool

from django import forms
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
