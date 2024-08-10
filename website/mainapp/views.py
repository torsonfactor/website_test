from django import views
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from itertools import chain

from .forms import LoginForm, RegistrationForm, OrderForm, AccountForm, RegistrationContinueForm, AccountForm_Replace_Password
from .mixins import *
from .mixins import CartMixin, NotificationsMixin
from .models import *
from .utils import recalc_cart, create_cart
from jinja2 import Template
from django.shortcuts import redirect
# const


# Начало главной части
brand_names = Brand.objects.filter(name__in=[
    "Champion Reverse Weave",
    "New Balance",
    "Edwin",
    "Nike",
    "Adidas Originals",
    "Jordan",
    "C.P. Company"
])


def main(request):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []

    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    search_query = request.GET.get('search', '')
    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()
    suggestion = Suggestion.objects.all()

    brands_main = []
    selected_brand1 = []
    selected_brand2 = []
    for element in brands_all:
        if element.output_main:
            brands_main.append(element)
            if element.name == "Jordan":
                selected_brand1 = element
            if element.name == "C.P. Company":
                selected_brand2 = element

    new_products = NewProduct.objects.all()
    products = Product.objects.all()

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    month_bestseller, month_bestseller_qty = Product.objects.get_month_bestseller()

    context = {
        'product_all': product_all,
        'brands_all': brands_all,
        'category_all': category_all,
        'sex_all': sex_all,
        'search_query': search_query,
        'suggestion': suggestion,
        'new_products': new_products,
        'brands_main': brands_main,
        'selected_brand1': selected_brand1,
        'selected_brand2': selected_brand2,
        'products': products,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,
        'cart': cart
    }

    if month_bestseller:
        context.update({'month_bestseller': month_bestseller, 'month_bestseller_qty': month_bestseller_qty})

    return render(request, 'mainapp/home/main.html', context=context)


def search(request):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []

    for element in wishlist:
        wishlistoutput.append(element.content_object)

    search_query = request.GET.get('search', '')
    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    category_search = list(chain(category_all, CategoryAccessories.objects.all()))
    brands_search = list(chain(brands_all, BrandAccessories.objects.all()))

    if search_query:
        if Product.objects.filter(title__icontains=search_query.strip()):
            product = Product.objects.filter(
                title__icontains=search_query.strip()
            )
        elif Brand.objects.filter(name__icontains=search_query.strip()):
            product = Product.objects.filter(
                brand=Brand.objects.filter(name__icontains=search_query.strip())[0]
            )
        else:
            product = []

        if ProductAccessories.objects.filter(title__icontains=search_query.strip()):
            product_accessories = ProductAccessories.objects.filter(
                title__icontains=search_query.strip()
            )
        elif BrandAccessories.objects.filter(name__icontains=search_query.strip()):
            product_accessories = Product.objects.filter(
                brand=Brand.objects.filter(name__icontains=search_query.strip())[0]
            )
        else:
            product_accessories = []

        product = list(chain(product, product_accessories))

        brands = Brand.objects.filter(name__icontains=search_query.strip())
        category_filter = Category.objects.filter(name__icontains=search_query.strip())
        set_query = 0
        if (len(product) == 0) and (len(category_filter) == 0) and (len(brands) == 0):
            set_query = 1
    else:
        product = Product.objects.all()
        brands = Brand.objects.all()
        category_filter = Category.objects.all()
        set_query = 0

    search_query = "{}".format(search_query)

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        'products': products,
        'discounted_products': discounted_products,
        'brands': brands,
        'category_filter': category_filter,
        'product_all': product_all,
        'brands_all': brands_all,
        'category_all': category_all,
        'sex_all': sex_all,
        'search_query': search_query,
        'set_query': set_query,

        'category_search': category_search,
        'brands_search': brands_search,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,
        'cart': cart
    }
    return render(request, 'mainapp/search/search.html', context=context)


# cart

class CartView(CartMixin, NotificationsMixin, View):

    def get(self, request, *args, **kwargs):

        product_all = Product.objects.all()
        category_all = Category.objects.all()
        brands_all = Brand.objects.all()
        sex_all = Sex.objects.all()

        #if request.user.is_authenticated:
            #cart = Cart.objects.filter(owner=Customer.objects.filter(user=request.user).first()).first()
        #else:
            #cart = None

        context = {
            'cart': self.cart,
            'product_all': product_all,
            'brands_all': brands_all,
            'category_all': category_all,
            'sex_all': sex_all,

            'brand_names': brand_names,

            #'cart': cart
        }
        #return render(request, 'mainapp/cart/cart_last(old).html', context)
        return render(request, 'mainapp/cart/cart.html', context)

