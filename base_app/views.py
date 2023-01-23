from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.urls import reverse
from base_app.search import OxfordDictionary, YandexDictionary
from base_app.models import SearchHistoryRecord
from base_app.forms import SearchForm


def homepage(request):
    search_form = SearchForm()
    return render(request, 'home.html', context={'search_form': search_form})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('home'))
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form,})


def search_view(request):
    result = []
    if request.POST:
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_record = search_form.save(commit=False)
            dicts = request.get['dicts']
            oxford = OxfordDictionary()
            yandex = YandexDictionary()
            oxford_result = oxford.search(search_record.word)
            if oxford_result:
                result.append(oxford_result)
            yandex_result = yandex.search(search_record.word)
            if yandex_result:
                result.append(yandex_result)

                #form.save()
    else:
        search_form = SearchForm()
    return render(request, 'search.html', {'search_form': search_form, 'result': result})
