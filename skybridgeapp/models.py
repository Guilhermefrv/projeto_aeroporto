from django.db import models
from django.contrib.auth.models import AbstractUser


class UsuarioCustomizado(AbstractUser):
    """
    Model de usuário customizado que substitui o User padrão do Django.
    Utiliza AbstractUser para herdar autenticação segura (hash de senha, sessões, permissões).
    O campo 'tipo' determina qual painel o usuário acessa após o login.
    """
    TIPOS = [
        ('passageiro', 'Passageiro'),
        ('funcionario', 'Funcionário'),
        ('administrador', 'Administrador'),
    ]
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default='passageiro',
        verbose_name='Tipo de usuário',
    )

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class Passageiro(models.Model):
    """
    Perfil complementar do usuário com tipo='passageiro'.
    Vinculado via OneToOneField ao UsuarioCustomizado.
    """
    usuario = models.OneToOneField(
        UsuarioCustomizado,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='passageiro',
        verbose_name='Usuário',
    )
    nome = models.CharField(max_length=100, verbose_name='Nome completo')
    cpf_passaporte = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='CPF / Passaporte',
    )
    data_nascimento = models.DateField(verbose_name='Data de nascimento')
    contato = models.CharField(max_length=100, verbose_name='Telefone / Contato')
    nacionalidade = models.CharField(max_length=50, verbose_name='Nacionalidade')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Passageiro'
        verbose_name_plural = 'Passageiros'


class Funcionario(models.Model):
    """
    Perfil complementar do usuário com tipo='funcionario'.
    Vinculado via OneToOneField ao UsuarioCustomizado.
    """
    CARGOS = [
        ('piloto', 'Piloto'),
        ('atendente', 'Atendente'),
        ('seguranca', 'Segurança'),
    ]
    usuario = models.OneToOneField(
        UsuarioCustomizado,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='funcionario',
        verbose_name='Usuário',
    )
    nome = models.CharField(max_length=100, verbose_name='Nome completo')
    cargo = models.CharField(max_length=20, choices=CARGOS, verbose_name='Cargo')
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula')
    contato = models.CharField(max_length=100, verbose_name='Telefone / Contato')

    def __str__(self):
        return f"{self.nome} — {self.get_cargo_display()}"

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'


class Administrador(models.Model):
    """
    Model legado mantido durante o desenvolvimento inicial.
    Será integrado ao UsuarioCustomizado em fase futura.
    ATENÇÃO: senha armazenada em texto puro — não usar em produção.
    """
    nome = models.CharField(max_length=100)
    login = models.CharField(max_length=50, unique=True)
    senha = models.CharField(max_length=128)
    nivel_acesso = models.IntegerField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Administrador (legado)'
        verbose_name_plural = 'Administradores (legado)'


class Aeronave(models.Model):
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    capacidade = models.IntegerField(verbose_name='Capacidade (passageiros)')
    companhia_aerea = models.CharField(max_length=100, verbose_name='Companhia aérea')

    def __str__(self):
        return f"{self.modelo} — {self.companhia_aerea}"

    class Meta:
        verbose_name = 'Aeronave'
        verbose_name_plural = 'Aeronaves'


class PortaoEmbarque(models.Model):
    STATUS = [
        ('livre', 'Livre'),
        ('ocupado', 'Ocupado'),
    ]
    numero_portao = models.CharField(max_length=10, unique=True, verbose_name='Número do portão')
    localizacao = models.CharField(max_length=100, verbose_name='Localização')
    status = models.CharField(max_length=20, choices=STATUS, verbose_name='Status')

    def __str__(self):
        return f"Portão {self.numero_portao} — {self.get_status_display()}"

    class Meta:
        verbose_name = 'Portão de Embarque'
        verbose_name_plural = 'Portões de Embarque'


