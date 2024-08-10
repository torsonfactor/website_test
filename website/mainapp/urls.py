from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [

    #   Главная

    path('', views.main, name="home"),
    path('search/', views.search, name="search"),

    #   Категория Новинки

    path('new_products/', views.category_for_new_products, name="category_for_new_products"),

    #   Категория Аксессуары

    path('accessories/', views.category_accessories, name="category_accessories"),

    #   Категория Скидки

    path('skidki/', views.category_skidki, name="category_skidki"),

    #   Категория Пол

    path('muzhskoe/', views.sex_man, name="man"),
    path('zhenskoe/', views.sex_woman, name="woman"),
    path('muzhskoe/<slug:category_slug>/', views.category_man, name="category_man"),
    path('zhenskoe/<slug:category_slug>/', views.category_woman, name="category_woman"),

    #   Категория Бренд

    path('brand/<slug:brand_slug>/', views.category_for_brands, name="brand_catalog"),
    path('brands/', views.brands_all, name="brands_all"),
    path('brands/<slug:brand_accessories_slug>/', views.category_for_brands_accessories, name="brand_accessories_catalog"),

    #   Фильтр

    path('filter_for_brand/<slug:brand_slug>/', views.user_filter_for_brand, name="filter_for_brand"),
    path('filter_man/', views.user_filter_for_man, name="filter_for_man"),
    path('filter_woman/', views.user_filter_for_woman, name="filter_for_woman"),
    path('filter_search/<slug:search_slug>/', views.user_filter_for_search, name="filter_for_search"),
    path('filter_for_accessories/', views.user_filter_for_accessories, name="filter_for_accessories"),
    path('filter_for_skidki/', views.user_filter_for_skidki, name="filter_for_skidki"),
    path('filter_for_new/', views.user_filter_for_new, name="filter_for_new"),

    # Корзина

    path('cart/', views.CartView.as_view(), name="cart"),
    path('add-to-cart/<slug:ct_model>/<slug:product_slug>/<slug:product_size>', views.AddToCartView.as_view(), name="add-to-cart"),
    path('remove-from-cart/<slug:ct_model>/<slug:product_slug>/<slug:product_size>', views.DeleteFromCartView.as_view(), name="remove-from-cart"),

    path('add-to-wishlist/<slug:ct_model>/<slug:product_slug>/', views.AddToWishListView.as_view(), name='add_to_wishlist'),
    path('remove-from-wishlist/<slug:ct_model>/<slug:product_slug>', views.DeleteFromWishListView.as_view(), name="remove_from_wishlist"),

    path('change-qty/<str:ct_model>/<slug:product_slug>/<slug:product_size>', views.ChangeQTYView.as_view(), name='change_qty'),
    path('change-size/<str:ct_model>/<slug:product_slug>/<slug:product_size>', views.ChangeSIZEView.as_view(), name='change_size'),

    #   Оформление заказа

    path('making_an_order/', views.CheckoutView.as_view(), name="making_an_order"),
    path('make-order/', views.MakeOrderView.as_view(), name='make-order'),

    #   Вывод продукта (блок должен быть поледним)

    path('<slug:product_brand_slug>/<slug:product_slug>/', views.product_output, name="product"),
    path('accessories/<slug:product_brand_slug1>/<slug:product_slug1>/', views.product_output1, name="product1"),

    #   Конец блока вывода продукта

    #   Блок Аккаунт пользователя

    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page="/"), name='logout'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('account/', views.AccountView.as_view(), name='account'),
]
