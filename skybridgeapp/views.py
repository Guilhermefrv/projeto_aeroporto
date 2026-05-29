from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy

from .forms import BuscaVooForm, CadastroAdministradorForm, CadastroFuncionarioForm, CadastroPassageiroForm
from .models import Bagagem, Funcionario, Passageiro, PortaoEmbarque, Reserva, Tarifa, Voo


LANDING_CONTEXT = {
    'asset_version': '20260528-national-polish-2',
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
            'image_url': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=900&q=80',
            'route': 'São Paulo → Manaus',
            'title': 'Amazônia e cultura no Norte',
            'description': 'Trechos nacionais com opções em datas selecionadas.',
            'price': 'R$ 549',
        },
        {
            'image_class': 'offer-curitiba',
            'image_url': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80',
            'route': 'São Paulo → Curitiba',
            'title': 'Fim de semana no Sul',
            'description': 'Rotas nacionais para viagens rápidas e flexíveis.',
            'price': 'R$ 219',
        },
        {
            'image_class': 'offer-brasilia',
            'image_url': 'https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=900&q=80',
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
            'image_url': 'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=900&q=80',
            'route': 'São Paulo → Porto Alegre',
            'title': 'Cultura e gastronomia no Sul',
            'description': 'Trechos nacionais com tarifas promocionais.',
            'price': 'R$ 259',
        },
        {
            'image_class': 'offer-cuiaba',
            'image_url': 'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=900&q=80',
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


def home(request):
    context = {
        **LANDING_CONTEXT,
        'search_form': BuscaVooForm(),
    }
    _add_account_context(request, context)

    return render(request, 'home.html', context)


def buscar_voos(request):
    form = BuscaVooForm(request.GET or None)
    voos = []
    filtros_validos = form.is_valid() if form.is_bound else True

    if filtros_validos:
        cleaned_data = form.cleaned_data if form.is_bound else {}
        voos = _preparar_voos_para_resultado(
            _filtrar_voos(cleaned_data),
            cleaned_data.get('classe'),
        )

    context = {
        'asset_version': LANDING_CONTEXT['asset_version'],
        'nav_items': LANDING_CONTEXT['nav_items'],
        'search_form': form,
        'voos': voos,
        'busca_realizada': bool(request.GET),
    }
    _add_account_context(request, context)

    return render(request, 'buscar_voos.html', context)


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
            return redirect('login')

        if form:
            modal_aberto = tipo_enviado
        else:
            messages.error(request, 'Selecione um tipo de usuario valido.')

    return render(request, 'cadastro.html', {
        'passageiro_form': forms['passageiro'],
        'funcionario_form': forms['funcionario'],
        'administrador_form': forms['administrador'],
        'modal_aberto': modal_aberto,
    })


def _add_account_context(request, context):
    if request.user.is_authenticated:
        context['account_dashboard_url'] = reverse(_dashboard_route_for_user(request.user))
        context['account_label'] = _account_label_for_user(request.user)
        context['account_initials'] = _account_initials_for_user(request.user)


def _filtrar_voos(cleaned_data):
    voos = Voo.objects.select_related('aeronave', 'portao').exclude(status='cancelado')

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
        voo.preco_a_partir_de = _formatar_moeda(menor_tarifa.preco_base + menor_tarifa.taxas) if menor_tarifa else None
        voo.classe_preco = menor_tarifa.get_classe_display() if menor_tarifa else None

    return resultados


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
        reservas = passageiro.reserva_set.select_related('voo').all().order_by('-id')[:5]
        notificacoes = passageiro.notificacao_set.all()[:5]

    return render(request, 'painel_passageiro.html', {
        'passageiro': passageiro,
        'reservas': reservas,
        'notificacoes': notificacoes,
    })


@login_required
def dashboard_funcionario(request):
    if not _can_access_dashboard(request.user, 'funcionario'):
        return _redirect_to_user_dashboard(request.user)

    funcionario = getattr(request.user, 'funcionario', None)
    voos = Voo.objects.all().order_by('partida')[:5]
    bagagens = Bagagem.objects.select_related('reserva__passageiro').all().order_by('-id')[:5]
    portoes = PortaoEmbarque.objects.all().order_by('numero_portao')[:6]

    return render(request, 'painel_funcionario.html', {
        'funcionario': funcionario,
        'voos': voos,
        'bagagens': bagagens,
        'portoes': portoes,
    })


@login_required
def dashboard_administrador(request):
    if not _can_access_dashboard(request.user, 'administrador'):
        return _redirect_to_user_dashboard(request.user)

    stats = {
        'total_passageiros': Passageiro.objects.count(),
        'total_funcionarios': Funcionario.objects.count(),
        'total_voos': Voo.objects.count(),
        'total_reservas': Reserva.objects.count(),
    }

    return render(request, 'painel_admin.html', {'stats': stats})


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
