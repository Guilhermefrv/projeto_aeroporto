from django.contrib import admin
from .models import Passageiro, Funcionario, Administrador, Voo, Aeronave, Reserva, Bilhete, Bagagem, CheckIn, PortaoEmbarque, Notificacao


admin.site.register(Passageiro)
admin.site.register(Funcionario)
admin.site.register(Administrador)
admin.site.register(Voo)
admin.site.register(Aeronave)
admin.site.register(Reserva)
admin.site.register(Bilhete)
admin.site.register(Bagagem)
admin.site.register(CheckIn)
admin.site.register(PortaoEmbarque)
admin.site.register(Notificacao)
