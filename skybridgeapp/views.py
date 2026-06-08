import random
import uuid
from datetime import timedelta
from decimal import Decimal
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    AtualizarVooOperacionalForm,
    BuscaVooForm,
    CadastroAdministradorForm,
    CadastroFuncionarioForm,
    CadastroPassageiroForm,
    PagamentoForm,
    SelecionarVooForm,
)
from .models import Bagagem, Bilhete, CheckIn, ContaMilhas, Funcionario, Notificacao, Pagamento, Passageiro, PortaoEmbarque, Promocao, Reserva, Tarifa, TransacaoMilhas, Voo


LANDING_CONTEXT = {
    'asset_version': '20260608-date-carousel',
    'nav_items': [
        'Comprar',
        'Minhas viagens',
        'Check-in',
        'Status de voo',
        'Sky Pass',
        'Ajuda',
    ],
    'search_tabs': [
        {'label': 'Voos', 'active': True},
        {'label': 'Pacotes'},
        {'label': 'Hotéis'},
        {'label': 'Carros'},
    ],
    'search_fields': [
        {'label': 'Origem', 'value': 'GRU - São Paulo', 'aria_label': 'Selecionar origem nacional'},
        {'label': 'Destino', 'value': 'Destino nacional', 'aria_label': 'Selecionar destino nacional'},
        {'label': 'Ida', 'value': 'Escolher data', 'aria_label': 'Selecionar data de ida'},
        {'label': 'Volta', 'value': 'Escolher data', 'aria_label': 'Selecionar data de volta'},
        {'label': 'Passageiros', 'value': '1 adulto', 'aria_label': 'Selecionar passageiros'},
        {'label': 'Cabine', 'value': 'Econômica', 'aria_label': 'Selecionar cabine'},
        {
            'label': 'Código promocional',
            'value': 'Adicionar',
            'aria_label': 'Adicionar código promocional',
            'wide': True,
        },
    ],
    'payment_options': [
        {'label': 'Usar milhas', 'active': True},
        {'label': 'Milhas + dinheiro'},
    ],
    'domestic_airports': [
        {'code': 'GRU', 'city': 'São Paulo', 'name': 'Guarulhos', 'region': 'Sudeste'},
        {'code': 'CWB', 'city': 'Curitiba', 'name': 'Afonso Pena', 'region': 'Sul'},
        {'code': 'REC', 'city': 'Recife', 'name': 'Guararapes', 'region': 'Nordeste'},
        {'code': 'MAO', 'city': 'Manaus', 'name': 'Eduardo Gomes', 'region': 'Norte'},
        {'code': 'BSB', 'city': 'Brasília', 'name': 'Presidente Juscelino Kubitschek', 'region': 'Centro-Oeste'},
    ],
    'offer_filters': [
        {'label': 'Todos os destinos', 'active': True},
        {'label': 'Nacionais'},
        {'label': 'Menor preço'},
        {'label': 'Voos diretos'},
        {'label': 'Voos com conexão'},
    ],
    'offers': [
        {
            'image_class': 'offer-rio',
            'image_url': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=900&q=80',
            'route': 'São Paulo → Rio de Janeiro',
            'title': 'Escapada urbana à beira-mar',
            'description': 'Voos selecionados com taxas incluídas.',
            'price': 'R$ 189',
        },
        {
            'image_class': 'offer-recife',
            'image_url': 'https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=900&q=80',
            'route': 'São Paulo → Recife',
            'title': 'Praias e cultura no Nordeste',
            'description': 'Condições especiais em datas selecionadas.',
            'price': 'R$ 329',
        },
        {
            'image_class': 'offer-salvador',
            'image_url': 'https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=900&q=80',
            'route': 'São Paulo → Salvador',
            'title': 'Sol, música e centro histórico',
            'description': 'Tarifas promocionais para ida e volta.',
            'price': 'R$ 299',
        },
        {
            'image_class': 'offer-manaus',
            'image_url': '/static/img/offers/manaus.jpg',
            'route': 'São Paulo → Manaus',
            'title': 'Amazônia e cultura no Norte',
            'description': 'Trechos nacionais com opções em datas selecionadas.',
            'price': 'R$ 549',
        },
        {
            'image_class': 'offer-curitiba',
            'image_url': '/static/img/offers/curitiba.jpg',
            'route': 'São Paulo → Curitiba',
            'title': 'Fim de semana no Sul',
            'description': 'Rotas nacionais para viagens rápidas e flexíveis.',
            'price': 'R$ 219',
        },
        {
            'image_class': 'offer-brasilia',
            'image_url': '/static/img/offers/brasilia.jpg',
            'route': 'São Paulo → Brasília',
            'title': 'Conexão com o Centro-Oeste',
            'description': 'Ofertas para a capital federal com taxas incluídas.',
            'price': 'R$ 289',
        },
        {
            'image_class': 'offer-belem',
            'image_url': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80',
            'route': 'São Paulo → Belém',
            'title': 'Sabores e rios do Pará',
            'description': 'Destinos nacionais para explorar o Norte do Brasil.',
            'price': 'R$ 579',
        },
        {
            'image_class': 'offer-porto-alegre',
            'image_url': '/static/img/offers/porto-alegre.jpg',
            'route': 'São Paulo → Porto Alegre',
            'title': 'Cultura e gastronomia no Sul',
            'description': 'Trechos nacionais com tarifas promocionais.',
            'price': 'R$ 259',
        },
        {
            'image_class': 'offer-cuiaba',
            'image_url': '/static/img/offers/cuiaba.jpg',
            'route': 'São Paulo → Cuiabá',
            'title': 'Porta de entrada para o Pantanal',
            'description': 'Preços finais para voos dentro do Brasil.',
            'price': 'R$ 399',
        },
    ],
    'benefits': [
        {
            'icon': 'fa-solid fa-shield-halved',
            'title': 'Compra segura',
            'description': 'Ambiente protegido para consultar ofertas e escolher serviços.',
        },
        {
            'icon': 'fa-solid fa-receipt',
            'title': 'Taxas incluídas',
            'description': 'Cards com preços finais apresentados de forma clara.',
        },
        {
            'icon': 'fa-solid fa-star',
            'title': 'Acumule pontos',
            'description': 'Planeje viagens considerando benefícios e programa de fidelidade.',
        },
        {
            'icon': 'fa-solid fa-suitcase-rolling',
            'title': 'Gerencie sua viagem',
            'description': 'Acompanhe reservas, serviços e preferências em um só lugar.',
        },
        {
            'icon': 'fa-solid fa-headset',
            'title': 'Atendimento e suporte',
            'description': 'Encontre ajuda para dúvidas antes, durante e depois do voo.',
        },
        {
            'icon': 'fa-solid fa-circle-check',
            'title': 'Check-in online',
            'description': 'Tenha uma experiência mais rápida quando sua viagem estiver próxima.',
        },
    ],
    'footer_columns': [
        {
            'title': 'Sobre a empresa',
            'links': ['Quem somos', 'Trabalhe conosco', 'Sustentabilidade'],
        },
        {
            'title': 'Central de ajuda',
            'links': ['Atendimento', 'Bagagem', 'Alterações de viagem'],
        },
        {
            'title': 'Informações legais',
            'links': ['Termos e condições', 'Política de privacidade', 'Informações legais'],
        },
    ],
    'social_links': [
        {'label': 'Instagram', 'icon': 'fa-brands fa-instagram'},
        {'label': 'Facebook', 'icon': 'fa-brands fa-facebook-f'},
        {'label': 'YouTube', 'icon': 'fa-brands fa-youtube'},
    ],
}

