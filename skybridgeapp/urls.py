from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('acesso/', views.auth_home, name='auth_home'),
    path('login/', views.login_view, name='login'),
]
