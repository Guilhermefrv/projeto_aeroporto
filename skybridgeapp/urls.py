from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('acesso/', views.auth_home, name='auth_home'),
    path('voos/buscar/', views.buscar_voos, name='buscar_voos'),
    path('voos/<int:voo_id>/', views.detalhe_voo, name='detalhe_voo'),
    path('voos/<int:voo_id>/selecionar/', views.selecionar_voo, name='selecionar_voo'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.SkyBridgeLoginView.as_view(), name='login'),
    path('logout/', views.SkyBridgeLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard_router, name='dashboard'),
    path('dashboard/passageiro/', views.dashboard_passageiro, name='dashboard_passageiro'),
    path('dashboard/funcionario/', views.dashboard_funcionario, name='dashboard_funcionario'),
    path('dashboard/administrador/', views.dashboard_administrador, name='dashboard_administrador'),
]
