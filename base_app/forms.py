from django.forms import ModelForm, MultipleChoiceField, CheckboxSelectMultiple
from base_app.models import SearchHistoryRecord
import base_app.search

DICTS_CHOICES = (
    ('Yandex', 'Yandex Dictionary'),
    ('Oxford', 'Oxford Dictionary'),
)


class SearchForm(ModelForm):
    dicts = MultipleChoiceField(choices=DICTS_CHOICES, widget=CheckboxSelectMultiple,required=True)
    class Meta:
        model = SearchHistoryRecord
        fields = ['word',]

    def search(self):
        result = []
        word = self.cleaned_data['word']
        dicts = self.cleaned_data['dicts']
        for dict in dicts:
            dict = getattr(base_app.search, dict+'Dictionary')()
            dict_result = dict.search(word)
            if dict_result:
                result.append(dict_result)
        return result