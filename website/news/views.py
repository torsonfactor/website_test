from django.shortcuts import render, redirect

from .forms import ChattForm
from .models import Chatt


def news(request):
    news = Chatt.objects.all()
    data = {
        "news": news,
    }
    return render(request, "news/news.html", context=data)


def create(request):
    error = ""
    if request.method == "POST":
        form = ChattForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('news')
        else:
            error = "Форма заполнена неверно"

    form = ChattForm()

    data = {
        'form': form,
        'error': error,
    }

    return render(request, "news/create.html", data)