from django.urls import path

from . import views

urlpatterns = [
    path('', views.offer, name="trade_offers_offer"),
    path('create', views.create, name="trade_offers_create")
]