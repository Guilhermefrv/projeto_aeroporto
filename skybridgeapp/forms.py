from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Aeroporto, Funcionario, Passageiro, Tarifa, UsuarioCustomizado, Voo


NACIONALIDADES_CHOICES = [
    ('', 'Selecione sua nacionalidade'),
    ('Brasileira', 'Brasileira'),
    ('Argentina', 'Argentina'),
    ('Chilena', 'Chilena'),
    ('Uruguaia', 'Uruguaia'),
    ('Paraguaia', 'Paraguaia'),
    ('Boliviana', 'Boliviana'),
    ('Peruana', 'Peruana'),
    ('Colombiana', 'Colombiana'),
    ('Venezuelana', 'Venezuelana'),
    ('Portuguesa', 'Portuguesa'),
    ('Espanhola', 'Espanhola'),
    ('Italiana', 'Italiana'),
    ('Francesa', 'Francesa'),
    ('Alemã', 'Alemã'),
    ('Estadunidense', 'Estadunidense'),
    ('Canadense', 'Canadense'),
    ('Mexicana', 'Mexicana'),
    ('Japonesa', 'Japonesa'),
    ('Chinesa', 'Chinesa'),
    ('Outra', 'Outra'),
]


class BuscaVooForm(forms.Form):
    origem = forms.ModelChoiceField(
        label='Origem',
        queryset=Aeroporto.objects.none(),
        required=False,
        empty_label='Selecionar origem',
        widget=forms.Select(attrs={'class': 'flight-search-input'}),
    )
    destino = forms.ModelChoiceField(
        label='Destino',
        queryset=Aeroporto.objects.none(),
        required=False,
        empty_label='Selecionar destino',
        widget=forms.Select(attrs={'class': 'flight-search-input'}),
    )
    data_ida = forms.DateField(
        label='Ida',
        required=False,
        widget=forms.DateInput(attrs={'class': 'flight-search-input', 'type': 'date'}),
    )
    data_volta = forms.DateField(
        label='Volta',
        required=False,
        widget=forms.DateInput(attrs={'class': 'flight-search-input', 'type': 'date'}),
    )
    passageiros = forms.IntegerField(
        label='Passageiros',
        min_value=1,
        max_value=9,
        initial=1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'flight-search-input', 'min': '1', 'max': '9'}),
    )
    classe = forms.ChoiceField(
        label='Cabine',
        required=False,
        choices=[('', 'Todas as classes')] + Tarifa.CLASSES,
        widget=forms.Select(attrs={'class': 'flight-search-input'}),
    )
    codigo_promocional = forms.CharField(
        label='Codigo promocional',
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'flight-search-input', 'placeholder': 'Adicionar'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aeroportos = Aeroporto.objects.filter(pais__iexact='Brasil')
        origens = self._aeroportos_com_voos(aeroportos, 'origem', self.data.get('origem') if self.is_bound else None)
        destinos = self._aeroportos_com_voos(aeroportos, 'destino', self.data.get('destino') if self.is_bound else None)
        self.fields['origem'].queryset = origens.order_by('codigo_iata')
        self.fields['destino'].queryset = destinos.order_by('codigo_iata')
        self.fields['origem'].label_from_instance = self._label_aeroporto
        self.fields['destino'].label_from_instance = self._label_aeroporto

    @staticmethod
    def _label_aeroporto(aeroporto):
        return f'{aeroporto.codigo_iata} - {aeroporto.cidade}'

    @staticmethod
    def _aeroportos_com_voos(aeroportos, campo_voo, selecionado=None):
        codigos = set()
        for valor in Voo.objects.filter(status='programado').values_list(campo_voo, flat=True).distinct():
            codigo = (valor or '').split('-', 1)[0].strip().upper()
            if codigo:
                codigos.add(codigo)

        queryset = aeroportos.filter(codigo_iata__in=codigos) if codigos else aeroportos
        if selecionado:
            queryset = queryset | aeroportos.filter(pk=selecionado)

        return queryset.distinct()


class SelecionarVooForm(forms.Form):
    passageiros = forms.IntegerField(
        label='Passageiros',
        min_value=1,
        max_value=9,
        initial=1,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'detail-input',
            'min': '1',
            'max': '9',
        }),
    )
    classe = forms.ChoiceField(
        label='Cabine',
        required=False,
        choices=[('', 'Menor tarifa disponivel')] + Tarifa.CLASSES,
        widget=forms.Select(attrs={'class': 'detail-input'}),
    )


class CadastroBaseForm(UserCreationForm):
    nome = forms.CharField(label='Nome completo', max_length=100)
    email = forms.EmailField(label='Email')

    class Meta(UserCreationForm.Meta):
        model = UsuarioCustomizado
        fields = ('username', 'nome', 'email', 'password1', 'password2')

    def preparar_usuario(self, tipo, is_staff=False):
        user = super().save(commit=False)
        user.tipo = tipo
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nome']
        user.is_staff = is_staff
        user.is_superuser = False
        return user


class CadastroPassageiroForm(CadastroBaseForm):
    contato = forms.CharField(label='Telefone / Contato', max_length=100)
    cpf_passaporte = forms.CharField(label='CPF / Passaporte', max_length=20)
    data_nascimento = forms.DateField(
        label='Data de nascimento',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    nacionalidade = forms.ChoiceField(
        label='Nacionalidade',
        choices=NACIONALIDADES_CHOICES,
    )

    class Meta(CadastroBaseForm.Meta):
        fields = CadastroBaseForm.Meta.fields + (
            'contato',
            'cpf_passaporte',
            'data_nascimento',
            'nacionalidade',
        )

    def clean_cpf_passaporte(self):
        cpf_passaporte = self.cleaned_data['cpf_passaporte']
        if Passageiro.objects.filter(cpf_passaporte=cpf_passaporte).exists():
            raise forms.ValidationError('Ja existe um passageiro com este CPF/passaporte.')
        return cpf_passaporte

    def save(self, commit=True):
        user = self.preparar_usuario('passageiro')

        if commit:
            with transaction.atomic():
                user.save()
                Passageiro.objects.create(
                    usuario=user,
                    nome=self.cleaned_data['nome'],
                    cpf_passaporte=self.cleaned_data['cpf_passaporte'],
                    data_nascimento=self.cleaned_data['data_nascimento'],
                    contato=self.cleaned_data['contato'],
                    nacionalidade=self.cleaned_data['nacionalidade'],
                )

        return user


class CadastroFuncionarioForm(CadastroBaseForm):
    contato = forms.CharField(label='Telefone / Contato', max_length=100)
    cargo = forms.ChoiceField(label='Cargo', choices=Funcionario.CARGOS)
    matricula = forms.CharField(label='Matricula', max_length=20)

    class Meta(CadastroBaseForm.Meta):
        fields = CadastroBaseForm.Meta.fields + ('contato', 'cargo', 'matricula')

    def clean_matricula(self):
        matricula = self.cleaned_data['matricula']
        if Funcionario.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError('Ja existe um funcionario com esta matricula.')
        return matricula

    def save(self, commit=True):
        user = self.preparar_usuario('funcionario')

        if commit:
            with transaction.atomic():
                user.save()
                Funcionario.objects.create(
                    usuario=user,
                    nome=self.cleaned_data['nome'],
                    cargo=self.cleaned_data['cargo'],
                    matricula=self.cleaned_data['matricula'],
                    contato=self.cleaned_data['contato'],
                )

        return user


class CadastroAdministradorForm(CadastroBaseForm):
    def save(self, commit=True):
        user = self.preparar_usuario('administrador', is_staff=True)

        if commit:
            user.save()

        return user