PAYMENT_METHODS = [
    {
        'value': 'pix',
        'label': 'Pix',
        'icon': 'fa-solid fa-qrcode',
        'description': 'Confirmação imediata para liberar a reserva.',
    },
    {
        'value': 'cartao',
        'label': 'Cartão',
        'icon': 'fa-solid fa-credit-card',
        'description': 'Pagamento por cartão de crédito ou débito.',
    },
    {
        'value': 'boleto',
        'label': 'Boleto',
        'icon': 'fa-solid fa-receipt',
        'description': 'Geração simulada com aprovação na confirmação.',
    },
    {
        'value': 'milhas',
        'label': 'Milhas',
        'icon': 'fa-solid fa-star',
        'description': 'Use seu saldo de fidelidade para a compra.',
    },
]


PROMOTION_IMAGE_DATA = {
    'GRU': {
        'image_class': 'offer-sao-paulo',
        'image_url': 'https://images.unsplash.com/photo-1744771070810-886638822097?auto=format&fit=crop&w=900&q=80',
    },
    'GIG': {
        'image_class': 'offer-rio',
        'image_url': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=900&q=80',
    },
    'REC': {
        'image_class': 'offer-recife',
        'image_url': 'https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=900&q=80',
    },
    'SSA': {
        'image_class': 'offer-salvador',
        'image_url': 'https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=900&q=80',
    },
    'MAO': {
        'image_class': 'offer-manaus',
        'image_url': '/static/img/offers/manaus.jpg',
    },
    'CWB': {
        'image_class': 'offer-curitiba',
        'image_url': '/static/img/offers/curitiba.jpg',
    },
    'BSB': {
        'image_class': 'offer-brasilia',
        'image_url': '/static/img/offers/brasilia.jpg',
    },
    'BEL': {
        'image_class': 'offer-belem',
        'image_url': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80',
    },
    'POA': {
        'image_class': 'offer-porto-alegre',
        'image_url': '/static/img/offers/porto-alegre.jpg',
    },
    'CGB': {
        'image_class': 'offer-cuiaba',
        'image_url': '/static/img/offers/cuiaba.jpg',
    },
}


def _airport_city_or_default(aeroporto, default):
    if aeroporto:
        return aeroporto.cidade
    return default


def _promotion_image_data(promocao):
    codigo_destino = promocao.destino.codigo_iata if promocao.destino else ''
    return PROMOTION_IMAGE_DATA.get(codigo_destino, {
        'image_class': 'offer-rio',
        'image_url': LANDING_CONTEXT['offers'][0]['image_url'],
    })


def _promotion_search_url(promocao):
    if not (promocao.origem_id and promocao.destino_id):
        return ''

    query = urlencode({
        'origem': promocao.origem_id,
        'destino': promocao.destino_id,
        'passageiros': 1,
    })
    return f'{reverse("buscar_voos")}?{query}'


def _promotion_to_offer(promocao):
    image_data = _promotion_image_data(promocao)
    origem = _airport_city_or_default(promocao.origem, 'Brasil')
    destino = _airport_city_or_default(promocao.destino, 'Destino nacional')

    return {
        'image_class': image_data['image_class'],
        'image_url': image_data['image_url'],
        'route': f'{origem} -> {destino}',
        'title': promocao.titulo,
        'description': promocao.descricao or 'Oferta nacional cadastrada para a landing page.',
        'price': _formatar_moeda(promocao.preco_a_partir_de),
        'search_url': _promotion_search_url(promocao),
    }


def _offers_for_home():
    promocoes = (
        Promocao.objects.filter(ativa=True)
        .select_related('origem', 'destino')
        .order_by('preco_a_partir_de', 'titulo')
    )
    ofertas_unicas = []
    rotas_exibidas = set()

    for promocao in promocoes:
        chave_rota = (
            promocao.origem_id,
            promocao.destino_id,
        ) if promocao.origem_id and promocao.destino_id else ('promocao', promocao.pk)
        if chave_rota in rotas_exibidas:
            continue
        rotas_exibidas.add(chave_rota)
        ofertas_unicas.append(promocao)

    if not ofertas_unicas:
        return LANDING_CONTEXT['offers']
    return [_promotion_to_offer(promocao) for promocao in ofertas_unicas]


def home(request):
    context = {
        **LANDING_CONTEXT,
        'offers': _offers_for_home(),
        'search_form': BuscaVooForm(),
        'route_map': _route_map(),
    }
    _add_account_context(request, context)

    return render(request, 'home.html', context)


def status_voo(request):
    numero_voo = request.GET.get('numero_voo', '').strip()
    voo = None
    erro_busca = False

    if numero_voo:
        clean_query = numero_voo.replace(' ', '').replace('-', '').upper()
        # Direct lookup (case-insensitive)
        qs = Voo.objects.select_related('aeronave', 'portao').filter(numero_voo__iexact=clean_query)
        if qs.exists():
            voo = qs.first()
        else:
            # Fallback scan of all flights (in case database values have hyphens or spaces)
            for v in Voo.objects.select_related('aeronave', 'portao').all():
                if v.numero_voo.replace(' ', '').replace('-', '').upper() == clean_query:
                    voo = v
                    break
        if not voo:
            erro_busca = True

    context = {
        'asset_version': LANDING_CONTEXT['asset_version'],
        'nav_items': LANDING_CONTEXT['nav_items'],
        'voo': voo,
        'numero_voo': numero_voo,
        'erro_busca': erro_busca,
    }
    _add_account_context(request, context)
    return render(request, 'status_voo.html', context)


