from calendar import monthrange

from django.db import models
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

User = get_user_model()


class Size(models.Model):
    title = models.CharField(verbose_name="Размер", max_length=9)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", blank=True, null=True)
    shoe_size = models.BooleanField(verbose_name="Для обуви", default=False, null=True, blank=True)
    clothing_size = models.BooleanField(verbose_name="Для одежды", default=False, null=True, blank=True)
    accessories_size = models.BooleanField(verbose_name="Для аксессуаров", default=False, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"


class Suggestion(models.Model):
    name = models.CharField(verbose_name="Название", max_length=50)
    #content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    #object_id = models.PositiveIntegerField()
    #content_object = GenericForeignKey('content_type', 'object_id')
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True)
    photo = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)

    def __str__(self):
        return "{} - категория для предложки".format(self.name)

    class Meta:
        verbose_name = "Предложка для главной страницы"
        verbose_name_plural = "Предложка для главной страницы"


class NewProduct(models.Model):
    product = models.ForeignKey('Product', verbose_name="Вещи из продуктов", on_delete=models.CASCADE, blank=True,
                                null=True, related_name='back_product')
    product_accessories = models.ForeignKey('ProductAccessories', verbose_name="Вещи из аксессуаров",
                                            on_delete=models.CASCADE, blank=True, null=True)

    new_product = models.BooleanField(verbose_name="Добавить в новинки", default=True)

    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True, blank=True, null=True)

    def __str__(self):
        if self.product:
            return "{}".format(self.product)
        else:
            return "{}".format(self.product_accessories)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not NewProduct.objects.get(id=self.pk).new_product:
            r = NewProduct.objects.get(id=self.pk).product
            r.new_product = False
            r.save()
            super().delete(*args, **kwargs)

    def delete(self, *args, **kwargs):
        r = NewProduct.objects.get(id=self.pk)
        r.product.new_product = False
        r.product.save()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Новинки"
        verbose_name_plural = "Новинки"


class DiscountProduct(models.Model):
    product = models.ForeignKey('Product', verbose_name="Вещи из продуктов", on_delete=models.CASCADE, blank=True,
                                null=True, related_name='back_product_discount')
    product_accessories = models.ForeignKey('ProductAccessories', verbose_name="Вещи из аксессуаров",
                                            on_delete=models.CASCADE, blank=True, null=True)

    discount = models.BooleanField(verbose_name="Добавить в скидки", default=True)

    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True)

    def __str__(self):
        if self.product:
            return "{}".format(self.product)
        else:
            return "{}".format(self.product_accessories)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not DiscountProduct.objects.get(id=self.pk).discount:
            r = DiscountProduct.objects.get(id=self.pk).product
            r.discount = False
            r.save()
            super().delete(*args, **kwargs)

    def delete(self, *args, **kwargs):
        r = DiscountProduct.objects.get(id=self.pk)
        r.product.discount = False
        r.product.save()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Скидки"
        verbose_name_plural = "Скидки"


class Category(models.Model):
    name = models.CharField("Название", max_length=50)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url_man(self):
        return reverse('category_man', kwargs={'category_slug': self.slug})

    def get_absolute_url_woman(self):
        return reverse('category_woman', kwargs={'category_slug': self.slug})

    class Meta:
        verbose_name = "Категория Для Вещей"
        verbose_name_plural = "Категории Для Вещей"


class CategoryAccessories(models.Model):
    name = models.CharField("Название", max_length=50)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория Для Аксессуаров"
        verbose_name_plural = "Категория Для Аксессуаров"


class Sex(models.Model):
    name = models.CharField("Название", max_length=50)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True)
    photo = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Пол"
        verbose_name_plural = "Пол"

    def get_absolute_url(self):
        return reverse('sex', kwargs={"sex_slug": self.slug})


