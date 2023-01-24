from django.forms import ModelForm, MultipleChoiceField, CheckboxSelectMultiple
from base_app.models import SearchHistoryRecord

DICTS_CHOICES = (
    ('Yandex', 'Yandex Dictionary'),
    ('Oxford', 'Oxford Dictionary'),
)


class SearchForm(ModelForm):
    dicts = MultipleChoiceField(choices=DICTS_CHOICES, widget=CheckboxSelectMultiple)
    class Meta:
        model = SearchHistoryRecord
        fields = ['word',]
