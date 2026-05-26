from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('acesso/', views.auth_home, name='auth_home'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.SkyBridgeLoginView.as_view(), name='login'),
    path('logout/', views.SkyBridgeLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
