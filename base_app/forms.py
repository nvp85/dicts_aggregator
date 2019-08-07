from django.forms import ModelForm
from base_app.models import SearchHistoryRecord


class SearchForm(ModelForm):
    class Meta:
        model = SearchHistoryRecord
        fields = ['word',]
