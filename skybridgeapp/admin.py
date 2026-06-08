from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    UsuarioCustomizado, Passageiro, Funcionario, Administrador,
    Aeroporto, CompanhiaAerea, Aeronave, Voo, Tarifa, Promocao, Reserva,
    Pagamento, Bilhete, Bagagem, CheckIn, PortaoEmbarque, Notificacao,
    ContaMilhas, TransacaoMilhas,
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


@admin.register(ContaMilhas)
class ContaMilhasAdmin(admin.ModelAdmin):
    list_display = ['numero_programa', 'passageiro', 'saldo']
    search_fields = ['numero_programa', 'passageiro__nome']


@admin.register(TransacaoMilhas)
class TransacaoMilhasAdmin(admin.ModelAdmin):
    list_display = ['conta', 'tipo', 'quantidade', 'data']
    list_filter = ['tipo']
    search_fields = ['conta__numero_programa', 'descricao']


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo', 'matricula', 'contato']
    list_filter = ['cargo']
    search_fields = ['nome', 'matricula']


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'login', 'nivel_acesso']
    exclude = ['senha']
    readonly_fields = ['nome', 'login', 'nivel_acesso']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff


# ──────────────────────────────────────────
#  Domínio Aeroportuário
# ──────────────────────────────────────────

@admin.register(Aeroporto)
class AeroportoAdmin(admin.ModelAdmin):
    list_display = ['codigo_iata', 'nome', 'cidade', 'pais']
    search_fields = ['codigo_iata', 'nome', 'cidade', 'pais']
    list_filter = ['pais']


@admin.register(CompanhiaAerea)
class CompanhiaAereaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo_iata', 'pais']
    search_fields = ['nome', 'codigo_iata', 'pais']
    list_filter = ['pais']


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


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ['voo', 'classe', 'preco_base', 'taxas', 'ativa']
    list_filter = ['classe', 'ativa']
    search_fields = ['voo__numero_voo']


@admin.register(Promocao)
class PromocaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'origem', 'destino', 'preco_a_partir_de', 'data_inicio', 'data_fim', 'ativa']
    list_filter = ['ativa', 'data_inicio', 'data_fim']
    search_fields = ['titulo', 'origem__codigo_iata', 'destino__codigo_iata']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'passageiro', 'voo', 'assento', 'status']
    list_filter = ['status']
    search_fields = ['passageiro__nome', 'voo__numero_voo']


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'valor_total', 'metodo', 'status', 'data_pagamento']
    list_filter = ['metodo', 'status']
    search_fields = ['reserva__passageiro__nome', 'reserva__voo__numero_voo']


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
