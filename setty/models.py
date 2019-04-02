from django.db import models
from picklefield import PickledObjectField


class TypeChoices:
    BOOL = 'bool'
    DICT = 'dict'
    FLOAT = 'float'
    INTEGER = 'integer'
    LIST = 'list'
    STRING = 'string'

    ALL_CHOICES = (
        (BOOL, 'Bool'),
        (DICT, 'Dict'),
        (FLOAT, 'Float'),
        (INTEGER, 'Integer'),
        (LIST, 'List'),
        (STRING, 'String'),
    )


class SettySettings(models.Model):
    # 190 chars or there is a key length error in mysql 5.6
    name = models.CharField(max_length=190, primary_key=True)
    value = PickledObjectField()
    type = models.CharField(max_length=8, choices=TypeChoices.ALL_CHOICES)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    @property
    def value_unpacked(self):
        return str(self.value)

    @value_unpacked.setter
    def value_unpacked(self, value):
        self.value = value

    def __str__(self):
        return '{}={}'.format(self.name, self.value_unpacked)

    class Meta:
        verbose_name = 'Setty Settings'
        verbose_name_plural = 'Setty Settings'
