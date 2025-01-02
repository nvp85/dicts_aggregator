from django.forms import Form, MultipleChoiceField, CheckboxSelectMultiple, CharField


DICTS_CHOICES = (
    ('Yandex', 'Yandex Dictionary'),
    #('Oxford', 'Oxford Dictionary'),
    ('free_dict', 'Free Dictionary')
)


class SearchForm(Form):
    dicts = MultipleChoiceField(choices=DICTS_CHOICES, widget=CheckboxSelectMultiple,required=True)
    word = CharField(required=True, max_length=30)