def buscar_voos(request):
    form = BuscaVooForm(request.GET or None)
    voos = []
    voos_proximos = []
    datas_flexiveis = []
    date_nav = {}
    resultado_tipo = 'exato'
    filtros_resumo = []
    rota_consultada_existe = True
    cleaned_data = {}
    filtros_validos = form.is_valid() if form.is_bound else True

    if filtros_validos:
        cleaned_data = form.cleaned_data if form.is_bound else {}
        filtros_resumo = _filtros_resumo(cleaned_data)
        rota_consultada_existe = _rota_consultada_existe(cleaned_data)

        if request.GET and not rota_consultada_existe:
            resultado_tipo = 'rota_indisponivel'
        elif _deve_escolher_data(cleaned_data, request.GET):
            resultado_tipo = 'selecionar_data'
            datas_flexiveis = _datas_flexiveis(cleaned_data, request.GET)
            date_nav = _date_nav_context(cleaned_data, request.GET)
        else:
            voos = _preparar_voos_para_resultado(
                _filtrar_voos(cleaned_data),
                cleaned_data.get('classe'),
            )
            datas_flexiveis = _datas_flexiveis(cleaned_data, request.GET)
            date_nav = _date_nav_context(cleaned_data, request.GET)

            if request.GET and cleaned_data.get('data_ida') and not voos:
                voos_proximos = _voos_proximos(cleaned_data)
                if voos_proximos:
                    resultado_tipo = 'proximo'
                else:
                    resultado_tipo = 'vazio'

    voos_exibidos = voos if voos else voos_proximos

    context = {
        'asset_version': LANDING_CONTEXT['asset_version'],
        'nav_items': LANDING_CONTEXT['nav_items'],
        'search_form': form,
        'voos': voos,
        'voos_exibidos': voos_exibidos,
        'voos_proximos': voos_proximos,
        'resultado_tipo': resultado_tipo,
        'rota_consultada_existe': rota_consultada_existe,
        'datas_flexiveis': datas_flexiveis,
        'date_nav': date_nav,
        'filtros_resumo': filtros_resumo,
        'busca_realizada': bool(request.GET),
        'rotas_disponiveis': _rotas_disponiveis(cleaned_data),
        'route_map': _route_map(),
    }
    _add_account_context(request, context)

    return render(request, 'buscar_voos.html', context)


def buscar_voos_datas(request):
    form = BuscaVooForm(request.GET or None)
    if not form.is_valid():
        return JsonResponse({'error': 'Filtros invalidos.'}, status=400)

    cleaned_data = form.cleaned_data
    datas = _datas_flexiveis(cleaned_data, request.GET)
    date_nav = _date_nav_context(cleaned_data, request.GET)

    return JsonResponse({
        'dates': [_date_chip_payload(dia) for dia in datas],
        'previousUrl': date_nav.get('previous_api_url', ''),
        'nextUrl': date_nav.get('next_api_url', ''),
        'windowUrl': date_nav.get('window_url', ''),
    })


def detalhe_voo(request, voo_id):
    voo = get_object_or_404(
        Voo.objects.select_related('aeronave', 'portao'),
        pk=voo_id,
    )
    form = SelecionarVooForm(request.GET or None)
    classe = ''
    passageiros = 1

    if form.is_valid():
        classe = form.cleaned_data.get('classe') or ''
        passageiros = form.cleaned_data.get('passageiros') or 1

    voo = _preparar_voo_para_detalhe(voo, classe, passageiros)

    context = {
        'asset_version': LANDING_CONTEXT['asset_version'],
        'nav_items': LANDING_CONTEXT['nav_items'],
        'voo': voo,
        'selection_form': form,
        'passageiros': passageiros,
        'classe_selecionada': classe,
        'selecionar_url': reverse('selecionar_voo', args=[voo.id]),
    }
    _add_account_context(request, context)

    return render(request, 'detalhe_voo.html', context)


@login_required
def selecionar_voo(request, voo_id):
    get_object_or_404(Voo, pk=voo_id)
    detalhe_url = reverse('detalhe_voo', args=[voo_id])
    query_string = request.GET.urlencode()

    if query_string:
        detalhe_url = f'{detalhe_url}?{query_string}'

    return redirect(detalhe_url)


@login_required
@require_POST
def criar_reserva(request, voo_id):
    voo = get_object_or_404(Voo.objects.select_related('aeronave', 'portao'), pk=voo_id)
    form = SelecionarVooForm(request.POST)
    classe = ''
    passageiros = 1

    if form.is_valid():
        classe = form.cleaned_data.get('classe') or ''
        passageiros = form.cleaned_data.get('passageiros') or 1

    passageiro = getattr(request.user, 'passageiro', None)
    if not passageiro:
        messages.error(request, 'Complete seu cadastro de passageiro antes de reservar um voo.')
        return redirect(_detalhe_voo_url(voo.id, classe, passageiros))

    reserva = Reserva.objects.create(
        passageiro=passageiro,
        voo=voo,
        classe_tarifa=classe,
        quantidade_passageiros=passageiros,
        assento=_gerar_assento_simples(voo),
        status='pendente',
    )
    messages.success(request, 'Reserva criada com sucesso. Finalize o pagamento para confirmar a viagem.')

    return redirect('pagamento_reserva', reserva_id=reserva.id)


@login_required
def pagamento_reserva(request, reserva_id):
    reserva = get_object_or_404(
        Reserva.objects.select_related('passageiro__usuario', 'voo__aeronave', 'voo__portao'),
        pk=reserva_id,
    )

    if reserva.passageiro.usuario_id != request.user.id and not request.user.is_staff:
        return _redirect_to_user_dashboard(request.user)

    pagamento_existente = getattr(reserva, 'pagamento', None)
    if _pagamento_aprovado(pagamento_existente):
        return redirect('reserva_sucesso', reserva_id=reserva.id)

    valor_total = _valor_total_reserva(reserva)

    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            if valor_total is None:
                messages.error(request, 'Nao foi possivel calcular o valor total desta reserva.')
                return redirect(_detalhe_voo_url(reserva.voo_id, reserva.classe_tarifa, reserva.quantidade_passageiros))

            metodo = form.cleaned_data['metodo']
            if metodo == 'milhas':
                conta = _obter_ou_criar_conta_milhas(reserva.passageiro)
                milhas_necessarias = int(valor_total * 10)
                if conta.saldo < milhas_necessarias:
                    form.add_error('metodo', f"Saldo de milhas insuficiente. Necessário: {milhas_necessarias} milhas. Seu saldo: {conta.saldo} milhas.")
                else:
                    with transaction.atomic():
                        # Deduz milhas
                        conta.saldo -= milhas_necessarias
                        conta.save(update_fields=['saldo'])
                        
                        # Cria transação de resgate
                        TransacaoMilhas.objects.create(
                            conta=conta,
                            tipo='resgate',
                            quantidade=-milhas_necessarias,
                            descricao=f"Resgate para voo {reserva.voo.numero_voo} (Reserva #{reserva.id})"
                        )
                        
                        _aprovar_pagamento(reserva, metodo, valor_total)
                    messages.success(request, 'Pagamento em milhas aprovado com sucesso.')
                    return redirect('reserva_sucesso', reserva_id=reserva.id)
            else:
                with transaction.atomic():
                    # Para outros métodos, acumula milhas fictícias (1 milha por R$ 1,00 gasto)
                    conta = _obter_ou_criar_conta_milhas(reserva.passageiro)
                    milhas_acumuladas = int(valor_total)
                    conta.saldo += milhas_acumuladas
                    conta.save(update_fields=['saldo'])
                    
                    TransacaoMilhas.objects.create(
                        conta=conta,
                        tipo='acumulo',
                        quantidade=milhas_acumuladas,
                        descricao=f"Acúmulo por voo {reserva.voo.numero_voo} (Reserva #{reserva.id})"
                    )
                    
                    _aprovar_pagamento(reserva, metodo, valor_total)
                messages.success(request, 'Pagamento aprovado com sucesso.')
                return redirect('reserva_sucesso', reserva_id=reserva.id)
    else:
        metodo_inicial = pagamento_existente.metodo if pagamento_existente and pagamento_existente.metodo else PAYMENT_METHODS[0]['value']
        form = PagamentoForm(initial={'metodo': metodo_inicial})

    context = {
        'asset_version': LANDING_CONTEXT['asset_version'],
        'nav_items': LANDING_CONTEXT['nav_items'],
        'reserva': reserva,
        'pagamento_form': form,
        'metodos_pagamento': PAYMENT_METHODS,
        'valor_total': _formatar_moeda(valor_total) if valor_total is not None else None,
        'tarifa_label': dict(Tarifa.CLASSES).get(reserva.classe_tarifa, 'Menor tarifa disponivel'),
    }
    if pagamento_existente:
        context['pagamento_existente'] = pagamento_existente

    _add_account_context(request, context)

    return render(request, 'pagamento.html', context)


