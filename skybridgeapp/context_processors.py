def notificacoes_nao_lidas(request):
    user = getattr(request, 'user', None)

    if not user or not user.is_authenticated:
        return {'notificacoes_nao_lidas': 0}

    passageiro = getattr(user, 'passageiro', None)
    if not passageiro:
        return {'notificacoes_nao_lidas': 0}

    from .models import Notificacao

    total = Notificacao.objects.filter(
        passageiro=passageiro,
        lida=False,
    ).count()

    return {'notificacoes_nao_lidas': total}
