from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import CadastroAdministradorForm, CadastroFuncionarioForm, CadastroPassageiroForm
from .models import Passageiro


LANDING_CONTEXT = {
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
        {'label': 'Origem', 'value': 'São Paulo', 'aria_label': 'Selecionar origem'},
        {'label': 'Destino', 'value': 'Para onde?', 'aria_label': 'Selecionar destino'},
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
    'offer_filters': [
        {'label': 'Todos os destinos', 'active': True},
        {'label': 'Nacionais'},
        {'label': 'Internacionais'},
        {'label': 'Menor preço'},
        {'label': 'Voos diretos'},
        {'label': 'Voos com conexão'},
    ],
    'offers': [
        {
            'image_class': 'offer-rio',
            'route': 'São Paulo → Rio de Janeiro',
            'title': 'Escapada urbana à beira-mar',
            'description': 'Voos selecionados com taxas incluídas.',
            'price': 'R$ 189',
        },
        {
            'image_class': 'offer-recife',
            'route': 'São Paulo → Recife',
            'title': 'Praias e cultura no Nordeste',
            'description': 'Condições especiais em datas selecionadas.',
            'price': 'R$ 329',
        },
        {
            'image_class': 'offer-salvador',
            'route': 'São Paulo → Salvador',
            'title': 'Sol, música e centro histórico',
            'description': 'Tarifas promocionais para ida e volta.',
            'price': 'R$ 299',
        },
        {
            'image_class': 'offer-buenos-aires',
            'route': 'São Paulo → Buenos Aires',
            'title': 'Fim de semana internacional',
            'description': 'Opções com conexão curta ou voo direto.',
            'price': 'R$ 689',
        },
        {
            'image_class': 'offer-santiago',
            'route': 'São Paulo → Santiago',
            'title': 'Montanhas e gastronomia',
            'description': 'Preços finais com taxas já consideradas.',
            'price': 'R$ 759',
        },
        {
            'image_class': 'offer-lisboa',
            'route': 'São Paulo → Lisboa',
            'title': 'Europa com planejamento flexível',
            'description': 'Ofertas sujeitas à disponibilidade.',
            'price': 'R$ 2.499',
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
    return render(request, 'home.html', LANDING_CONTEXT)


def auth_home(request):
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


@login_required
def dashboard(request):
    passageiro = Passageiro.objects.filter(usuario=request.user).first()
    return render(request, 'dashboard.html', {'passageiro': passageiro})


class SkyBridgeLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True


class SkyBridgeLogoutView(LogoutView):
    next_page = reverse_lazy('home')
