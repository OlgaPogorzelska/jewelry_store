from django.shortcuts import render
from django.views import View


class StartView(View):
    """
        Main View
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'base.html')