class Brand(models.Model):
    photo = models.ImageField("Выберите фотографию логотипа: ", upload_to="mainapp/", null=True, blank=True)
    photo_background = models.ImageField("Выберите фотографию на задний план: ", upload_to="mainapp/", null=True, blank=True)
    name = models.CharField(verbose_name="Название", max_length=50)
    description = models.TextField("Описание: ", max_length=1050, null=False, blank=True)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True)

    output_main = models.BooleanField(verbose_name="Добавить на главную", default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('brand_catalog', kwargs={"brand_slug": self.slug})

    class Meta:
        verbose_name = "Список Брендов Для Вещей"
        verbose_name_plural = "Список Брендов Для Вещей"


class BrandAccessories(models.Model):
    photo = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)
    name = models.CharField(verbose_name="Название", max_length=50)
    description = models.TextField("Описание: ", max_length=50, null=False, blank=True)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('brand_accessories_catalog', kwargs={"brand_accessories_slug": self.slug})

    class Meta:
        verbose_name = "Список Брендов Для Аксессуаров"
        verbose_name_plural = "Список Брендов Для Аксессуаров"


class ProductManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()

    def get_month_bestseller(self):
        today = datetime.today()
        year, month = today.year, today.month
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, monthrange(year, month)[1])
        query = f"""
            SELECT shop_product.id as product_id, SUM(distinct shop_cart_product.qty) as total_qty
            FROM mainapp_order as shop_order
            JOIN mainapp_cart as shop_cart on shop_order.cart_id = shop_cart.id
            JOIN mainapp_cartproduct as shop_cart_product on shop_cart.id = shop_cart_product.cart_id
            JOIN mainapp_product as shop_product on shop_cart_product.object_id=shop_product.id
            WHERE shop_order.order_date >= '{first_day}' and shop_order.order_date <= '{last_day}'
            GROUP BY product_id
            ORDER BY total_qty DESC
            LIMIT 9
        """

        product_id = []
        qty = []
        product_get = []
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchall()
        if row:
            for count in row:
                product_id.append(count[0])
                qty.append(count[1])
                product_get.append(Product.objects.get(pk=count[0]))
            return product_get, qty
        return None, None


class Product(models.Model):

    MIN_RESOLUTION = (200, 200)
    MAX_RESOLUTION = (4000, 4000)
    MAX_IMAGE_SIZE = 3145728

    photo = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True)
    photo_product1 = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)
    photo_product2 = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)
    photo_product3 = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)
    title = models.CharField("Название: ", max_length=32)
    description = models.TextField("Описание: ", max_length=1000, null=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sex = models.ForeignKey(Sex, on_delete=models.CASCADE)

    size = models.ManyToManyField(Size, verbose_name="Размеры", null=True, blank=True)

    stock = models.IntegerField(default=1, verbose_name="Наличие на складе")

    discount = models.BooleanField(verbose_name="Товар со скидкой", default=True)

    new_product = models.BooleanField(verbose_name="Добавить в новинки", default=True)

    price = models.IntegerField("Введите цену: ")

    sale_price = models.IntegerField(
        verbose_name="Введите цену со скидкой", blank=True, null=True
    )

    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True)

    objects = ProductManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs={"product_brand_slug": self.brand.slug, "product_slug": self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if Product.objects.get(id=self.pk).new_product and NewProduct.objects.filter(slug=self.slug).first() is None:
            p = Product.objects.get(id=self.pk)
            n = NewProduct.objects.create(product=p, new_product=p.new_product, slug=p.slug)
            n.save()
        if Product.objects.get(id=self.pk).discount and DiscountProduct.objects.filter(slug=self.slug).first() is None:
            p = Product.objects.get(id=self.pk)
            n = DiscountProduct.objects.create(product=p, discount=p.discount, slug=p.slug)
            n.save()

    @property
    def ct_model(self):
        return self._meta.model_name

    class Meta:
        verbose_name = "Каталог Вещей"
        verbose_name_plural = "Каталог Вещей"


class ProductAccessories(models.Model):

    MIN_RESOLUTION = (200, 200)
    MAX_RESOLUTION = (4000, 4000)
    MAX_IMAGE_SIZE = 3145728

    photo = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True)
    photo_product1 = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)
    photo_product2 = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)
    photo_product3 = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)
    title = models.CharField("Название: ", max_length=32)
    description = models.TextField("Описание: ", max_length=1000, null=False)

    brand = models.ForeignKey(
        BrandAccessories, verbose_name="Бренд аксессуара>", on_delete=models.CASCADE, null=True, blank=True
    )

    category = models.ForeignKey(
        CategoryAccessories, verbose_name="Категория аксесуара", on_delete=models.CASCADE, null=True, blank=True
    )

    sex = models.ForeignKey(Sex, on_delete=models.CASCADE)

    size = models.ManyToManyField(Size, verbose_name="Размеры", null=True, blank=True)

    stock = models.IntegerField(default=1, verbose_name="Наличие на складе")

    discount = models.BooleanField(verbose_name="Товар со скидкой", default=True)

    price = models.IntegerField("Введите цену: ")

    sale_price = models.IntegerField(
        verbose_name="Введите цену со скидкой", blank=True, null=True
    )

    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product1', kwargs={"product_brand_slug1": self.brand.slug, "product_slug1": self.slug})

    @property
    def ct_model(self):
        return self._meta.model_name

    class Meta:
        verbose_name = "Каталог Аксессуаров"
        verbose_name_plural = "Каталог Аксессуаров"