@login_required
def reserva_sucesso(request, reserva_id):
    reserva = get_object_or_404(
        Reserva.objects.select_related('passageiro__usuario', 'voo__aeronave', 'voo__portao', 'pagamento'),
        pk=reserva_id,
    )

    if reserva.passageiro.usuario_id != request.user.id and not request.user.is_staff:
        return _redirect_to_user_dashboard(request.user)

    pagamento = getattr(reserva, 'pagamento', None)
    if not pagamento or pagamento.status != 'aprovado':
        return redirect('pagamento_reserva', reserva_id=reserva.id)

    context = {
        'asset_version': LANDING_CONTEXT['asset_version'],
        'nav_items': LANDING_CONTEXT['nav_items'],
        'reserva': reserva,
        'pagamento': pagamento,
        'valor_total': _formatar_moeda(pagamento.valor_total),
    }
    _add_account_context(request, context)

    return render(request, 'reserva_sucesso.html', context)


@login_required
def bilhete_reserva(request, reserva_id):
    reserva = get_object_or_404(
        Reserva.objects.select_related('passageiro__usuario', 'voo__aeronave', 'voo__portao', 'pagamento', 'bilhete'),
        pk=reserva_id,
    )

    if reserva.passageiro.usuario_id != request.user.id and not request.user.is_staff:
        return _redirect_to_user_dashboard(request.user)

    bilhete = get_object_or_404(Bilhete, reserva=reserva)
    pagamento = getattr(reserva, 'pagamento', None)

    context = {
        'asset_version': LANDING_CONTEXT['asset_version'],
        'nav_items': LANDING_CONTEXT['nav_items'],
        'reserva': reserva,
        'bilhete': bilhete,
        'pagamento': pagamento,
        'valor_total': _formatar_moeda(pagamento.valor_total) if pagamento else None,
    }
    _add_account_context(request, context)

    return render(request, 'bilhete.html', context)


@login_required
def minhas_viagens(request):
    if not _can_access_dashboard(request.user, 'passageiro'):
        return _redirect_to_user_dashboard(request.user)

    passageiro = getattr(request.user, 'passageiro', None)
    reservas = []
    conta_milhas = None

    if passageiro:
        reservas = _preparar_reservas_jornada(
            passageiro.reserva_set
            .select_related('voo__aeronave', 'voo__portao', 'pagamento', 'bilhete')
            .all()
            .order_by('-id')
        )
        conta_milhas = getattr(passageiro, 'conta_milhas', None)

    context = {
        'passageiro': passageiro,
        'reservas': reservas,
        'conta_milhas': conta_milhas,
    }

    return render(request, 'minhas_viagens.html', context)


@login_required
def detalhe_reserva(request, reserva_id):
    reserva = get_object_or_404(
        Reserva.objects.select_related('passageiro__usuario', 'voo__aeronave', 'voo__portao', 'pagamento', 'bilhete'),
        pk=reserva_id,
    )

    if reserva.passageiro.usuario_id != request.user.id and not request.user.is_staff:
        return _redirect_to_user_dashboard(request.user)

    _preparar_reserva_jornada(reserva)

    return render(request, 'detalhe_reserva.html', {
        'reserva': reserva,
        'passageiro': reserva.passageiro,
    })


@login_required
@require_POST
def realizar_checkin(request, reserva_id):
    reserva = get_object_or_404(
        Reserva.objects.select_related('passageiro__usuario', 'voo__aeronave', 'voo__portao'),
        pk=reserva_id,
    )

    if reserva.passageiro.usuario_id != request.user.id and not request.user.is_staff:
        return _redirect_to_user_dashboard(request.user)

    if not _reserva_pode_checkin(reserva):
        messages.error(request, 'Check-in disponivel apenas para reservas confirmadas de voos futuros.')
        return redirect('detalhe_reserva', reserva_id=reserva.id)

    checkin = _checkin_da_reserva(reserva)
    if checkin:
        messages.info(request, 'Check-in ja realizado para esta reserva.')
    else:
        CheckIn.objects.create(
            passageiro=reserva.passageiro,
            voo=reserva.voo,
            status='realizado',
        )
        messages.success(request, 'Check-in realizado com sucesso.')

    return redirect('cartao_embarque', reserva_id=reserva.id)


@login_required
def cartao_embarque(request, reserva_id):
    reserva = get_object_or_404(
        Reserva.objects.select_related('passageiro__usuario', 'voo__aeronave', 'voo__portao', 'pagamento', 'bilhete'),
        pk=reserva_id,
    )

    if reserva.passageiro.usuario_id != request.user.id and not request.user.is_staff:
        return _redirect_to_user_dashboard(request.user)

    checkin = _checkin_da_reserva(reserva)
    if not checkin:
        messages.error(request, 'Realize o check-in antes de acessar o cartao de embarque.')
        return redirect('detalhe_reserva', reserva_id=reserva.id)

    _preparar_reserva_jornada(reserva)

    return render(request, 'cartao_embarque.html', {
        'reserva': reserva,
        'passageiro': reserva.passageiro,
        'checkin': checkin,
    })


@login_required
@require_POST
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(
        Reserva.objects.select_related('passageiro__usuario'),
        pk=reserva_id,
    )

    if reserva.passageiro.usuario_id != request.user.id and not request.user.is_staff:
        return _redirect_to_user_dashboard(request.user)

    if reserva.status != 'cancelada':
        reserva.status = 'cancelada'
        reserva.save(update_fields=['status'])
        messages.success(request, 'Reserva cancelada com sucesso.')
    else:
        messages.info(request, 'Esta reserva ja estava cancelada.')

    return redirect('detalhe_reserva', reserva_id=reserva.id)


