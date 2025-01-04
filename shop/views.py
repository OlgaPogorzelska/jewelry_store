from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, FormView, ListView, DetailView, UpdateView
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from shop.forms import RegistrationUserForm, UserLoginForm, SearchForm
from shop.models import CustomerUser, Category, Product, ProductImages, SIZE
from cart.models import Cart, CartItem


class StartView(View):
    """
        Main View
    """

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        return render(request, 'shop/base.html', {'categories': categories})


class RegistrationView(CreateView):
    form_class = RegistrationUserForm
    template_name = 'shop/registration.html'
    success_url = reverse_lazy('main_view')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)


class UserLoginView(FormView):
    form_class = UserLoginForm
    template_name = 'shop/login.html'
    success_url = reverse_lazy('main_view')

    def form_valid(self, form):
        login(self.request, form.user)

        #Dodanie produktów z sesji do koszyka
        if 'cart_items' in self.request.session:
            cart_items = self.request.session['cart_items']
            print(self.request.session.get('cart_items', []))
            cart, carted = Cart.objects.get_or_create(user=form.user)
            for item_data in cart_items:
                item_id = item_data.get('pk')
                size = item_data.get('size')
                product = get_object_or_404(Product, pk=item_id)
                CartItem.objects.create(cart=cart, product=product, size=size)

            print(f"Added products from session to cart for user {form.user.email}")
            #Po dodaniu produktów do koszyka usuwa z sesji
            del self.request.session['cart_items']


        next_url = self.request.GET.get('next')
        cart = Cart.objects.get(user=form.user)
        if next_url:
            return redirect(reverse('cart_details', kwargs={'pk': cart.pk}))
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('main_view')


class UserDetailsView(LoginRequiredMixin, DetailView):
    model = CustomerUser
    template_name = 'shop/user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object()
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):  # Dodać PermissionRequiredMixin ?
    model = CustomerUser
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'street',
              'house_number', 'apartment_number', 'city', 'postal_code',
              'country']
    template_name = 'shop/update_user.html'
    success_url = reverse_lazy('main_view')


class ChangeUserPasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'shop/change_pwd.html'
    success_url = reverse_lazy('main_view')


# class ResetUserPasswordView(PasswordResetView): Do zrobienia pózniej
#     template_name = 'shop/reset_pwd.html'
#     success_url = reverse_lazy('main_view')


# class CategoryView(ListView):
#     model = Category
#     context_object_name = 'categories'
#     template_name = 'shop/category.html'
#

class ProductsListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_id = self.kwargs['pk']  # Pobranie ID kategorii z URL
        return Product.objects.filter(category_id=category_id).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(pk=self.kwargs['pk'])
        context['category'] = self.get_object()
        return context

    def get_object(self, queryset=None):
        return Category.objects.get(pk=self.kwargs['pk'])


class ProductView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['product'] = self.get_object() nie potrzebuje bo DetailView sama mi to zrobi
        context['images'] = ProductImages.objects.filter(product=self.object)
        context['SIZE'] = SIZE
        return context


class SearchFormView(View):
    def get(self, request, *args, **kwargs):
        form = SearchForm()
        return render(request, 'shop/search.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            products = Product.objects.filter(name__icontains=search)
            categories = Category.objects.filter(name__icontains=search)
            form = SearchForm()
            return render(request, 'shop/search.html', {'form': form, 'products': products, 'categories': categories})
        return render(request, 'shop/search.html', {'form': form})