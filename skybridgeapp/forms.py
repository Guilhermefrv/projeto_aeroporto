from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Funcionario, Passageiro, UsuarioCustomizado


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