# Конец cart

# Конец первой части

# Вывод продукта


def product_output(request, product_brand_slug, product_slug):

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    brands_sort = sorted(Brand.objects.all(), key=lambda x: x.name)
    product = Product.objects.filter(slug=product_slug)[0]

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "brands": brands_sort,
        "product_slug": product_slug,
        "product": product,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,

        'brand_names': brand_names,

        'cart': cart
    }
    return render(request, "mainapp/output/new_product_output_with_slider.html", context=context)
    #return render(request, "mainapp/output/product_output.html", context=context)


def product_output1(request, product_brand_slug1, product_slug1):

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    brands_sort = sorted(Brand.objects.all(), key=lambda x: x.name)
    product = ProductAccessories.objects.filter(slug=product_slug1)[0]

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "brands": brands_sort,
        "product_slug": product_slug1,
        "product": product,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,

        'brand_names': brand_names,
        'cart': cart
    }
    return render(request, "mainapp/output/new_product_output_with_slider.html", context=context)

#   Корзина

#class AddToCartView(CartMixin, views.View):
#
#    def get(self, request, *args, **kwargs):
#        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('product_slug')
#        content_type = ContentType.objects.get(model=ct_model)
#        product = content_type.model_class().objects.get(slug=product_slug)
#        cart_product, created = CartProduct.objects.get_or_create(
#            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
#        )
#        if created:
#            self.cart.products.add(cart_product)
#        recalc_cart(self.cart)
#        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
#        return HttpResponseRedirect('/cart/')


class AddToCartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug, product_size = kwargs.get('ct_model'), kwargs.get('product_slug'), kwargs.get('product_size')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)

        date = {
            'cart': self.cart,
            'content_type': content_type,
            'object_id': product.id,
            'size': product_size
        }
        if request.user.is_authenticated:
            date.update({'user': self.cart.owner})
            cart_product, created = CartProduct.objects.get_or_create(**date)
        else:
            date.update({
                'session_key': request.session.session_key
            })
            cart_product, created = CartProduct.objects.get_or_create(**date)

        if created:
            self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        #messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect('/cart/')


class AddToWishListView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.filter(user=request.user).first()
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('product_slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        wishlist_product, created = WishList.objects.get_or_create(
            owner=customer, content_type=content_type, object_id=product.id
        )
        wishlist_product.save()
        #messages.add_message(request, messages.INFO, "Товар успешно удален")
        url = str(HttpResponseRedirect(request.META['HTTP_REFERER']).url + '#' + product_slug)
        print(url)
        print(HttpResponseRedirect(request.META['HTTP_REFERER']))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class DeleteFromWishListView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.filter(user=request.user).first()
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('product_slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        wishlist_product = WishList.objects.get(
            owner=customer, content_type=content_type, object_id=product.id
        )
        wishlist_product.delete()
        #messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class DeleteFromCartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug, product_size = kwargs.get('ct_model'), kwargs.get('product_slug'), kwargs.get('product_size')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)

        date = {
            'cart': self.cart,
            'content_type': content_type,
            'object_id': product.id,
            'size': product_size
        }
        if request.user.is_authenticated:
            date.update({'user': self.cart.owner})
            cart_product, created = CartProduct.objects.get_or_create(**date)
        else:
            date.update({
                'session_key': request.session.session_key
            })
            cart_product, created = CartProduct.objects.get_or_create(**date)

        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        #messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect('/cart/')

#   Конец корзины

# Конец блока вывода продукта

# Разделитель главной части

# Пол

def sex_man(request):

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()

    category = Category.objects.all()
    product = Product.objects.filter(sex=Sex.objects.filter(slug="muzhskoe")[0])

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        'category': category,
        "set_category": 0,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "products": products,
        "discounted_products": discounted_products,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart
    }
    return render(request, "mainapp/sex/sex_man.html", context=context)


def sex_woman(request):

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    category = Category.objects.all()
    product = Product.objects.filter(sex=Sex.objects.filter(slug="zhenskoe")[0])

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        'category': category,
        "set_category": 0,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "products": products,
        "discounted_products": discounted_products,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, "mainapp/sex/sex_woman.html", context=context)


def category_man(request, category_slug):

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex = Sex.objects.get(slug='muzhskoe')
    category = Category.objects.get(slug=category_slug)
    product = Product.objects.filter(category_id=category.pk, sex_id=sex.pk)
    category = Category.objects.all()

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "category": category,
        "products": products,
        "discounted_products": discounted_products,
        "set_category": category_slug,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, 'mainapp/sex/category_man.html', context=context)