@login_required
def notificacoes_passageiro(request):
    if not _can_access_dashboard(request.user, 'passageiro'):
        return _redirect_to_user_dashboard(request.user)

    passageiro = getattr(request.user, 'passageiro', None)
    notificacoes = []

    if passageiro:
        notificacoes = passageiro.notificacao_set.all()

    return render(request, 'notificacoes_passageiro.html', {
        'passageiro': passageiro,
        'notificacoes': notificacoes,
    })


def _pagamento_aprovado(pagamento):
    return bool(pagamento and pagamento.status == 'aprovado')


def _preparar_reservas_jornada(reservas):
    return [_preparar_reserva_jornada(reserva) for reserva in reservas]


def _preparar_reserva_jornada(reserva):
    pagamento = getattr(reserva, 'pagamento', None)
    bilhete = getattr(reserva, 'bilhete', None)
    checkin = _checkin_da_reserva(reserva)

    reserva.pagamento_jornada = pagamento
    reserva.bilhete_jornada = bilhete
    reserva.checkin_jornada = checkin
    reserva.pode_checkin = _reserva_pode_checkin(reserva) and not checkin
    reserva.pagamento_status_label = pagamento.get_status_display() if pagamento else 'Pendente'
    reserva.pagamento_status_texto = f'Pagamento {reserva.pagamento_status_label.lower()}'
    reserva.metodo_pagamento_label = pagamento.get_metodo_display() if pagamento else 'Aguardando pagamento'
    reserva.valor_total_formatado = _formatar_moeda(pagamento.valor_total) if pagamento else None

    return reserva


def _reserva_pode_checkin(reserva):
    return reserva.status == 'confirmada' and reserva.voo.partida > timezone.now()


def _checkin_da_reserva(reserva):
    return CheckIn.objects.filter(
        passageiro=reserva.passageiro,
        voo=reserva.voo,
        status='realizado',
    ).order_by('-data_hora').first()


def _valor_total_reserva(reserva):
    tarifa = _tarifa_preferida(reserva.voo, reserva.classe_tarifa or None)
    if not tarifa:
        return None

    quantidade = max(1, reserva.quantidade_passageiros or 1)
    return (tarifa.preco_base + tarifa.taxas) * quantidade


def _aprovar_pagamento(reserva, metodo, valor_total):
    Pagamento.objects.update_or_create(
        reserva=reserva,
        defaults={
            'valor_total': valor_total,
            'metodo': metodo,
            'status': 'aprovado',
            'data_pagamento': timezone.now(),
        },
    )
    reserva.status = 'confirmada'
    reserva.save(update_fields=['status'])

    # Gerar Bilhete automaticamente ao aprovar o pagamento
    codigo_bilhete = f"TKT-{reserva.id}-{uuid.uuid4().hex[:6].upper()}"
    Bilhete.objects.get_or_create(
        reserva=reserva,
        defaults={
            'codigo': codigo_bilhete
        }
    )


def _obter_ou_criar_conta_milhas(passageiro):
    try:
        return passageiro.conta_milhas
    except ContaMilhas.DoesNotExist:
        while True:
            num_programa = f"SB-{random.randint(100000, 999999)}"
            if not ContaMilhas.objects.filter(numero_programa=num_programa).exists():
                break
        return ContaMilhas.objects.create(
            passageiro=passageiro,
            saldo=10000,  # 10.000 de saldo padrão para passageiros herdados ou sem conta
            numero_programa=num_programa
        )


def auth_home(request):
    if request.user.is_authenticated:
        return redirect(_post_login_route_for_user(request.user))

    return render(request, 'auth_home.html')


CADASTRO_FORMS = {
    'passageiro': CadastroPassageiroForm,
    'funcionario': CadastroFuncionarioForm,
    'administrador': CadastroAdministradorForm,
}


def cadastro(request):
    tipo_enviado = request.POST.get('tipo_usuario') if request.method == 'POST' else None
    next_url = _safe_next_url(request)
    forms = {
        tipo: form_class(request.POST if tipo == tipo_enviado else None)
        for tipo, form_class in CADASTRO_FORMS.items()
    }
    modal_aberto = None

    if request.method == 'POST':
        form = forms.get(tipo_enviado)
        if form and form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso. Faca login para continuar.')
            return redirect(_login_url_with_next(next_url))

        if form:
            modal_aberto = tipo_enviado
        else:
            messages.error(request, 'Selecione um tipo de usuario valido.')

    return render(request, 'cadastro.html', {
        'passageiro_form': forms['passageiro'],
        'funcionario_form': forms['funcionario'],
        'administrador_form': forms['administrador'],
        'modal_aberto': modal_aberto,
        'next': next_url,
    })


def _add_account_context(request, context):
    if request.user.is_authenticated:
        context['account_dashboard_url'] = reverse(_dashboard_route_for_user(request.user))
        context['account_trips_url'] = reverse('minhas_viagens') if request.user.tipo == 'passageiro' else context['account_dashboard_url']
        context['account_notifications_url'] = reverse('notificacoes_passageiro') if request.user.tipo == 'passageiro' else context['account_dashboard_url']
        context['account_password_url'] = reverse('password_change')
        context['account_label'] = _account_label_for_user(request.user)
        context['account_initials'] = _account_initials_for_user(request.user)


def _filtrar_voos(cleaned_data):
    voos = Voo.objects.select_related('aeronave', 'portao').filter(status='programado')

    origem = cleaned_data.get('origem')
    destino = cleaned_data.get('destino')
    data_ida = cleaned_data.get('data_ida')
    classe = cleaned_data.get('classe')

    if origem:
        voos = voos.filter(_aeroporto_text_query('origem', origem))

    if destino:
        voos = voos.filter(_aeroporto_text_query('destino', destino))

    if data_ida:
        voos = voos.filter(partida__date=data_ida)

    if classe:
        voos = voos.filter(tarifas__classe=classe, tarifas__ativa=True)

    return voos.distinct().order_by('partida')


