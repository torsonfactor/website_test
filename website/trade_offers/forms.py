from django.forms import ModelForm, TextInput, DateTimeInput, Textarea, EmailInput

from .models import Offer


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        fields = ['title', 'person_info', 'person_email', 'full_text', 'date']

        widgets = {
            "title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название:'
            }),
            "person_info": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ФИО:'
            }),
            "person_email": EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите свой Email:'
            }),
            "full_text": Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Текст статьи'
            }),
            "date": DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Дата публикации: формат 2022-01-31'
            }),
        }