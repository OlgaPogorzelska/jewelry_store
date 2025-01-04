from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from cart.models import Cart, CartItem
from shop.models import Product


class AddToCart(View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        product = get_object_or_404(Product, pk=pk)

        size = request.POST.get('size') if product.category.name == "PIERŚCIONKI" else None
        # Sprawdzenie, czy użytkownik jest zalogowany

        if not request.user.is_authenticated:
            #Przechowywanie id produktu w sesji
            if 'cart_items' not in request.session:
                request.session['cart_items'] = []

            cart_items = request.session['cart_items']
            for item in cart_items:
                if item['pk'] == pk and item['size'] == size:
                    item['quantity'] += 1
                    break

            #Dodanie produktu do sesji
            cart_items.append({"pk": pk, "size": size})
            request.session['cart_items'] = cart_items
            request.session.modified = True

            #Przekierowanie do strony logowania
            return redirect(f'{self.login_url}?next={reverse("cart_details", kwargs={"pk": pk})}')



        # Pobranie lub stworzenie koszyka dla zalogowanego użytkownika
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, size=size)

        # Obliczenie całkowitej ilości produktów w koszyku niezależnie od rozmiaru
        total_quantity_in_cart = CartItem.objects.filter(cart=cart, product=product).aggregate(
            total_quantity=models.Sum('quantity')
        )['total_quantity'] or 0

        if total_quantity_in_cart + 1 > product.stock:
            messages.error(request, f"Ilość {product.name} w koszyku przekracza ilość dostępną w magazynie.")
            return redirect(reverse('cart_details', kwargs={'pk': cart.pk}))

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
                    product = cart_item.product
                    # Obliczenie całkowitej ilości produktów w koszyku niezależnie od rozmiaru
                    total_quantity_in_cart = CartItem.objects.filter(cart=cart, product=product).aggregate(
                        total_quantity=models.Sum('quantity')
                    )['total_quantity'] or 0

                    planned_total_quantity = total_quantity_in_cart + int(quantity)

                    if planned_total_quantity > product.stock:
                        messages.error(request, f"Ilość {product.name} w koszyku przekracza ilość dostępną w magazynie.")
                        return redirect(reverse('cart_details', kwargs={'pk': cart.pk}))

                    cart_item.quantity = int(quantity)  # Zaktualizuj ilość "quantity"
                    cart_item.save()

        messages.success(request, "Koszyk został zaktualizowany.")
        return redirect(reverse('cart_details', kwargs={'pk': cart.pk}))


class RemoveFromCart(LoginRequiredMixin, DetailView):
    model = CartItem

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        cart_pk = self.object.cart.pk
        self.object.delete()
        return redirect(reverse('cart_details', kwargs={'pk': cart_pk}))
