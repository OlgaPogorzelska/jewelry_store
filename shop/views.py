from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView
from django.contrib.auth import login, logout
from shop.forms import RegistrationUserForm, UserLoginForm


class StartView(View):
    """
        Main View
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'base.html')


class RegistrationView(CreateView):
    form_class = RegistrationUserForm
    template_name = 'registration.html'
    success_url = reverse_lazy('base_view')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)


class UserLoginView(FormView):
    form_class = UserLoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('base_view')

    def form_valid(self, form):
        login(self.request, form.user)
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login_view')
