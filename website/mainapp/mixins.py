import uuid
from django import views

from .models import Cart, Customer, WishList, Notification


class CartMixin(views.generic.detail.SingleObjectMixin, views.View):

    def dispatch(self, request, *args, **kwargs):
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
            self.cart = cart
        else:
            if not request.session.get('cart_id'):
                cart = Cart.objects.create(
                    session_key=uuid.uuid4()
                )
                request.session['cart_id'] = cart.id
                self.cart = cart
            else:
                try:
                    cart = Cart.objects.get(id=request.session.get('cart_id'))
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(
                        session_key=uuid.uuid4(),
                    )
                    request.session['cart_id'] = cart.id
                self.cart = cart
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class WishListMixin(views.generic.detail.SingleObjectMixin, views.View):

    def dispatch(self, request, *args, **kwargs):
        # Переделать
        # нужно для WishListMixin
        # self.customer = customer
        #wishlist = None
        #if request.user.is_authenticated:
        #    customer = Customer.objects.filter(user=request.user).first()
        #    if not customer:
        #        customer = Customer.objects.create(
        #            user=request.user
        #        )
        #    wishlist = WishList.objects.filter(owner=customer).first()
        #    if not wishlist:
        #        wishlist = WishList.objects.create(owner=customer)
        #self.wishlist = wishlist
        #self.customer = customer

        customer = Customer.objects.filter(user=request.user).first()
        wishlist = WishList.objects.create(owner=customer)
        self.wishlist = wishlist
        self.customer = customer
        return super().dispatch(request, *args, **kwargs)


class NotificationsMixin(views.generic.detail.SingleObjectMixin):

    @staticmethod
    def notifications(user):
        if user.is_authenticated:
            return Notification.objects.all(Customer.objects.filter(user=user)[0])
        return Notification.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = self.notifications(self.request.user)
        return context