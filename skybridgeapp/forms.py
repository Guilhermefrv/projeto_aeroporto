from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Passageiro, UsuarioCustomizado


class CadastroPassageiroForm(UserCreationForm):
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
        widget=forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
    )
    data_nascimento = forms.DateField(
        label='Data de nascimento',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    contato = forms.CharField(
        label='Telefone / Contato',
        max_length=100,
        widget=forms.TextInput(attrs={
            'autocomplete': 'tel',
            'placeholder': '(11) 99999-9999',
        }),
    )
    nacionalidade = forms.CharField(
        label='Nacionalidade',
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Brasileira'}),
    )

    class Meta(UserCreationForm.Meta):
        model = UsuarioCustomizado
        fields = (
            'username',
            'nome',
            'email',
            'cpf_passaporte',
            'data_nascimento',
            'contato',
            'nacionalidade',
            'password1',
            'password2',
        )

    def clean_cpf_passaporte(self):
        cpf_passaporte = self.cleaned_data['cpf_passaporte']
        if Passageiro.objects.filter(cpf_passaporte=cpf_passaporte).exists():
            raise forms.ValidationError('Ja existe um passageiro com este CPF/passaporte.')
        return cpf_passaporte

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'passageiro'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nome']

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
