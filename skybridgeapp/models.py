from django.db import models

class Passageiro(models.Model):
    nome = models.CharField(max_length=100)
    cpf_passaporte = models.CharField(max_length=20, unique=True)
    data_nascimento = models.DateField()
    contato = models.CharField(max_length=100)
    nacionalidade = models.CharField(max_length=50)

    def __str__(self):
        return self.nome


class Funcionario(models.Model):
    CARGOS = [
        ('piloto', 'Piloto'),
        ('atendente', 'Atendente'),
        ('seguranca', 'Segurança'),
    ]
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=20, choices=CARGOS)
    matricula = models.CharField(max_length=20, unique=True)
    contato = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} - {self.cargo}"


class Administrador(models.Model):
    nome = models.CharField(max_length=100)
    login = models.CharField(max_length=50, unique=True)
    senha = models.CharField(max_length=128)
    nivel_acesso = models.IntegerField()

    def __str__(self):
        return self.nome


class Aeronave(models.Model):
    modelo = models.CharField(max_length=100)
    capacidade = models.IntegerField()
    companhia_aerea = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.modelo} - {self.companhia_aerea}"


class Voo(models.Model):
    STATUS = [
        ('programado', 'Programado'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]
    numero_voo = models.CharField(max_length=20, unique=True)
    origem = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    partida = models.DateTimeField()
    chegada = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS)
    aeronave = models.ForeignKey(Aeronave, on_delete=models.CASCADE)

    def __str__(self):
        return f"Voo {self.numero_voo} - {self.origem} → {self.destino}"


class Reserva(models.Model):
    STATUS = [
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    passageiro = models.ForeignKey(Passageiro, on_delete=models.CASCADE)
    voo = models.ForeignKey(Voo, on_delete=models.CASCADE)
    assento = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f"Reserva {self.id} - {self.passageiro.nome}"


class Bilhete(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=100, unique=True)
    data_emissao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bilhete {self.codigo}"


class Bagagem(models.Model):
    STATUS = [
        ('despachada', 'Despachada'),
        ('em_transito', 'Em trânsito'),
        ('entregue', 'Entregue'),
    ]
    passageiro = models.ForeignKey(Passageiro, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f"Bagagem {self.id} - {self.passageiro.nome}"


class CheckIn(models.Model):
    STATUS = [
        ('realizado', 'Realizado'),
        ('pendente', 'Pendente'),
    ]
    passageiro = models.ForeignKey(Passageiro, on_delete=models.CASCADE)
    voo = models.ForeignKey(Voo, on_delete=models.CASCADE)
    data_hora = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f"Check-in {self.id} - {self.passageiro.nome}"


class PortaoEmbarque(models.Model):
    STATUS = [
        ('livre', 'Livre'),
        ('ocupado', 'Ocupado'),
    ]
    numero_portao = models.CharField(max_length=10, unique=True)
    localizacao = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f"Portão {self.numero_portao}"


class Notificacao(models.Model):
    TIPOS = [
        ('atraso', 'Alerta de atraso'),
        ('mudanca_portao', 'Mudança de portão'),
    ]
    passageiro = models.ForeignKey(Passageiro, on_delete=models.CASCADE)
    mensagem = models.TextField()
    data_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)

    def __str__(self):
        return f"Notificação {self.tipo} - {self.passageiro.nome}"
