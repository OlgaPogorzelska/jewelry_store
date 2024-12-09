from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, CreateView, UpdateView, DeleteView, ListView
from shop.forms import RegistrationUserForm


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
