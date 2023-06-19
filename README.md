# Django Tegro Money

[![Build Status](https://img.shields.io/pypi/pyversions/django-tegro-money)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/pypi/v/django-tegro-money)](https://pypi.org/project/django-tegro-money/)

Django API connector for [Tegro Money's HTTP APIs](https://tegro.money/docs/).

## Table of Contents

- [About](#about)
- [Development](#development)
- [Installation](#installation)
- [Usage](#usage)

## About
Put simply, `django-tegro-money` is the lightweight one-stop-shop module for the [Tegro Money's HTTP APIs](https://tegro.money/docs/).

It was designed with the following vision in mind:

> I wanted to build my own Django-dedicated connector to Tegro Money the system for accepting online payments with very little external resources. The goal of the connector is to provide entrepreneurs and developers with an easy-to-use high-performing module that has an active issue and discussion board leading to consistent improvements.

## Development
`Tegro Money` is being actively developed, and new API changes should arrive on `Tegro Money` very quickly. `Tegro Money` uses `requests` for its methods, alongside other built-in modules. Anyone is welcome to branch/fork the repository and add their own upgrades. If you think you've made substantial improvements to the module, submit a pull request, so we'll gladly take a look.

## Installation
`django-tegro-money` requires Django 3.2 or higher and Python 3.8 or higher.

The module can be installed manually or via [PyPI](https://pypi.org/project/pybit/) with `pip`:
```
pip install django-tegro-money
```
Add `django-tegro-money` to the `INSTALLED_APPS` in your `settings.py`:
```python
INSTALLED_APPS = [
    ...,
    'django_tegro_money',
    ...,
]
```
Add an entry to your `urls.py`:
```python
urlpatterns += [
    path('', include('django_tegro_money.urls')),
]
```
Run migration:
```
python manage.py migrate
```

## Usage
The first before using `django-tegro-money` you must register with `Tegro.Money`. [Do it ...](https://tegro.money/my/register/).

Then you must add a store. [Do it ...](https://tegro.money/my/add-shop/).

You can find more information [here](https://tegro.money/docs/en/begin/register/).

NOTICE! Specify `payment_status` as `Notification URL`:
```
Notification URL
URL: https://<your_site>/payment_status/
```

Add secret parameters of your store (`Shop ID`, `Secret KEY` and `API KEY`) in your `settings.py` (it's best to store secret settings locally):

```python
TEGRO_MONEY_SHOP_ID = <Shop ID>
TEGRO_MONEY_SECRET_KEY = <Secret KEY>
TEGRO_MONEY_API_KEY = <API KEY>
```
Create `TegroMoney` object:
```python
tegro_money = TegroMoney(log_requests=True, timeout=10, max_retries=3, retry_delay=3)
```
Just use `TegroMoney` methods:
```python
# Create order and get payment

# Get data (you can get data from your form)
data = {
  "amount": 1200,
  "currency": "RUB",
  "order_id": "test order",
  "payment_system": 5,
  "fields": {
    "email": "user@email.ru",
    "phone": "79111231212"
  },
  "receipt": {
    "items": [
      {
        "name": "test item 1",
        "count": 1,
        "price": 600
      },
      {
        "name": "test item 2",
        "count": 1,
        "price": 600
      }
    ]
  }
}

# Send request to Tergo Money
try:
    result = tegro_money.create_order(**data)
    
    # Save order id from tegro money for future use
    tegro_money_order_id = result['data']['id']
    
    # Redirect to payment page
    return redirect(result['data']['url'])
except:
    pass
```
