from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, FormView, ListView, DetailView, UpdateView
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from shop.forms import RegistrationUserForm, UserLoginForm, SearchForm
from shop.models import CustomerUser, Category, Product, ProductImages, SIZE
from cart.models import Cart, CartItem, Order


class StartView(View):
    """
        Main View
    """

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        cart = None
        form = SearchForm()
        if request.user.is_authenticated:
            cart, carted = Cart.objects.get_or_create(user=request.user)
        return render(request, 'shop/base.html', {
            'categories': categories,
            'cart': cart,
            'form': form,
            'home_banner': True
        })


class AboutUsView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        return render(request, 'shop/about_us.html', {
            'categories': categories,
            'is_home': True
        })


class CareView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        return render(request, 'shop/care.html', {
            'categories': categories,
            'is_home': True
        })


class ContactView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        return render(request, 'shop/contact.html', {
            'categories': categories,
            'is_home': True
        })


class SizeView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        return render(request, 'shop/size.html', {
            'categories': categories,
            'is_home': True
        })


class RegistrationView(CreateView):
    form_class = RegistrationUserForm
    template_name = 'shop/registration.html'
    success_url = reverse_lazy('main_view')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Dodanie kategorii do kontekstu
        return context


class UserLoginView(FormView):
    form_class = UserLoginForm
    template_name = 'shop/login.html'
    success_url = reverse_lazy('main_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        return context

    def form_valid(self, form):
        login(self.request, form.user)
        cart, created = Cart.objects.get_or_create(user=form.user)

        # Dodanie produktów z sesji do koszyka
        if 'cart_items' in self.request.session:
            cart_items = self.request.session['cart_items']
            for item_data in cart_items:
                item_id = item_data.get('pk')
                size = item_data.get('size')
                product = get_object_or_404(Product, pk=item_id)
                CartItem.objects.create(cart=cart, product=product, size=size)

            # Po dodaniu produktów do koszyka usuwa z sesji
            del self.request.session['cart_items']

        next_url = self.request.GET.get('next')
        cart = Cart.objects.get(user=form.user)
        if next_url:
            return redirect(reverse('cart_details', kwargs={'pk': cart.pk}))
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Login failed.")
        return super().form_invalid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('main_view')


class UserDetailsView(LoginRequiredMixin, DetailView):
    model = CustomerUser
    template_name = 'shop/user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.filter(user=self.request.user).first()
        categories = Category.objects.all()
        context['categories'] = categories
        context['cart'] = cart
        context['user'] = self.get_object()
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomerUser
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'street',
              'house_number', 'apartment_number', 'city', 'postal_code',
              'country']
    template_name = 'shop/update_user.html'
    success_url = reverse_lazy('main_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.filter(user=self.request.user).first()
        categories = Category.objects.all()
        context['categories'] = categories
        context['cart'] = cart
        context['hide_menu'] = False
        context['form_order'] = 'next' in self.request.GET
        context['minimal_header'] = 'next' in self.request.GET
        context['order_id'] = self.request.GET.get('next')
        return context

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('main_view')

    def get_object(self, queryset=None):
        # Jeśli użytkownik nie jest właścicielem konta, zgłoś błąd 404
        obj = super().get_object(queryset)
        if obj != self.request.user:
            raise Http404("You are not allowed to edit this user's data.")
        return obj


class ChangeUserPasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'shop/change_pwd.html'
    success_url = reverse_lazy('main_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.filter(user=self.request.user).first()
        context['cart'] = cart
        categories = Category.objects.all()
        context['categories'] = categories
        return context


class ProductsListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_id = self.kwargs['pk']  # Pobranie ID kategorii z URL
        return Product.objects.filter(category_id=category_id).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        # Sprawdzenie, czy użytkownik jest zalogowany
        if self.request.user.is_authenticated:
            # Jeżeli użytkownik jest zalogowany, pobierz koszyk
            cart = Cart.objects.filter(user=self.request.user).first()
        else:
            # Jeśli użytkownik nie jest zalogowany, ustaw pusty koszyk lub przekieruj
            cart = None  # lub: cart = Cart.objects.none()
        context['categories'] = categories
        return context


class ProductView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        # Sprawdzenie, czy użytkownik jest zalogowany
        if self.request.user.is_authenticated:
            # Jeżeli użytkownik jest zalogowany, pobierz koszyk
            cart = Cart.objects.filter(user=self.request.user).first()
        else:
            # Jeśli użytkownik nie jest zalogowany, ustaw pusty koszyk lub przekieruj
            cart = None  # lub: cart = Cart.objects.none()
        # context['product'] = self.get_object() nie potrzebuje bo DetailView sama mi to zrobi
        context['images'] = ProductImages.objects.filter(product=self.object)
        context['SIZE'] = SIZE
        context['categories'] = categories
        context['banner_hide'] = True
        return context


class SearchFormView(View):
    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)
        categories_menu = Category.objects.all()

        if form.is_valid():
            search = form.cleaned_data['search']
            # Wyszukiwanie po nazwie i opisie
            products = Product.objects.filter(name__icontains=search) | Product.objects.filter(
                description__icontains=search)

            form = SearchForm()  # Reset formularza
            return render(request, 'shop/search.html', {
                'form': form,
                'products': products,
                'categories': categories_menu
            })

        return render(request, 'shop/search.html', {
            'form': form,
            'categories': categories_menu
        })
