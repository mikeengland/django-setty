django-setty
==============

Django-Setty allows you to dynamically change settings inside the Django Admin Console.
The app provides both a database and a cache backend for storing and retrieving your settings.

[![Build Status](https://travis-ci.org/mikeengland/django-setty.svg?branch=master)](https://travis-ci.org/mikeengland/django-setty)
[![Coverage Status](https://coveralls.io/repos/github/mikeengland/django-setty/badge.svg?branch=master)](https://coveralls.io/github/mikeengland/django-setty?branch=master)

Requirements
------------
* Python 3.6+
* Django 1.11+

Continuous integration currently tests Django v1.11, v2.0, v2.1 and master.

Installation
------------
```
pip install setty
```

Django Configuration
--------------------
Add `setty` to the list of INSTALLED_APPS in your Django settings:

```
INSTALLED_APPS = [
    ...
    'setty'
]
```

Create the Setty database table by running

```
python manage.py migrate
```

Specify the backend to use using the `SETTY_BACKEND` setting. 
The valid backend values are `'DatabaseBackend'` and `'CacheBackend'`.

`'DatabaseBackend'` always accesses the database when retrieving settings.

`'CacheBackend'` only accesses the database if the item is not in the cache, and caches the value once retrieved.

Define the length of time settings should be cached for using the SETTY_CACHE_TTL setting. The default cache TTL is
one hour.

```python
SETTY_BACKEND = 'CacheBackend'
SETTY_CACHE_TTL = 60  # 60 seconds
```

Usage Examples
--------------
Open the Django admin console at <url>/admin and open `Setty Settings`.
Here, you will see the list of all settings defined in Setty.

To add a new setting, click the `add` button. 

Enter the setting name, type (String, Integer, Float, Boolean, List, Dictionary)
and the value. Note, the List and Dict data type expect the data to be in the JSON format e.g.
`{"a": 1, "b": 2}` and `[1, 2, 3]`.

Once settings have been created, you will be able to access these in your code.
```python
from setty import config

assert config.my_integer == 10

```
If the setting does not exist in the database, the value defined in the setting `SETTY_NOT_FOUND_VALUE` will be used.
If this is not set, `None` will be returned.

Setty can be used inside Django templates by adding 'setty.context_processors.setty_settings' to the
`TEMPLATE_CONTEXT_PROCESSORS` setting and accessing it via the `setty` key.

The value of a setting can also be updated by using the syntax:
```python
from setty import config

config.my_integer = 100

```
Note: Only settings that already exist in the database can be updated. New settings cannot be added this way.

Loading all settings into the Cache
------------------------------------
If you use the `CacheBackend` backend, you can easily load all settings into the Cache. This is useful if you want to
cache all settings when you start up your app.

```python
from setty.backend import CacheBackend
CacheBackend().load_all_settings_into_cache()
```

Similar Projects
-----------------
* This project was inspired by Django Constance
https://github.com/jazzband/django-constance