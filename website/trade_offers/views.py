from django.shortcuts import render, redirect

from .forms import OfferForm
from .models import Offer


def offer(request):
    offer_ob = Offer.objects.all()
    data = {
        'offer_ob': offer_ob,
    }
    return render(request, "trade_offers/trade_offers.html", context=data)


def create(request):
    error = ''
    if request.method == "POST":
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("trade_offers_offer")
        else:
            error = 'Форма была заполнена неверно'

    form = OfferForm()

    data = {
        'form': form,
        'error': error,
    }

    return render(request, "trade_offers/create.html", data)