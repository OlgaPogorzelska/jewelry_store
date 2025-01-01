from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from cart.models import Cart, CartItem
from shop.models import Product


# Create your views here.

class AddToCart(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        product = get_object_or_404(Product, pk=pk)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect(reverse('cart_details', kwargs={'pk': cart.pk}))


class CartView(LoginRequiredMixin, DetailView):
    model = Cart
    template_name = 'cart/cart_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.get_object()
        context['cart_items'] = CartItem.objects.filter(cart=self.object)
        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        cart = get_object_or_404(Cart, pk=pk)

        for key in request.POST:
            if key.startswith('quantity_'):
                index = key.split('_')[1]
                quantity = request.POST[key]
                item_pk = request.POST.get(f'item_pk_{index}')  # Identyfikator elementu

                if quantity and item_pk:
                    cart_item = get_object_or_404(CartItem, pk=item_pk)
                    cart_item.quantity = int(quantity)  # Zaktualizuj iloquantity
                    cart_item.save()

        return redirect(reverse('cart_details', kwargs={'pk': cart.pk}))


class RemoveFromCart(LoginRequiredMixin, DetailView):
    model = CartItem

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        cart_pk = self.object.cart.pk
        self.object.delete()
        return redirect(reverse('cart_details', kwargs={'pk': cart_pk}))
