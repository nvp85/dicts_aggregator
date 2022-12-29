# dicts_aggregator

It's a web application that provides a unified interface to lookup words in several different online dictionaries using their APIs. Currently it's oxford and yandex dictionaries.

## Techmologies
Python 3.7+
Django 2.2


## Launch
Prerequisites: Postgresql running on the port 5432 (default port).

To run this project locally implement following steps:

* Clone the repository

* Set up and activate a virtual environment

* Install requirements.txt

* Create a database "dicts_aggregator" and a role "dicts_aggregator" with the login option.

* The project uses the package django-environ to separate secrets from the code. Generate new secret key. Create .env file and put the secret key and your postgres credentials in it. Exemplary content of an .env file:
```
DEBUG=on
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://dicts_aggregator@127.0.0.1:5432/dicts_aggregator
YANDEX_API_KEY=api_key
OXFORD_APP_ID=api_key
```

* Make migrations
```bash
$ python manage.py makemigrations
$ python manage.py migrate
```
* Run the development web server
```
$ python manage.py runserver
```