def category_woman(request, category_slug):

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex = Sex.objects.get(slug='zhenskoe')
    category = Category.objects.get(slug=category_slug)
    product = Product.objects.filter(category_id=category.pk, sex_id=sex.pk)
    category = Category.objects.all()

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "category": category,
        "products": products,
        "discounted_products": discounted_products,
        "set_category": category_slug,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, 'mainapp/sex/category_woman.html', context=context)

# Конец Пола

# Категория новинки


def category_for_new_products(request):
    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()
    new_products = NewProduct.objects.all()

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    discounted_products = []
    products = []
    for element in new_products:
        if element.product and element.product.discount:
            discounted_products.append(element.product)
        elif element.product_accessories and element.product_accessories.discount:
            discounted_products.append(element.product)
        else:
            products.append(element.product)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,
        "new_products": new_products,

        'brand_names': brand_names,

        'products': products,
        'discounted_products': discounted_products,

        'wishlist': wishlistoutput,

        'cart': cart,
    }

    return render(request, 'mainapp/new_products/new_products.html', context=context)
# Конец категории новинки

# Бренд


def category_for_brands(request, brand_slug):
    set_brand = brand_slug

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()
    brands = Brand.objects.get(slug=brand_slug)
    product = Product.objects.filter(brand_id=brands.pk)

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    brands_sort = sorted(Brand.objects.all(), key=lambda x: x.name)
    context = {
        "brands": brands_sort,
        "products": products,
        'discounted_products': discounted_products,
        "set_brands": brand_slug,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,
        "set_brand": set_brand,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }

    return render(request, "mainapp/brand/brand_sidebar_with_products.html", context=context)


def category_for_brands_accessories(request, brand_accessories_slug):
    set_brand = brand_accessories_slug

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()
    brands = Brand.objects.get(slug=brand_accessories_slug)
    product = ProductAccessories.objects.filter(brand_id=brands.pk)

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    brands_sort = sorted(Brand.objects.all(), key=lambda x: x.name)
    context = {
        "brands": brands_sort,
        "products": products,
        'discounted_products': discounted_products,
        "set_brands": brand_accessories_slug,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,
        "set_brand": set_brand,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }

    return render(request, "mainapp/brand/brand_sidebar_with_products.html", context=context)


def product_brand(request, product_brand_slug, product_slug):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    brands_sort = sorted(Brand.objects.all(), key=lambda x: x.name)
    product = Product.objects.get(slug=product_slug)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "brands": brands_sort,
        "product_slug": product_slug,
        "product": product,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, "mainapp/brand/product_brand.html", context=context)


def brands_all(request):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    brands = sorted(brands_all, key=lambda x: x.name)

    #first_literally_brands_all = []

    first_literally_brands_all = {}
    for element in brands:
        if first_literally_brands_all.get(str(element)[0], False):
            first_literally_brands_all[str(element)[0]].append(element)
        else:
            first_literally_brands_all[str(element)[0]] = [element]

    #for element in brands:
    #    if first_literally_brands_all.count(str(element)[0]) == 0:
    #        first_literally_brands_all.append(str(element)[0])

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "category_all": category_all,
        "brands_all": brands_all,
        "sex_all": sex_all,

        "brands": brands,
        "first_literally_brands_all": first_literally_brands_all,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, "mainapp/brand/brands_all.html", context=context)

#   Аксессуары


def category_accessories(request):

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    category_for_accessories = CategoryAccessories.objects.all()
    brands_for_accessories = BrandAccessories.objects.all()

    product = ProductAccessories.objects.all()

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    discounted_products = []
    products = []

    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        #"products": product,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,

        "category_for_accessories": category_for_accessories,
        "brands_for_accessories": brands_for_accessories,

        "products": products,
        "discounted_products": discounted_products,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }

    return render(request, "mainapp/accessories/category_accessories.html", context=context)


#   Скидки

def category_skidki(request):
    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    category_for_all_products = []
    brands_for_all_products = []

    for element in Category.objects.all():
        category_for_all_products.append(element)

    for element in CategoryAccessories.objects.all():
        category_for_all_products.append(element)

    for element in Brand.objects.all():
        brands_for_all_products.append(element)

    for element in BrandAccessories.objects.all():
        brands_for_all_products.append(element)

    product = []

    for element in Product.objects.all():
        if element.discount:
            product.append(element)

    for element in ProductAccessories.objects.all():
        if element.discount:
            product.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "products": product,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,

        "category_for_all_products": category_for_all_products,
        "brands_for_all_products": brands_for_all_products,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, "mainapp/skidki/skidki.html", context=context)


#   Фильтры для пользователей