def _rotas_disponiveis(cleaned_data=None, limit=6):
    cleaned_data = cleaned_data or {}
    data_base = cleaned_data.get('data_ida') or timezone.localdate()
    origem = cleaned_data.get('origem')
    destino = cleaned_data.get('destino')

    voos = Voo.objects.filter(status='programado', partida__date__gte=data_base)
    titulo = 'Rotas disponiveis'

    if origem:
        voos_origem = voos.filter(_aeroporto_text_query('origem', origem))
        if destino and _rota_consultada_existe(cleaned_data):
            voos = voos_origem.filter(_aeroporto_text_query('destino', destino))
            titulo = f'Rotas disponiveis: proximas datas para {origem.codigo_iata} - {destino.codigo_iata}'
        else:
            voos = voos_origem
            titulo = f'Rotas disponiveis a partir de {origem.codigo_iata}'
    elif destino:
        voos = voos.filter(_aeroporto_text_query('destino', destino))
        titulo = f'Rotas disponiveis para {destino.codigo_iata}'

    rotas = []
    vistos = set()
    for voo in voos.order_by('partida')[:80]:
        chave = (voo.origem, voo.destino, voo.partida.date())
        if chave in vistos:
            continue

        vistos.add(chave)
        rotas.append({
            'numero_voo': voo.numero_voo,
            'origem': voo.origem,
            'destino': voo.destino,
            'partida': voo.partida,
        })

        if len(rotas) >= limit:
            break

    if not rotas and cleaned_data.get('data_ida'):
        fallback = cleaned_data.copy()
        fallback['data_ida'] = None
        return _rotas_disponiveis(fallback, limit)

    return {
        'titulo': titulo,
        'items': rotas,
    }


def _route_map():
    rotas = {}
    voos = Voo.objects.filter(
        status='programado',
        partida__date__gte=timezone.localdate(),
    ).values_list('origem', 'destino').distinct()

    for origem, destino in voos:
        origem_codigo = _codigo_rota(origem)
        destino_codigo = _codigo_rota(destino)
        if origem_codigo and destino_codigo and origem_codigo != destino_codigo:
            rotas.setdefault(origem_codigo, set()).add(destino_codigo)

    return {origem: sorted(destinos) for origem, destinos in sorted(rotas.items())}


def _rota_consultada_existe(cleaned_data):
    origem = cleaned_data.get('origem')
    destino = cleaned_data.get('destino')

    if not (origem and destino):
        return True

    return Voo.objects.filter(
        status='programado',
        partida__date__gte=timezone.localdate(),
    ).filter(
        _aeroporto_text_query('origem', origem),
        _aeroporto_text_query('destino', destino),
    ).exists()


def _voos_proximos(cleaned_data, janela=7):
    origem = cleaned_data.get('origem')
    destino = cleaned_data.get('destino')
    data_ida = cleaned_data.get('data_ida')

    if not (origem and destino and data_ida):
        return []

    filtros = cleaned_data.copy()
    filtros['data_ida'] = None
    inicio = data_ida - timedelta(days=janela)
    fim = data_ida + timedelta(days=janela)

    voos = (
        _filtrar_voos(filtros)
        .filter(partida__date__range=(inicio, fim))
        .exclude(partida__date=data_ida)
        .order_by('partida')[:8]
    )

    return _preparar_voos_para_resultado(voos, cleaned_data.get('classe'))


DIAS_SEMANA_ABREV = ['seg.', 'ter.', 'qua.', 'qui.', 'sex.', 'sab.', 'dom.']


def _deve_escolher_data(cleaned_data, query_params):
    return bool(
        query_params
        and cleaned_data.get('origem')
        and cleaned_data.get('destino')
        and not cleaned_data.get('data_ida')
    )


def _data_inicio_faixa(cleaned_data, query_params, janela=3):
    data_ida = cleaned_data.get('data_ida')
    if data_ida:
        return data_ida - timedelta(days=janela)

    data_inicio = parse_date(query_params.get('inicio', ''))
    if data_inicio:
        return data_inicio

    filtros = cleaned_data.copy()
    filtros['data_ida'] = None
    primeiro_voo = (
        _filtrar_voos(filtros)
        .filter(partida__date__gte=timezone.localdate())
        .order_by('partida')
        .first()
    )
    if primeiro_voo:
        return timezone.localtime(primeiro_voo.partida).date()

    return timezone.localdate()


def _date_nav_context(cleaned_data, query_params):
    if not (cleaned_data.get('origem') and cleaned_data.get('destino')):
        return {}

    inicio = _data_inicio_faixa(cleaned_data, query_params)
    return {
        'previous_url': _date_nav_url(query_params, inicio - timedelta(days=7), 'buscar_voos'),
        'next_url': _date_nav_url(query_params, inicio + timedelta(days=7), 'buscar_voos'),
        'previous_api_url': _date_nav_url(query_params, inicio - timedelta(days=7), 'buscar_voos_datas'),
        'next_api_url': _date_nav_url(query_params, inicio + timedelta(days=7), 'buscar_voos_datas'),
        'window_url': _date_nav_url(query_params, inicio, 'buscar_voos'),
    }


def _date_nav_url(query_params, inicio, route_name):
    parametros = query_params.copy()
    if 'data_ida' in parametros:
        del parametros['data_ida']
    parametros['inicio'] = inicio.isoformat()
    return f'{reverse(route_name)}?{parametros.urlencode()}'


def _date_chip_payload(dia):
    return {
        'date': dia['data'].isoformat(),
        'label': dia['label'],
        'url': dia['url'],
        'price': dia['preco'],
        'hasFlight': dia['tem_voo'],
        'selected': dia['selecionada'],
        'ariaLabel': f"Buscar voos em {dia['data']:%d/%m/%Y}",
    }


def _datas_flexiveis(cleaned_data, query_params, janela=3):
    origem = cleaned_data.get('origem')
    destino = cleaned_data.get('destino')
    data_ida = cleaned_data.get('data_ida')

    if not (origem and destino):
        return []

    inicio = _data_inicio_faixa(cleaned_data, query_params, janela=janela)
    datas = []
    for deslocamento in range(0, 7):
        data_consulta = inicio + timedelta(days=deslocamento)
        filtros = cleaned_data.copy()
        filtros['data_ida'] = data_consulta
        voos_dia = _preparar_voos_para_resultado(
            _filtrar_voos(filtros),
            cleaned_data.get('classe'),
        )
        precos = [voo.preco_valor for voo in voos_dia if voo.preco_valor is not None]
        menor_preco = min(precos, default=None)
        parametros = query_params.copy()
        if 'inicio' in parametros:
            del parametros['inicio']
        parametros['data_ida'] = data_consulta.isoformat()

        datas.append({
            'data': data_consulta,
            'label': f'{DIAS_SEMANA_ABREV[data_consulta.weekday()]} {data_consulta:%d/%m}',
            'url': f'{reverse("buscar_voos")}?{parametros.urlencode()}',
            'preco': _formatar_moeda(menor_preco) if menor_preco else None,
            'tem_voo': bool(voos_dia),
            'selecionada': data_consulta == data_ida,
        })

    return datas


