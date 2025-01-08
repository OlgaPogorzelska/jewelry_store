from decimal import Decimal

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models, transaction
from cart.models import Cart, CartItem, Order, Shipping, OrderItem
from shop.models import Product, CustomerUser


class AddToCart(View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        product = get_object_or_404(Product, pk=pk)

        size = request.POST.get('size') if product.category.name == "PIERŚCIONKI" else None
        # Sprawdzenie, czy użytkownik jest zalogowany

        if not request.user.is_authenticated:
            # Przechowywanie id produktu w sesji
            if 'cart_items' not in request.session:
                request.session['cart_items'] = []

            cart_items = request.session['cart_items']
            for item in cart_items:
                if item['pk'] == pk and item['size'] == size:
                    item['quantity'] += 1
                    break

            # Dodanie produktu do sesji
            cart_items.append({"pk": pk, "size": size})
            request.session['cart_items'] = cart_items
            request.session.modified = True

            # Przekierowanie do strony logowania
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
        context['shipping_options'] = [
            {'code': 'PP', 'name': 'Poczta Polska', 'price': 15},
            {'code': 'IN', 'name': 'InPost', 'price': 18},
            {'code': 'DP', 'name': 'DPD', 'price': 20},
        ]

        selected_shipping_code = self.request.session.get('shipping_company')
        selected_shipping_price = next((option['price'] for option in context['shipping_options']
                                        if option['code'] == selected_shipping_code), 0)

        context['total_price_with_shipping'] = context['cart'].get_total_price_cart() + selected_shipping_price

        # order = Order.objects.filter(cart=self.object).first()
        # context['order'] = order  # Dodaj zamowienie do kontekstu
        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        cart = get_object_or_404(Cart, pk=pk)

        # Aktualizacja ilości produktów w koszyku
        for key in request.POST:
            if key.startswith('quantity_'):
                index = key.split('_')[1]
                quantity = request.POST[key]
                item_pk = request.POST.get(f'item_pk_{index}')  # Identyfikator elementu

                if quantity and item_pk:
                    cart_item = get_object_or_404(CartItem, pk=item_pk)
                    product = cart_item.product

                    # Obliczenie całkowitej ilości produktów w koszyku niezależnie od rozmiaru
                    total_quantity_in_cart = \
                        CartItem.objects.filter(cart=cart, product=product).exclude(pk=item_pk).aggregate(
                            total_quantity=models.Sum('quantity')
                        )['total_quantity'] or 0

                    planned_total_quantity = total_quantity_in_cart + int(quantity)

                    if planned_total_quantity > product.stock:
                        messages.error(request,
                                       f"Ilość {product.name} w koszyku przekracza ilość dostępną w magazynie.")
                        return redirect(reverse('cart_details', kwargs={'pk': cart.pk}))

                    cart_item.quantity = int(quantity)  # Zaktualizuj ilość "quantity"
                    cart_item.save()
                    print(f"Updated {cart_item.product.name} quantity to {cart_item.quantity}")

        selected_shipping = request.POST.get('shipping_company')
        if selected_shipping:
            request.session['shipping_company'] = selected_shipping
            if selected_shipping == 'PP':
                request.session['shipping_price'] = 15
            elif selected_shipping == 'IN':
                request.session['shipping_price'] = 18
            elif selected_shipping == 'DP':
                request.session['shipping_price'] = 20
            messages.success(request, f"Wybrano firmę kurierską: {selected_shipping}")
            print(f"Wybrano firmę kurierską: {selected_shipping}")

        messages.success(request, "Koszyk został zaktualizowany.")
        if 'order' in request.POST:
            print("Finalize order triggered")
            return redirect(reverse('order_details', kwargs={'pk': cart.pk}))
        else:
            print("Finalize order not found in POST")
        print(request.POST)
        return redirect(reverse('cart_details', kwargs={'pk': cart.pk}))


class RemoveFromCart(LoginRequiredMixin, DetailView):
    model = CartItem

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        cart_pk = self.object.cart.pk
        self.object.delete()
        return redirect(reverse('cart_details', kwargs={'pk': cart_pk}))


class OrderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart_pk = kwargs['pk']
        cart = get_object_or_404(Cart, pk=cart_pk)

        shipping_price = request.session.get('shipping_price')
        total_price_with_shipping = cart.get_total_price_cart() + Decimal(shipping_price)

        return render(request, 'cart/order.html', {
            'cart': cart,
            'shipping_company': request.session.get('shipping_company'),
            'cart_items': CartItem.objects.filter(cart=cart),
            'total_price_with_shipping': total_price_with_shipping,
            'user_id': request.user.pk
        })

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        cart_pk = kwargs['pk']
        cart = get_object_or_404(Cart, pk=cart_pk)
        # Oblicz całkowitą cenę z przedmiotów w koszyku
        total_price = cart.get_total_price_cart()

        # Tworzenie zamówienia
        order = Order.objects.create(user=request.user, cart=cart, total_price=total_price)

        # Sprawdź czy są elementy w koszyku
        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            return redirect(reverse_lazy('main_view'))  # Przekierowanie jeśli brak elementów

        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity,
                                     price=item.get_total_price())

            # Zaktualizowanie stanu magazynowego produktów po zakupie
            product = item.product
            product.stock -= item.quantity
            product.save()

        # Zbieranie danych o wysyłce z formularza (upewnij się, że te dane są dostępne)
        shipping_company = request.session.get('shipping_company')

        if shipping_company:
            Shipping.objects.create(user=request.user, order=order, shipping_company=shipping_company)

        # Usunięcie wszystkich elementów koszyka
        cart_items.delete()

        return redirect(reverse_lazy('main_view'))


class ShippingDetailsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Przekierowanie do edycji danych użytkownika
        return redirect(reverse('user_details') + f"?next={reverse('order_details', kwargs={'pk': self.kwargs['pk']})}")


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'cart/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class UserOrderDetailsView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'cart/order_details.html'  # Ścieżka do szablonu szczegółów zamówienia
    context_object_name = 'order'

    def get_queryset(self):
        # Filtruj zamówienia tylko dla zalogowanego użytkownika
        return Order.objects.filter(user=self.request.user)

    def get_object(self):
        # Użyj order_pk z URL do pobrania zamówienia
        order_pk = self.kwargs.get('order_pk')
        order = get_object_or_404(Order, pk=order_pk, user=self.request.user)  # Tylko dla zalogowanego użytkownika
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()

        # Upewnij się, że zamówienie ma przypisany koszyk
        if not order.cart:
            raise Http404("Zamówienie nie ma przypisanego koszyka.")

        # Dodaj szczegóły zamówienia do kontekstu
        context['order_items'] = OrderItem.objects.filter(order=order)
        context['shipping'] = Shipping.objects.filter(order=order).first()

        return context
