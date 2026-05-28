from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Funcionario, Passageiro, UsuarioCustomizado


class CadastroUsuarioForm(UserCreationForm):
    tipo = forms.ChoiceField(
        label='Tipo de usuario',
        choices=UsuarioCustomizado.TIPOS,
        initial='passageiro',
        widget=forms.RadioSelect,
    )
    nome = forms.CharField(
        label='Nome completo',
        max_length=100,
        widget=forms.TextInput(attrs={
            'autocomplete': 'name',
            'placeholder': 'Joao da Silva',
        }),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'placeholder': 'seu@email.com',
        }),
    )
    cpf_passaporte = forms.CharField(
        label='CPF / Passaporte',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
    )
    data_nascimento = forms.DateField(
        label='Data de nascimento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    contato = forms.CharField(
        label='Telefone / Contato',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'tel',
            'placeholder': '(11) 99999-9999',
        }),
    )
    nacionalidade = forms.CharField(
        label='Nacionalidade',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Brasileira'}),
    )
    cargo = forms.ChoiceField(
        label='Cargo',
        choices=[('', 'Selecione um cargo')] + Funcionario.CARGOS,
        required=False,
    )
    matricula = forms.CharField(
        label='Matricula',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'MAT123'}),
    )

    class Meta(UserCreationForm.Meta):
        model = UsuarioCustomizado
        fields = (
            'tipo',
            'username',
            'nome',
            'email',
            'cpf_passaporte',
            'data_nascimento',
            'contato',
            'nacionalidade',
            'cargo',
            'matricula',
            'password1',
            'password2',
        )

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')

        if tipo == 'passageiro':
            self._exigir_campos(cleaned_data, [
                'contato',
                'cpf_passaporte',
                'data_nascimento',
                'nacionalidade',
            ])
            cpf_passaporte = cleaned_data.get('cpf_passaporte')
            if cpf_passaporte and Passageiro.objects.filter(cpf_passaporte=cpf_passaporte).exists():
                self.add_error('cpf_passaporte', 'Ja existe um passageiro com este CPF/passaporte.')

        if tipo == 'funcionario':
            self._exigir_campos(cleaned_data, ['contato', 'cargo', 'matricula'])
            matricula = cleaned_data.get('matricula')
            if matricula and Funcionario.objects.filter(matricula=matricula).exists():
                self.add_error('matricula', 'Ja existe um funcionario com esta matricula.')

        return cleaned_data

    def _exigir_campos(self, cleaned_data, field_names):
        for field_name in field_names:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, 'Este campo e obrigatorio para o tipo selecionado.')

    def save(self, commit=True):
        user = super().save(commit=False)
        tipo = self.cleaned_data['tipo']
        user.tipo = tipo
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nome']
        user.is_staff = tipo == 'administrador'
        user.is_superuser = False

        if commit:
            with transaction.atomic():
                user.save()
                if tipo == 'passageiro':
                    Passageiro.objects.create(
                        usuario=user,
                        nome=self.cleaned_data['nome'],
                        cpf_passaporte=self.cleaned_data['cpf_passaporte'],
                        data_nascimento=self.cleaned_data['data_nascimento'],
                        contato=self.cleaned_data['contato'],
                        nacionalidade=self.cleaned_data['nacionalidade'],
                    )
                elif tipo == 'funcionario':
                    Funcionario.objects.create(
                        usuario=user,
                        nome=self.cleaned_data['nome'],
                        cargo=self.cleaned_data['cargo'],
                        matricula=self.cleaned_data['matricula'],
                        contato=self.cleaned_data['contato'],
                    )

        return user