class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name="Покупатель", on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    size = models.CharField(max_length=9, null=True, blank=True)
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')
    session_key = models.CharField(max_length=1024, verbose_name="Ключ сессии", null=True, blank=True)

    def __str__(self):
        return 'Продукт {} (Для корзины)'.format(self.content_object.title)

    def save(self, *args, **kwargs):
        if self.content_object.discount:
            self.final_price = self.qty * self.content_object.sale_price
        else:
            self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Корзина с продуктами"
        verbose_name_plural = "Корзина с продуктами"


class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name="Владелец", on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    session_key = models.CharField(max_length=1024, verbose_name="Ключ сессии", null=True, blank=True)

    def __str__(self):
        return f"Покупатель: {self.owner} - {self.session_key}"

    def products_in_cart(self):
        return [c.content_object for c in self.products.all()]

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class WishList(models.Model):
    """Избранное"""

    owner = models.ForeignKey('Customer', null=True, verbose_name="Владелец", on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return f"Избранное пользователя: {self.owner.user} - {self.content_object}"

    def products_in_wishlist(self):
        return [c for c in self.content_object.all()]

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name="Номер телефона", null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name="Адрес", null=True, blank=True)
    session_key = models.CharField(max_length=1024, verbose_name="Ключ сессии", null=True, blank=True)

    def __str__(self):
        return "Покупатель: {}".format(self.user)

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"


class Order(models.Model):
    """Заказ пользователя"""

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Не подтвержден'),
        (STATUS_IN_PROGRESS, 'Подтвержден'),
        (STATUS_READY, 'Готов к выдаче'),
        (STATUS_COMPLETED, 'Получен покупателем'),
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка'),
    )

    customer = models.ForeignKey('Customer', verbose_name="Покупатель", related_name="orders", on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name="Адрес")
    status = models.CharField(max_length=100, verbose_name="Статус заказа", choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name="Способ получения", choices=BUYING_TYPE_CHOICES)
    comment = models.TextField(verbose_name="Коментарий к заказу", null=True, blank=True)
    created_at = models.DateField(verbose_name="Дата создания заказа", auto_now=True)
    order_date = models.DateField(verbose_name="Дата получения заказа", default=timezone.now)
    session_key = models.CharField(max_length=1024, verbose_name="Ключ сессии", null=True, blank=True)

    def __str__(self):
        return f'Покупатель: {self.customer} ({self.first_name} - Номер заказа {self.id})'

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class NotificationManager(models.Manager):
    """Менеджер уведомлений"""

    def get_queryset(self):
        return super().get_queryset()

    def all(self, recipient):
        return self.get_queryset().filter(
            recipient=recipient,
            read=False
        )

    def make_all_read(self, recipient):
        qs = self.get_queryset().filter(recipient=recipient, read=False)
        qs.update(read=True)


class Notification(models.Model):
    """Уведомления"""

    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Покупатель")
    text = models.TextField()
    read = models.BooleanField(default=False)
    objects = NotificationManager()

    def __str__(self):
        return f"Уведомление для {self.recipient.user.username} | id={self.id}"

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"