def _filtros_resumo(cleaned_data):
    resumo = []

    origem = cleaned_data.get('origem')
    destino = cleaned_data.get('destino')
    data_ida = cleaned_data.get('data_ida')
    data_volta = cleaned_data.get('data_volta')
    classe = cleaned_data.get('classe')

    if origem:
        resumo.append(('Origem', BuscaVooForm._label_aeroporto(origem)))
    if destino:
        resumo.append(('Destino', BuscaVooForm._label_aeroporto(destino)))
    if data_ida:
        resumo.append(('Ida', data_ida.strftime('%d/%m/%Y')))
    if data_volta:
        resumo.append(('Volta', data_volta.strftime('%d/%m/%Y')))
    if classe:
        resumo.append(('Cabine', dict(Tarifa.CLASSES).get(classe, classe)))

    return resumo


def _aeroporto_text_query(field_name, aeroporto):
    query = Q()
    terms = {
        aeroporto.codigo_iata,
        aeroporto.nome,
        aeroporto.cidade,
        f'{aeroporto.codigo_iata} - {aeroporto.cidade}',
        f'{aeroporto.codigo_iata} - {aeroporto.nome}',
    }

    for term in terms:
        if term:
            query |= Q(**{f'{field_name}__icontains': term})

    return query


def _preparar_voos_para_resultado(voos, classe=None):
    tarifas = Tarifa.objects.filter(ativa=True)
    if classe:
        tarifas = tarifas.filter(classe=classe)

    voos = voos.prefetch_related(
        Prefetch('tarifas', queryset=tarifas, to_attr='tarifas_ativas_resultado'),
    )
    resultados = list(voos)

    for voo in resultados:
        tarifas_ativas = getattr(voo, 'tarifas_ativas_resultado', [])
        menor_tarifa = min(tarifas_ativas, key=lambda tarifa: tarifa.preco_base + tarifa.taxas, default=None)
        voo.preco_valor = menor_tarifa.preco_base + menor_tarifa.taxas if menor_tarifa else None
        voo.preco_a_partir_de = _formatar_moeda(voo.preco_valor) if menor_tarifa else None
        voo.classe_preco = menor_tarifa.get_classe_display() if menor_tarifa else None
        voo.origem_codigo = _codigo_rota(voo.origem)
        voo.destino_codigo = _codigo_rota(voo.destino)
        voo.duracao_label = _formatar_duracao(voo.chegada - voo.partida)

    return resultados


def _preparar_voo_para_detalhe(voo, classe=None, passageiros=1):
    tarifa = _tarifa_preferida(voo, classe)
    voo.preco_valor = tarifa.preco_base + tarifa.taxas if tarifa else None
    voo.preco_a_partir_de = _formatar_moeda(voo.preco_valor) if tarifa else None
    voo.classe_preco = tarifa.get_classe_display() if tarifa else None
    voo.valor_total_estimado = _formatar_moeda(voo.preco_valor * passageiros) if tarifa else None
    voo.origem_codigo = _codigo_rota(voo.origem)
    voo.destino_codigo = _codigo_rota(voo.destino)
    voo.duracao_label = _formatar_duracao(voo.chegada - voo.partida)
    return voo


def _tarifa_preferida(voo, classe=None):
    tarifas = list(voo.tarifas.filter(ativa=True))

    if classe:
        tarifas_classe = [tarifa for tarifa in tarifas if tarifa.classe == classe]
        if tarifas_classe:
            tarifas = tarifas_classe

    return min(tarifas, key=lambda tarifa: tarifa.preco_base + tarifa.taxas, default=None)


def _detalhe_voo_url(voo_id, classe='', passageiros=1):
    parametros = []
    if classe:
        parametros.append(f'classe={classe}')
    if passageiros:
        parametros.append(f'passageiros={passageiros}')

    url = reverse('detalhe_voo', args=[voo_id])
    if parametros:
        url = f'{url}?{"&".join(parametros)}'

    return url