def user_filter_for_brand(request, brand_slug):
    set_brand = brand_slug

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)
    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()
    if request.GET.getlist('category'):
        category = Category.objects.filter(slug__in=request.GET.getlist('category'))
    else:
        category = Category.objects.all()
    if request.GET.getlist('brand'):
        brand = Brand.objects.filter(slug__in=request.GET.getlist('brand'))
    else:
        brand = Brand.objects.filter(slug=brand_slug)[0]
    if request.GET.getlist('sex'):
        sex = Sex.objects.filter(slug__in=request.GET.getlist('sex'))
    else:
        sex = Sex.objects.all()

    if request.GET.getlist('brand'):
        product = Product.objects.filter(
            category__in=category,
            brand__in=brand,
            sex__in=sex
        )
    else:
        product = Product.objects.filter(
            category__in=category,
            brand=brand,
            sex__in=sex
        )

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "products": products,
        "discounted_products": discounted_products,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,
        "set_brand": set_brand,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, "mainapp/brand/brand_sidebar_with_products.html", context=context)


def user_filter_for_man(request):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()
    if request.GET.getlist('category'):
        category = Category.objects.filter(slug__in=request.GET.getlist('category'))
    else:
        category = Category.objects.all()
    if request.GET.getlist('brand'):
        brand = Brand.objects.filter(slug__in=request.GET.getlist('brand'))
    else:
        brand = Brand.objects.all()

    product = Product.objects.filter(
        category__in=category,
        brand__in=brand,
        sex=Sex.objects.filter(slug="muzhskoe")[0]
    )

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "products": products,
        "discounted_products": discounted_products,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, "mainapp/sex/sex_man.html", context=context)


def user_filter_for_woman(request):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()
    if request.GET.getlist('category'):
        category = Category.objects.filter(slug__in=request.GET.getlist('category'))
    else:
        category = Category.objects.all()
    if request.GET.getlist('brand'):
        brand = Brand.objects.filter(slug__in=request.GET.getlist('brand'))
    else:
        brand = Brand.objects.all()

    product = Product.objects.filter(
        category__in=category,
        brand__in=brand,
        sex=Sex.objects.filter(slug="zhenskoe")[0]
    )

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)
    print(discounted_products)
    context = {
        "products": products,
        "discounted_products": discounted_products,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, "mainapp/sex/sex_woman.html", context=context)


def user_filter_for_search(request, search_slug):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    category_search = list(chain(category_all, CategoryAccessories.objects.all()))
    brands_search = list(chain(brands_all, BrandAccessories.objects.all()))

    if request.GET.getlist('category'):
        category = Category.objects.filter(slug__in=request.GET.getlist('category'))
    else:
        category = Category.objects.all()

    if request.GET.getlist('brand'):
        brand = Brand.objects.filter(slug__in=request.GET.getlist('brand'))
    else:
        brand = Brand.objects.all()

    #   ///

    if request.GET.getlist('category'):
        category_accessories = CategoryAccessories.objects.filter(slug__in=request.GET.getlist('category'))
    else:
        category_accessories = CategoryAccessories.objects.all()

    if request.GET.getlist('brand'):
        brand_accessories = BrandAccessories.objects.filter(slug__in=request.GET.getlist('brand'))
    else:
        brand_accessories = BrandAccessories.objects.all()

    if request.GET.getlist('sex'):
        sex = Sex.objects.filter(slug__in=request.GET.getlist('sex'))
    else:
        sex = Sex.objects.all()

    if Product.objects.filter(title__icontains=search_slug.strip()):
        product = Product.objects.filter(
            category__in=category,
            brand__in=brand,
            sex__in=sex,
            title__icontains=search_slug.strip(),
        )
    elif Brand.objects.filter(name__icontains=search_slug.strip()):
        product = Product.objects.filter(
            category__in=category,
            brand__in=brand,
            sex__in=sex,
            brand=Brand.objects.filter(name__icontains=search_slug.strip())[0]
        )
    else:
        product = Product.objects.filter(
            category__in=category,
            brand__in=brand,
            sex__in=sex,
        )

    if ProductAccessories.objects.filter(title__icontains=search_slug.strip()):
        product_accessories = ProductAccessories.objects.filter(
            category__in=category_accessories,
            brand__in=brand_accessories,
            sex__in=sex,
            title__icontains=search_slug.strip(),
        )
    elif BrandAccessories.objects.filter(name__icontains=search_slug.strip()):
        product_accessories = ProductAccessories.objects.filter(
            category__in=category_accessories,
            brand__in=brand_accessories,
            sex__in=sex,
            brand=BrandAccessories.objects.filter(name__icontains=search_slug.strip())[0]
        )
    else:
        product_accessories = ProductAccessories.objects.filter(
            category__in=category_accessories,
            brand__in=brand_accessories,
            sex__in=sex,
        )

    product = list(chain(product, product_accessories))

    if search_slug:
        brands = Brand.objects.filter(name__icontains=search_slug.strip())
        category_filter = Category.objects.filter(name__icontains=search_slug.strip())
        set_query = 0
        if (len(category_filter) == 0) and (len(brands) == 0):
            set_query = 1
    else:
        brands = Brand.objects.all()
        category_filter = Category.objects.all()
        set_query = 0

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "products": products,
        "discounted_products": discounted_products,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,
        "search_query": search_slug,

        'brands': brands,
        'category_filter': category_filter,
        'set_query': set_query,

        'category_search': category_search,
        'brands_search': brands_search,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }
    return render(request, "mainapp/search/search.html", context=context)


