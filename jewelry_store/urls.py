"""
URL configuration for jewelry_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views

from shop import views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.StartView.as_view(), name='main_view'),
    path('register/', views.RegistrationView.as_view(), name='register_view'),
    path('login/', views.UserLoginView.as_view(), name='login_view'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('user/<int:pk>', views.UserDetailsView.as_view(), name='user_details'),
    path('edit_user/<int:pk>', views.UserUpdateView.as_view(), name='update_user'),
    path('change_pwd/', views.ChangeUserPasswordView.as_view(), name='change_password'),
    # path('category/', views.CategoryView.as_view(), name='category'),
    path('category/<int:pk>', views.ProductsListView.as_view(), name='products_list'),
    path('product/<int:pk>', views.ProductView.as_view(), name='product_details'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)