def _gerar_assento_simples(voo):
    letras = 'ABCDEF'
    capacidade = max(voo.aeronave.capacidade or 180, 1)
    total_fileiras = max(1, (capacidade + len(letras) - 1) // len(letras))
    assentos_ocupados = set(Reserva.objects.filter(voo=voo).values_list('assento', flat=True))

    for fileira in range(1, total_fileiras + 1):
        for letra in letras:
            assento = f'{fileira}{letra}'
            if assento not in assentos_ocupados:
                return assento

    return f'{total_fileiras + 1}A'


def _codigo_rota(valor):
    if not valor:
        return ''
    return valor.split('-', 1)[0].strip().upper()


def _formatar_duracao(duracao):
    minutos = max(0, int(duracao.total_seconds() // 60))
    horas, minutos = divmod(minutos, 60)
    if horas and minutos:
        return f'{horas}h {minutos}min'
    if horas:
        return f'{horas}h'
    return f'{minutos}min'


def _formatar_moeda(valor):
    numero = f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {numero}'


def _dashboard_route_for_user(user):
    if user.tipo == 'funcionario':
        return 'dashboard_funcionario'
    if user.tipo == 'administrador' or user.is_staff:
        return 'dashboard_administrador'
    return 'dashboard_passageiro'


def _account_label_for_user(user):
    first_name = (user.first_name or '').strip().split(' ')[0]
    if first_name:
        return f'Olá, {first_name}'
    return 'Minha conta'


def _account_initials_for_user(user):
    names = [name for name in [user.first_name, user.last_name] if name]
    if not names:
        names = [user.username]
    return ''.join(name[0] for name in names[:2]).upper()


def _post_login_route_for_user(user):
    if user.tipo == 'passageiro':
        return 'home'
    return _dashboard_route_for_user(user)


def _can_access_dashboard(user, tipo):
    if tipo == 'administrador':
        return user.tipo == 'administrador' or user.is_staff
    return user.tipo == tipo


def _redirect_to_user_dashboard(user):
    return redirect(_dashboard_route_for_user(user))


def _voos_do_dia_operacional():
    return Voo.objects.select_related('aeronave', 'portao').filter(
        partida__date=timezone.localdate(),
    ).order_by('partida')


def _notificacao_tipo_operacional(status_alterado, portao_alterado, novo_status):
    if status_alterado and novo_status == 'cancelado':
        return 'cancelamento'
    if status_alterado and novo_status == 'atrasado':
        return 'atraso'
    if portao_alterado:
        return 'mudanca_portao'
    return 'geral'


def _mensagem_operacional_voo(voo, status_alterado, portao_alterado):
    partes = [f'Atualizacao do voo {voo.numero_voo}.']
    if status_alterado:
        partes.append(f'Status: {voo.get_status_display()}.')
    if portao_alterado:
        numero_portao = voo.portao.numero_portao if voo.portao else 'A definir'
        partes.append(f'Portao: {numero_portao}.')
    return ' '.join(partes)


def _notificar_passageiros_operacionais(voo, mensagem, tipo):
    reservas = Reserva.objects.select_related('passageiro').filter(voo=voo).exclude(status='cancelada')
    passageiros = {}
    for reserva in reservas:
        passageiros[reserva.passageiro_id] = reserva.passageiro

    for passageiro in passageiros.values():
        Notificacao.objects.create(
            passageiro=passageiro,
            mensagem=mensagem,
            tipo=tipo,
        )

    return len(passageiros)


def _safe_next_url(request):
    next_url = request.POST.get('next') or request.GET.get('next') or ''
    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return ''


def _login_url_with_next(next_url):
    if next_url:
        return f'{reverse("login")}?{urlencode({"next": next_url})}'
    return reverse('login')


@login_required
def dashboard_router(request):
    return _redirect_to_user_dashboard(request.user)


@login_required
def dashboard_passageiro(request):
    if not _can_access_dashboard(request.user, 'passageiro'):
        return _redirect_to_user_dashboard(request.user)

    passageiro = getattr(request.user, 'passageiro', None)
    reservas = []
    notificacoes = []

    if passageiro:
        reservas = _preparar_reservas_jornada(
            passageiro.reserva_set.select_related('voo', 'pagamento', 'bilhete').all().order_by('-id')[:5]
        )
        notificacoes = passageiro.notificacao_set.all()[:5]

    return render(request, 'painel_passageiro.html', {
        'passageiro': passageiro,
        'reservas': reservas,
        'notificacoes': notificacoes,
    })


@login_required
@require_POST
def atualizar_voo_operacional(request, voo_id):
    if not _can_access_dashboard(request.user, 'funcionario'):
        return _redirect_to_user_dashboard(request.user)

    voo = get_object_or_404(Voo.objects.select_related('portao'), pk=voo_id)
    status_anterior = voo.status
    portao_anterior = voo.portao
    form = AtualizarVooOperacionalForm(request.POST, instance=voo)

    if not form.is_valid():
        messages.error(request, 'Nao foi possivel atualizar o voo. Verifique os dados informados.')
        return redirect('dashboard_funcionario')

    with transaction.atomic():
        voo = form.save()
        status_alterado = status_anterior != voo.status
        portao_alterado = (portao_anterior.id if portao_anterior else None) != voo.portao_id

        if portao_alterado:
            if portao_anterior:
                portao_anterior.status = 'livre'
                portao_anterior.save(update_fields=['status'])
            if voo.portao:
                voo.portao.status = 'ocupado'
                voo.portao.save(update_fields=['status'])

        if status_alterado or portao_alterado:
            tipo = _notificacao_tipo_operacional(status_alterado, portao_alterado, voo.status)
            mensagem = _mensagem_operacional_voo(voo, status_alterado, portao_alterado)
            total_notificados = _notificar_passageiros_operacionais(voo, mensagem, tipo)
            messages.success(
                request,
                f'Voo {voo.numero_voo} atualizado. {total_notificados} passageiro(s) notificado(s).',
            )
        else:
            messages.info(request, f'Nenhuma alteracao aplicada ao voo {voo.numero_voo}.')

    return redirect('dashboard_funcionario')


@login_required
def dashboard_funcionario(request):
    if not _can_access_dashboard(request.user, 'funcionario'):
        return _redirect_to_user_dashboard(request.user)

    funcionario = getattr(request.user, 'funcionario', None)
    voos = _voos_do_dia_operacional()
    bagagens = Bagagem.objects.select_related('reserva__passageiro', 'reserva__voo').all().order_by('-id')[:8]
    portoes = PortaoEmbarque.objects.all().order_by('numero_portao')

    return render(request, 'painel_funcionario.html', {
        'funcionario': funcionario,
        'voos': voos,
        'bagagens': bagagens,
        'portoes': portoes,
        'status_choices': Voo.STATUS,
    })


@login_required
def dashboard_administrador(request):
    if not _can_access_dashboard(request.user, 'administrador'):
        return _redirect_to_user_dashboard(request.user)

    receita_aprovada = Pagamento.objects.filter(status='aprovado').aggregate(
        total=Sum('valor_total'),
    )['total'] or Decimal('0.00')
    ultimas_reservas = list(
        Reserva.objects.select_related('passageiro', 'voo', 'pagamento')
        .order_by('-id')[:5]
    )

    for reserva in ultimas_reservas:
        pagamento = getattr(reserva, 'pagamento', None)
        reserva.pagamento_status_painel = pagamento.get_status_display() if pagamento else 'Sem pagamento'
        reserva.pagamento_valor_painel = _formatar_moeda(pagamento.valor_total) if pagamento else '-'

    stats = {
        'total_passageiros': Passageiro.objects.count(),
        'total_funcionarios': Funcionario.objects.count(),
        'total_voos': Voo.objects.count(),
        'total_reservas': Reserva.objects.count(),
        'total_pagamentos': Pagamento.objects.count(),
        'pagamentos_aprovados': Pagamento.objects.filter(status='aprovado').count(),
        'receita_aprovada': receita_aprovada,
        'receita_aprovada_formatada': _formatar_moeda(receita_aprovada),
    }

    admin_links = [
        {'label': 'Django Admin', 'url': '/admin/', 'icon': 'fa-screwdriver-wrench', 'primary': True},
        {'label': 'Usuarios', 'url': '/admin/skybridgeapp/usuariocustomizado/', 'icon': 'fa-user-shield'},
        {'label': 'Passageiros', 'url': '/admin/skybridgeapp/passageiro/', 'icon': 'fa-users'},
        {'label': 'Funcionarios', 'url': '/admin/skybridgeapp/funcionario/', 'icon': 'fa-id-card'},
        {'label': 'Voos', 'url': '/admin/skybridgeapp/voo/', 'icon': 'fa-plane-up'},
        {'label': 'Reservas', 'url': '/admin/skybridgeapp/reserva/', 'icon': 'fa-ticket'},
        {'label': 'Pagamentos', 'url': '/admin/skybridgeapp/pagamento/', 'icon': 'fa-file-invoice-dollar'},
        {'label': 'Aeroportos', 'url': '/admin/skybridgeapp/aeroporto/', 'icon': 'fa-location-dot'},
        {'label': 'Aeronaves', 'url': '/admin/skybridgeapp/aeronave/', 'icon': 'fa-plane'},
        {'label': 'Promocoes', 'url': '/admin/skybridgeapp/promocao/', 'icon': 'fa-tags'},
    ]

    return render(request, 'painel_admin.html', {
        'stats': stats,
        'ultimas_reservas': ultimas_reservas,
        'admin_links': admin_links,
    })


class SkyBridgeLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, 'Login realizado com sucesso.')
        return super().form_valid(form)

    def get_default_redirect_url(self):
        return reverse(_post_login_route_for_user(self.request.user))


class SkyBridgeLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, 'Logout realizado com sucesso.')
        return response


class SkyBridgePasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


class SkyBridgePasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class SkyBridgePasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class SkyBridgePasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


class SkyBridgePasswordChangeView(PasswordChangeView):
    template_name = 'password_change_form.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        messages.success(self.request, 'Senha alterada com sucesso.')
        return super().form_valid(form)


class SkyBridgePasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'password_change_done.html'