def user_filter_for_accessories(request):

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    category_for_accessories = CategoryAccessories.objects.all()
    brands_for_accessories = BrandAccessories.objects.all()

    if request.GET.getlist('category'):
        accessories_category = CategoryAccessories.objects.filter(slug__in=request.GET.getlist('category'))
    else:
        accessories_category = CategoryAccessories.objects.all()

    if request.GET.getlist('brand'):
        brand_category = BrandAccessories.objects.filter(slug__in=request.GET.getlist('brand'))
    else:
        brand_category = BrandAccessories.objects.all()

    product = ProductAccessories.objects.filter(
        category__in=accessories_category,
        brand__in=brand_category
    )

    discounted_products = []
    products = []
    for element in product:
        if element.discount:
            discounted_products.append(element)
        else:
            products.append(element)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "products": products,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,

        "category_for_accessories": category_for_accessories,
        "brands_for_accessories": brands_for_accessories,

        'discounted_products': discounted_products,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }

    return render(request, 'mainapp/accessories/category_accessories.html', context=context)


def user_filter_for_skidki(request):
    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []
    for element in wishlist:
        wishlistoutput.append(element.content_object)

    category_for_all_products = []
    brands_for_all_products = []

    for element in Category.objects.all():
        category_for_all_products.append(element)

    for element in CategoryAccessories.objects.all():
        category_for_all_products.append(element)

    for element in Brand.objects.all():
        brands_for_all_products.append(element)

    for element in BrandAccessories.objects.all():
        brands_for_all_products.append(element)

    if request.GET.getlist('category'):
        accessories_category = CategoryAccessories.objects.filter(slug__in=request.GET.getlist('category'))
        category = Category.objects.filter(slug__in=request.GET.getlist('category'))
    else:
        accessories_category = CategoryAccessories.objects.all()
        category = Category.objects.all()

    if request.GET.getlist('brand'):
        brand_category = BrandAccessories.objects.filter(slug__in=request.GET.getlist('brand'))
        brand = Brand.objects.filter(slug__in=request.GET.getlist('brand'))
    else:
        brand_category = BrandAccessories.objects.all()
        brand = Brand.objects.all()

    product1 = ProductAccessories.objects.filter(
        category__in=accessories_category,
        brand__in=brand_category,
        discount=True
    )

    product2 = Product.objects.filter(
        category__in=category,
        brand__in=brand,
        discount=True
    )

    product = list(chain(product1, product2))

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    context = {
        "products": product,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,

        "category_for_all_products": category_for_all_products,
        "brands_for_all_products": brands_for_all_products,


        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }

    return render(request, 'mainapp/skidki/skidki.html', context=context)


def user_filter_for_new(request):
    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())
    else:
        wishlist = []
    wishlistoutput = []

    for element in wishlist:
        wishlistoutput.append(element.content_object)

    cart = None
    if request.user.is_authenticated and not request.user.is_superuser:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        if not request.session.get('cart_id'):
            cart = Cart.objects.create(
                session_key=uuid.uuid4()
            )
            request.session['cart_id'] = cart.id
        else:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )

    if request.GET.getlist('category'):
        category = Category.objects.filter(slug__in=request.GET.getlist('category'))
    else:
        category = Category.objects.all()

    if request.GET.getlist('brand'):
        brand = Brand.objects.filter(slug__in=request.GET.getlist('brand'))
    else:
        brand = Brand.objects.all()

    if request.GET.getlist('sex'):
        sex = Sex.objects.filter(slug__in=request.GET.getlist('sex'))
    else:
        sex = Sex.objects.all()

    product = []

    for element in NewProduct.objects.all():
        if element.product.category in category and element.product.brand in brand and element.product.sex in sex:
            product.append(element.product)

    context = {
        "products": product,
        "product_all": product_all,
        "brands_all": brands_all,
        "category_all": category_all,
        "sex_all": sex_all,

        'brand_names': brand_names,

        'wishlist': wishlistoutput,

        'cart': cart,
    }

    return render(request, 'mainapp/new_products/new_products.html', context=context)


