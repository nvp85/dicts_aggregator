from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.db import transaction   
from base_app.models import SearchHistoryRecord
from base_app.forms import SearchForm


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
    if request.POST:
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            result = search_form.search()
            word = search_form.cleaned_data['word']
            if user.is_authenticated:
                with transaction.atomic():
                    old_record = SearchHistoryRecord.objects.select_for_update().filter(word=word, user=user)[:1]
                    if old_record:
                        old_record = old_record.get()
                        old_record.count = 1 + old_record.count
                        old_record.save()
                    else:
                        search_record = search_form.save(commit=False)
                        search_record.user = user
                        search_form.save()
    else:
        search_form = SearchForm()
    search_records = []
    if user.is_authenticated:
        search_records = SearchHistoryRecord.objects.filter(user=user).order_by('-last_date').values('word')[:10]        
    return render(request, 'search.html', {'search_form': search_form, 'result': result, 'search_records': search_records})
