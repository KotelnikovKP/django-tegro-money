from django.urls import path

from django_tegro_money.views import payment_status

urlpatterns = [
    path('payment_status/', payment_status, name='payment_status'),
]