class LoginView(views.View):

    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    def get(self, request, *args, **kwargs):

        cart = None
        if request.user.is_authenticated and not request.user.is_superuser:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            if not request.session.get('cart_id'):
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )
                request.session['cart_id'] = cart.id
            else:
                try:
                    cart = Cart.objects.get(id=request.session['cart_id'])
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(
                        session_key=uuid.uuid4()
                    )
                    request.session['cart_id'] = cart.id

        form = LoginForm(request.POST or None)
        context = {
            "product_all": self.product_all,
            "brands_all": brands_all,
            "category_all": self.category_all,
            "sex_all": self.sex_all,

            'form': form,
            'cart': cart
        }
        return render(request, 'mainapp/user_account/login.html', context)

    def post(self, request, *args, **kwargs):

        cart = None
        if request.user.is_authenticated and not request.user.is_superuser:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            if not request.session.get('cart_id'):
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )
                request.session['cart_id'] = cart.id
            else:
                try:
                    cart = Cart.objects.get(id=request.session['cart_id'])
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(
                        session_key=uuid.uuid4()
                    )
                    request.session['cart_id'] = cart.id

        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is None:
                user = authenticate(username=User.objects.filter(email=username).first().username, password=password)
                print(user)
            if user is not None:
                login(request, user)
                if request.session.get('cart_id'):
                    create_cart(request)
                return HttpResponseRedirect('/')
        context = {
            "product_all": self.product_all,
            "brands_all": brands_all,
            "category_all": self.category_all,
            "sex_all": self.sex_all,

            'form': form,
            'cart': cart
        }
        return render(request, 'mainapp/user_account/login.html', context)


class RegistrationView(views.View):
    product_all = Product.objects.all()
    category_all = Category.objects.all()
    brands_all = Brand.objects.all()
    sex_all = Sex.objects.all()

    def get(self, request, *args, **kwargs):

        cart = None
        if request.user.is_authenticated and not request.user.is_superuser:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            if not request.session.get('cart_id'):
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )
                request.session['cart_id'] = cart.id
            else:
                try:
                    cart = Cart.objects.get(id=request.session['cart_id'])
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(
                        session_key=uuid.uuid4()
                    )
                    request.session['cart_id'] = cart.id

        form = RegistrationForm(request.POST or None)
        context = {
            "product_all": self.product_all,
            "brands_all": self.brands_all,
            "category_all": self.category_all,
            "sex_all": self.sex_all,

            'form': form,
            'cart': cart
        }
        return render(request, 'mainapp/user_account/registration.html', context)

    def post(self, request, *args, **kwargs):

        cart = None
        if request.user.is_authenticated and not request.user.is_superuser:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            if not request.session.get('cart_id'):
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )
                request.session['cart_id'] = cart.id
            else:
                try:
                    cart = Cart.objects.get(id=request.session['cart_id'])
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(
                        session_key=uuid.uuid4()
                    )
                    request.session['cart_id'] = cart.id

        form = RegistrationForm(request.POST or None)
        form_continue = RegistrationContinueForm(request.POST or None)
        if request.user.is_authenticated:
            if form_continue.is_valid():
                customer = Customer.objects.filter(user=request.user).first()
                if form_continue.cleaned_data['phone']:
                    customer.phone = form_continue.cleaned_data['phone']
                if form_continue.cleaned_data['address']:
                    customer.address = form_continue.cleaned_data['address']
                if form_continue.cleaned_data['first_name']:
                    request.user.first_name = form_continue.cleaned_data['first_name']
                if form_continue.cleaned_data['last_name']:
                    request.user.last_name = form_continue.cleaned_data['last_name']
                customer.save()
                request.user.save()
                return HttpResponseRedirect('/')
            context = {
                "product_all": self.product_all,
                "brands_all": brands_all,
                "category_all": self.category_all,
                "sex_all": self.sex_all,

                'form': form_continue,
                'cart': cart
            }
            return render(request, 'mainapp/user_account/registration.html', context)
        else:
            if form.is_valid():
                new_user = form.save(commit=False)
                new_user.username = form.cleaned_data['username']
                new_user.save()
                new_user.set_password(form.cleaned_data['password'])
                new_user.save()
                Customer.objects.create(
                    user=new_user,
                )
                user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                if user is not None:
                    login(request, user)
                    context = {
                        'form': RegistrationContinueForm(),
                        'cart': cart
                    }
                    return render(request, 'mainapp/user_account/registration.html', context)
                else:
                    context = {
                        "product_all": self.product_all,
                        "brands_all": brands_all,
                        "category_all": self.category_all,
                        "sex_all": self.sex_all,

                        'form': form,
                        'cart': cart
                    }
                    return render(request, 'mainapp/user_account/registration.html', context)
            context = {
                "product_all": self.product_all,
                "brands_all": brands_all,
                "category_all": self.category_all,
                "sex_all": self.sex_all,

                'form': form,
                'cart': cart
            }
            return render(request, 'mainapp/user_account/registration.html', context)


