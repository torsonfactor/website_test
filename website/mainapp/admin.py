from django.contrib import admin
from django.contrib.sessions.models import Session
from django.forms import ModelForm

from .models import *


class SuggestionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class SexAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class CategoryAccessoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class ProductAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not self.fields['discount']:
            self.fields['sale_price'].widget.attrs.update({
                'readonly': True, 'style': 'lightgray'
            })

    def clean(self):
        if not self.cleaned_data['discount']:
            self.cleaned_data['sale_price'] = None
        return self.cleaned_data


class ProductAdmin(admin.ModelAdmin):

    change_form_template = 'mainapp/admin/admin.html'
    form = ProductAdminForm

    prepopulated_fields = {"slug": ("title",)}


class ProductAccessoriesAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not self.fields['discount']:
            self.fields['sale_price'].widget.attrs.update({
                'readonly': True, 'style': 'lightgray'
            })

    def clean(self):
        if not self.cleaned_data['discount']:
            self.cleaned_data['sale_price'] = None
        return self.cleaned_data


class ProductAccessoriesAdmin(admin.ModelAdmin):

    change_form_template = 'mainapp/admin/admin.html'
    form = ProductAccessoriesAdminForm

    prepopulated_fields = {"slug": ("title",)}


class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class BrandAccessoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Suggestion, SuggestionAdmin)
admin.site.register(NewProduct)
admin.site.register(DiscountProduct)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAccessories, ProductAccessoriesAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryAccessories, CategoryAccessoriesAdmin)
admin.site.register(Sex, SexAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(BrandAccessories, BrandAccessoriesAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Size)
admin.site.register(WishList)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Notification)
admin.site.register(Session)