from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, ListView, DetailView, UpdateView
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from shop.forms import RegistrationUserForm, UserLoginForm
from shop.models import CustomerUser


class StartView(View):
    """
        Main View
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'shop/main.html')


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
