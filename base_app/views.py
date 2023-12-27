from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.db import transaction   
from base_app.models import SearchHistoryRecord
from base_app.forms import SearchForm, DICTS_CHOICES
from base_app.search import search
from django.core.cache import cache


def homepage(request):
    search_form = SearchForm()
    user = request.user
    search_records = []
    if user.is_authenticated:
        search_records = SearchHistoryRecord.objects.filter(user=user).order_by('-last_date').values('word')[:10]        
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
    word = None
    search_form = SearchForm()
    if request.method == 'GET' and 'word' in request.GET:
        word = request.GET.get('word')
        dicts = []
        for d in DICTS_CHOICES:
            d = d[0]
            if cache.get(d.lower()+":"+word):
                dicts.append(d)
        if not dicts:
            dicts = [d[0] for d in DICTS_CHOICES]
        search_form.fields['dicts'].initial = dicts
    elif request.POST:
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            word = search_form.cleaned_data['word']
            dicts = search_form.cleaned_data['dicts']
    if word is not None:
        result = search(word, dicts)
        if user.is_authenticated and result.get('success', False):
            with transaction.atomic():
                old_record = SearchHistoryRecord.objects.select_for_update().filter(word=word, user=user)[:1]
                if old_record:
                    old_record = old_record.get()
                    old_record.count = 1 + old_record.count
                    old_record.save()
                else:
                    search_record = SearchHistoryRecord.objects.create(word=word,user=user)
                    search_record.save()
    search_records = []
    if user.is_authenticated:
        search_records = SearchHistoryRecord.objects.filter(user=user).order_by('-last_date').values('word')[:10]        
    return render(request, 'search.html', {'search_form': search_form, 'result': result, 'search_records': search_records})

