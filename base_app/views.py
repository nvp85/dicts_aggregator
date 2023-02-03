from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.urls import reverse
import base_app.search
from base_app.models import SearchHistoryRecord
from base_app.forms import SearchForm


def homepage(request):
    search_form = SearchForm()
    user = request.user
    search_records = SearchHistoryRecord.objects.filter(user=user).values('word')
    return render(request, 'home.html', context={'search_form': search_form, 'search_records': search_records})


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
    user = request.user
    if request.POST:
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_record = search_form.save(commit=False)
            try:
                old_record = SearchHistoryRecord.objects.get(word=search_record.word, user=user)
            except SearchHistoryRecord.DoesNotExist:
                old_record = None
            search_record.user = user
            dicts = search_form.cleaned_data['dicts']
            for dict in dicts:
                dict = getattr(base_app.search, dict+'Dictionary')()
                dict_result = dict.search(search_record.word)
                if dict_result:
                    result.append(dict_result)
            if old_record:
                old_record.count = 1 + old_record.count
                old_record.save()
            else:
                search_form.save()
    else:
        search_form = SearchForm()
    search_records = SearchHistoryRecord.objects.filter(user=user).order_by('last_date').values('word')
    return render(request, 'search.html', {'search_form': search_form, 'result': result, 'search_records': search_records})