# Возможна ошибка из-за CartMixin, 'cart': self.cart,
class AccountView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):

        form = AccountForm()

        product_all = Product.objects.all()
        category_all = Category.objects.all()
        brands_all = Brand.objects.all()
        sex_all = Sex.objects.all()
        customer = Customer.objects.get(user=request.user)
        wishlist = WishList.objects.filter(owner=Customer.objects.filter(user=request.user).first())

        if request.user.first_name:
            form.fields['first_name'].widget.attrs['placeholder'] = request.user.first_name
        else:
            form.fields['phone'].widget.attrs['placeholder'] = 'Вы ещё не заполнили это поле'

        if request.user.last_name:
            form.fields['last_name'].widget.attrs['placeholder'] = request.user.last_name
        else:
            form.fields['phone'].widget.attrs['placeholder'] = 'Вы ещё не заполнили это поле'

        if customer.phone:
            form.fields['phone'].widget.attrs['placeholder'] = customer.phone
        else:
            form.fields['phone'].widget.attrs['placeholder'] = 'Вы ещё не заполнили это поле'

        if customer.address:
            form.fields['address'].widget.attrs['placeholder'] = customer.address
        else:
            form.fields['address'].widget.attrs['placeholder'] = 'Вы ещё не заполнили это поле'

        if request.user.email:
            form.fields['email'].widget.attrs['placeholder'] = request.user.email
        else:
            form.fields['email'].widget.attrs['placeholder'] = 'Вы ещё не заполнили это поле'
        form_replace_password = AccountForm_Replace_Password(request.POST or None)

        context = {
            'customer': customer,
            'wishlist': wishlist,
            'cart': self.cart,
            "product_all": product_all,
            "brands_all": brands_all,
            "category_all": category_all,
            "sex_all": sex_all,
            'brand_names': brand_names,

            'form': form,
            'form_replace_password': form_replace_password
        }
        return render(request, 'mainapp/user_account/account.html', context)

    def post(self, request, *args, **kwargs):
        form = AccountForm(request.POST or None)
        if form.is_valid():
            if form.cleaned_data['first_name']:
                request.user.first_name = form.cleaned_data['first_name']

            if form.cleaned_data['last_name']:
                request.user.last_name = form.cleaned_data['last_name']
            customer = Customer.objects.get(user=request.user)

            if form.cleaned_data['phone']:
                customer.phone = form.cleaned_data['phone']

            if form.cleaned_data['address']:
                customer.address = form.cleaned_data['address']

            if form.cleaned_data['email']:
                request.user.email = form.cleaned_data['email']
            request.user.save()
            customer.save()
        return HttpResponseRedirect('/account/')


class CheckoutView(CartMixin, NotificationsMixin, views.View):

    def get(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'form': form,
            'notifications': self.notifications(request.user),
        }
        #return render(request, 'mainapp/cart/making_an_order_last(old).html', context)
        return render(request, 'mainapp/cart/making_an_order.html', context)