class Voo(models.Model):
    STATUS = [
        ('programado', 'Programado'),
        ('atrasado', 'Atrasado'),
        ('em_andamento', 'Em andamento'),
        ('cancelado', 'Cancelado'),
    ]
    numero_voo = models.CharField(max_length=20, unique=True, verbose_name='Número do voo')
    origem = models.CharField(max_length=100, verbose_name='Origem')
    destino = models.CharField(max_length=100, verbose_name='Destino')
    partida = models.DateTimeField(verbose_name='Partida')
    chegada = models.DateTimeField(verbose_name='Chegada')
    status = models.CharField(max_length=20, choices=STATUS, verbose_name='Status')
    aeronave = models.ForeignKey(
        Aeronave,
        on_delete=models.CASCADE,
        verbose_name='Aeronave',
    )
    portao = models.ForeignKey(
        PortaoEmbarque,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voos',
        verbose_name='Portão de embarque',
    )

    def __str__(self):
        return f"Voo {self.numero_voo} — {self.origem} → {self.destino}"

    class Meta:
        verbose_name = 'Voo'
        verbose_name_plural = 'Voos'
        ordering = ['partida']


class Reserva(models.Model):
    STATUS = [
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    passageiro = models.ForeignKey(
        Passageiro,
        on_delete=models.CASCADE,
        verbose_name='Passageiro',
    )
    voo = models.ForeignKey(
        Voo,
        on_delete=models.CASCADE,
        verbose_name='Voo',
    )
    assento = models.CharField(max_length=10, verbose_name='Assento')
    status = models.CharField(max_length=20, choices=STATUS, verbose_name='Status')

    def __str__(self):
        return f"Reserva #{self.id} — {self.passageiro.nome} / Voo {self.voo.numero_voo}"

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'


class Bilhete(models.Model):
    reserva = models.OneToOneField(
        Reserva,
        on_delete=models.CASCADE,
        verbose_name='Reserva',
    )
    codigo = models.CharField(max_length=100, unique=True, verbose_name='Código do bilhete')
    data_emissao = models.DateTimeField(auto_now_add=True, verbose_name='Data de emissão')

    def __str__(self):
        return f"Bilhete {self.codigo}"

    class Meta:
        verbose_name = 'Bilhete'
        verbose_name_plural = 'Bilhetes'


class Bagagem(models.Model):
    """
    Bagagem agora vinculada a uma Reserva (e portanto a um Voo específico).
    Possui número de rastreio único gerado automaticamente.
    """
    STATUS = [
        ('despachada', 'Despachada'),
        ('em_transito', 'Em trânsito'),
        ('entregue', 'Entregue'),
    ]
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='bagagens',
        verbose_name='Reserva',
    )
    peso = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Peso (kg)')
    status = models.CharField(max_length=20, choices=STATUS, verbose_name='Status')
    numero_rastreio = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de rastreio',
    )

    def __str__(self):
        return f"Bagagem {self.numero_rastreio} — {self.reserva.passageiro.nome}"

    class Meta:
        verbose_name = 'Bagagem'
        verbose_name_plural = 'Bagagens'


class CheckIn(models.Model):
    STATUS = [
        ('realizado', 'Realizado'),
        ('pendente', 'Pendente'),
    ]
    passageiro = models.ForeignKey(
        Passageiro,
        on_delete=models.CASCADE,
        verbose_name='Passageiro',
    )
    voo = models.ForeignKey(
        Voo,
        on_delete=models.CASCADE,
        verbose_name='Voo',
    )
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data e hora')
    status = models.CharField(max_length=20, choices=STATUS, verbose_name='Status')

    def __str__(self):
        return f"Check-in #{self.id} — {self.passageiro.nome} / Voo {self.voo.numero_voo}"

    class Meta:
        verbose_name = 'Check-in'
        verbose_name_plural = 'Check-ins'


class Notificacao(models.Model):
    """
    Notificações enviadas a passageiros.
    O campo 'lida' permite controlar o badge de não-lidas no menu.
    Criadas automaticamente ao mudar status de voo, ou manualmente pelo funcionário.
    """
    TIPOS = [
        ('atraso', 'Alerta de atraso'),
        ('mudanca_portao', 'Mudança de portão'),
        ('cancelamento', 'Cancelamento de voo'),
        ('geral', 'Informação geral'),
    ]
    passageiro = models.ForeignKey(
        Passageiro,
        on_delete=models.CASCADE,
        verbose_name='Passageiro',
    )
    mensagem = models.TextField(verbose_name='Mensagem')
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data e hora')
    tipo = models.CharField(max_length=20, choices=TIPOS, verbose_name='Tipo')
    lida = models.BooleanField(default=False, verbose_name='Lida')

    def __str__(self):
        return f"Notificação [{self.get_tipo_display()}] — {self.passageiro.nome}"

    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_hora']
