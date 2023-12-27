# dicts_aggregator

It's a web application that provides a unified interface for word lookup across multiple online dictionaries, using their APIs. Currently, it supports 3 dictionaries: Oxford, Yandex, and Free Dictionary. Crafted with Django and powered by PostgreSQL for my own use as a language learning tool.

## Techmologies
Python 3.7+
Django 4.2


## Launch locally with Docker
* Clone the repository
* Create .env file
* run in the project directory the following commands:
```bash
docker compose up -d 
docker exec web python manage.py migrate --noinput
docker exec web python manage.py createcachetable
```
## Launch locally without Docker
Prerequisites: Postgresql running on the port 5432 (default port).

To run this project locally implement the following steps:

* Clone the repository

* Set up and activate a virtual environment

* Install requirements.txt

* Create a database "dicts_aggregator" and a role "dicts_aggregator" with the login option.

* The project uses the package django-environ to separate secrets from the code. Generate a new secret key. Create .env file and put the secret key and your Postgres credentials in it. Exemplary content of an .env file:
```
DEBUG=on
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://dicts_aggregator@127.0.0.1:5432/dicts_aggregator
YANDEX_API_KEY=api_key
OXFORD_APP_ID=api_id
OXFORD_APP_ID=api_key
```

* Make migrations
```bash
$ python manage.py makemigrations
$ python manage.py migrate
```
* Create a cache table
```bash
$ python manage.py createcachetable
```
* Run the development web server
```
$ python manage.py runserver
```