class MakeOrderView(CartMixin, views.View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        form = OrderForm(request.POST or None)

        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)

        if form.is_valid():
            out_of_stock = []
            more_than_on_stock = []
            out_of_stock_message = ""
            more_than_on_stock_message = ""
            for item in self.cart.products.all():
                if not item.content_object.stock:
                    out_of_stock.append(' - '.join([
                        item.content_object.brand.name, item.content_object.title
                    ]))
                if item.content_object.stock and item.content_object.stock < item.qty:
                    more_than_on_stock.append(
                        {'product': ' - '.join([item.content_object.brand.name, item.content_object.title]),
                         'stock': item.content_object.stock, 'qty': item.qty}
                    )
            if out_of_stock:
                out_of_stock_products = ', '.join(out_of_stock)
                out_of_stock_message = f'Товара уже нет в наличии: {out_of_stock_products}.'

            if more_than_on_stock:
                for item in more_than_on_stock:
                    more_than_on_stock_message += f'Товар: {item["product"]}. ' \
                                                  f'В наличии: {item["stock"]}. ' \
                                                  f'Заказано: {item["qty"]}\n'
            error_message_for_customer = ""
            if out_of_stock:
                error_message_for_customer = out_of_stock_message + '\n'
            if more_than_on_stock_message:
                error_message_for_customer += more_than_on_stock_message + '\n'

            if error_message_for_customer:
                messages.add_message(request, messages.INFO, error_message_for_customer)
                return HttpResponseRedirect('/making_an_order/')

            new_order = form.save(commit=False)
            if request.user.is_authenticated:
                new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()

            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            if request.user.is_authenticated:
                customer.orders.add(new_order)
            else:
                for c in self.cart.products.all():
                    self.cart.products.remove(c)
                self.cart.save()

            for item in self.cart.products.all():
                item.content_object.stock -= item.qty
                item.content_object.save()

            #request.session['check'] = True] = True
            #request.session['order'] = new_order.id
            #request.session['first_name'] = new_order.first_name
            #request.session['last_name'] = new_order.last_name
            #request.session['phone'] = new_order.phone
            #request.session['buying_type'] = new_order.buying_type
            #request.session['address'] = new_order.address
            #request.session['order_date'] = new_order.order_date
            #request.session['comment'] = new_order.comment

            #data = {
            #    'order': new_order.id,
            #    'first_name': new_order.first_name,
            #    'last_name': new_order.last_name,
            #    'phone': new_order.phone,
            #    'buying_type': new_order.buying_type,
            #    'address': new_order.address,
            #    'order_date': new_order.order_date,
            #    'comment': new_order.comment
            #}

            #for key, value in data.items():
            #    messages.success(request, messages.INFO, value)

            messages.success(request, f'Номер заказа: {new_order.id}')
            messages.success(request, f'Имя: {new_order.first_name}')
            messages.success(request, f'Фамилия: {new_order.last_name}')
            messages.success(request, f'Номер телефона: {new_order.phone}')
            messages.success(request, f'Тип доставки: {new_order.buying_type}')
            messages.success(request, f'Адрес: {new_order.address}')
            messages.success(request, f'Дата доставки: {new_order.order_date}')
            messages.success(request, f'Коментарии к заказу: {new_order.comment}')

            #messages.add_message(request, messages.INFO, data)

            return HttpResponseRedirect('/')

        return HttpResponseRedirect('/making_an_order/')


class ChangeQTYView(CartMixin, views.View):
    def post(self, request, *args, **kwargs):
        ct_model, product_slug, product_size = kwargs.get('ct_model'), kwargs.get('product_slug'), kwargs.get('product_size')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        #cart_product = CartProduct.objects.get(
        #    user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id, size=product_size
        #)

        date = {
            'cart': self.cart,
            'content_type': content_type,
            'object_id': product.id,
            'size': product_size
        }
        if request.user.is_authenticated:
            date.update({'user': self.cart.owner})
            cart_product, created = CartProduct.objects.get_or_create(**date)
        else:
            date.update({
                'session_key': request.session.session_key
            })
            cart_product, created = CartProduct.objects.get_or_create(**date)
        if int(request.POST.get('qty')) == 0:
            self.cart.products.remove(cart_product)
            cart_product.delete()
            recalc_cart(self.cart)
        else:
            qty = int(request.POST.get('qty'))
            cart_product.qty = qty
            # force_update=True - обновление QuerySET остается прежним
            cart_product.save(force_update=True)
            recalc_cart(self.cart)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class ChangeSIZEView(CartMixin, views.View):
    def post(self, request, *args, **kwargs):
        ct_model, product_slug, product_size = kwargs.get('ct_model'), kwargs.get('product_slug'), kwargs.get('product_size')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        #cart_product = CartProduct.objects.get(
        #    user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id, size=product_size
        #)

        date = {
            'cart': self.cart,
            'content_type': content_type,
            'object_id': product.id,
            'size': product_size
        }
        if request.user.is_authenticated:
            date.update({'user': self.cart.owner})
            cart_product, created = CartProduct.objects.get_or_create(**date)
        else:
            date.update({
                'session_key': request.session.session_key
            })
            cart_product, created = CartProduct.objects.get_or_create(**date)
        if (cart_product in self.cart.products.filter(user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id, size=str(request.POST.get('size')))) or not self.cart.products.filter(user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id, size=str(request.POST.get('size'))):
            size = str(request.POST.get('size'))
            cart_product.size = size
            cart_product.save()
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            messages.add_message(request, messages.INFO,
                f'В вашей корзине уже есть товар {product.title} с размером {str(request.POST.get("size")).replace("_",".", 1)}')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])