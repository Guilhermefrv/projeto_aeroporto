from django.db import migrations


def promover_administradores(apps, schema_editor):
    UsuarioCustomizado = apps.get_model('skybridgeapp', 'UsuarioCustomizado')
    UsuarioCustomizado.objects.filter(tipo='administrador').update(
        is_staff=True,
        is_superuser=True,
    )


def manter_permissoes(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('skybridgeapp', '0003_reserva_pagamento'),
    ]

    operations = [
        migrations.RunPython(promover_administradores, manter_permissoes),
    ]
