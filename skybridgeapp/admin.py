from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    UsuarioCustomizado, Passageiro, Funcionario, Administrador,
    Aeronave, Voo, Reserva, Bilhete, Bagagem, CheckIn, PortaoEmbarque, Notificacao,
)


# ──────────────────────────────────────────
#  Usuário Customizado
# ──────────────────────────────────────────

@admin.register(UsuarioCustomizado)
class UsuarioCustomizadoAdmin(UserAdmin):
    """Admin do usuário com campo 'tipo' visível e filtrável."""
    fieldsets = UserAdmin.fieldsets + (
        ('Tipo de Usuário', {'fields': ('tipo',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Tipo de Usuário', {'fields': ('tipo',)}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo', 'is_active', 'is_staff']
    list_filter = ['tipo', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']


# ──────────────────────────────────────────
#  Perfis de Usuário
# ──────────────────────────────────────────

@admin.register(Passageiro)
class PassageiroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf_passaporte', 'nacionalidade', 'contato']
    search_fields = ['nome', 'cpf_passaporte']


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo', 'matricula', 'contato']
    list_filter = ['cargo']
    search_fields = ['nome', 'matricula']


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'login', 'nivel_acesso']


# ──────────────────────────────────────────
#  Domínio Aeroportuário
# ──────────────────────────────────────────

@admin.register(Aeronave)
class AeronaveAdmin(admin.ModelAdmin):
    list_display = ['modelo', 'companhia_aerea', 'capacidade']
    search_fields = ['modelo', 'companhia_aerea']


@admin.register(PortaoEmbarque)
class PortaoEmbarqueAdmin(admin.ModelAdmin):
    list_display = ['numero_portao', 'localizacao', 'status']
    list_filter = ['status']


@admin.register(Voo)
class VooAdmin(admin.ModelAdmin):
    list_display = ['numero_voo', 'origem', 'destino', 'partida', 'status', 'aeronave', 'portao']
    list_filter = ['status']
    search_fields = ['numero_voo', 'origem', 'destino']
    ordering = ['partida']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'passageiro', 'voo', 'assento', 'status']
    list_filter = ['status']
    search_fields = ['passageiro__nome', 'voo__numero_voo']


@admin.register(Bilhete)
class BilheteAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'reserva', 'data_emissao']
    search_fields = ['codigo']


@admin.register(Bagagem)
class BagagemAdmin(admin.ModelAdmin):
    list_display = ['numero_rastreio', 'reserva', 'peso', 'status']
    list_filter = ['status']
    search_fields = ['numero_rastreio']


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['id', 'passageiro', 'voo', 'data_hora', 'status']
    list_filter = ['status']


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['passageiro', 'tipo', 'data_hora', 'lida']
    list_filter = ['tipo', 'lida']
    search_fields = ['passageiro__nome', 'mensagem']
