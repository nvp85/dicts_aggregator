from django.forms import ModelForm, ChoiceField
from base_app.models import SearchHistoryRecord

DICTS_CHOICES = (
    ('yandex', 'Yandex Dictionary'),
    ('oxford', 'Oxford Dictionary'),
)


class SearchForm(ModelForm):
    dicts = ChoiceField(choices=DICTS_CHOICES)
    class Meta:
        model = SearchHistoryRecord
        fields = ['word',]
