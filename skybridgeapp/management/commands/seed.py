from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from skybridgeapp.models import (
    UsuarioCustomizado,
    Passageiro,
    ContaMilhas,
    TransacaoMilhas,
    Funcionario,
    Aeroporto,
    CompanhiaAerea,
    Aeronave,
    PortaoEmbarque,
    Voo,
    Tarifa,
    Promocao,
    Reserva,
    Pagamento,
    Bilhete,
    Bagagem,
    CheckIn,
    Notificacao,
)


class Command(BaseCommand):
    help = "Popula o banco de dados com dados iniciais para teste"

    def handle(self, *args, **kwargs):
        self.stdout.write("Limpando/criando dados iniciais...")

        # =========================
        # Aeroportos nacionais
        # =========================

        aeroportos_data = [
            {
                "codigo_iata": "GRU",
                "nome": "Aeroporto Internacional de Guarulhos",
                "cidade": "São Paulo",
                "estado": "SP",
                "pais": "Brasil",
            },
            {
                "codigo_iata": "CNF",
                "nome": "Aeroporto Internacional de Confins",
                "cidade": "Belo Horizonte",
                "estado": "MG",
                "pais": "Brasil",
            },
            {
                "codigo_iata": "BSB",
                "nome": "Aeroporto Internacional de Brasília",
                "cidade": "Brasília",
                "estado": "DF",
                "pais": "Brasil",
            },
            {
                "codigo_iata": "REC",
                "nome": "Aeroporto Internacional do Recife",
                "cidade": "Recife",
                "estado": "PE",
                "pais": "Brasil",
            },
            {
                "codigo_iata": "MAO",
                "nome": "Aeroporto Internacional de Manaus",
                "cidade": "Manaus",
                "estado": "AM",
                "pais": "Brasil",
            },
            {
                "codigo_iata": "POA",
                "nome": "Aeroporto Internacional de Porto Alegre",
                "cidade": "Porto Alegre",
                "estado": "RS",
                "pais": "Brasil",
            },
        ]

        aeroportos = {}

        for dados in aeroportos_data:
            aeroporto, _ = Aeroporto.objects.get_or_create(
                codigo_iata=dados["codigo_iata"],
                defaults=dados,
            )
            aeroportos[dados["codigo_iata"]] = aeroporto

        # =========================
        # Companhias aéreas
        # =========================

        companhias_data = [
            {
                "nome": "Latam Airlines Brasil",
                "codigo_iata": "LA",
                "pais": "Brasil",
            },
            {
                "nome": "Azul Linhas Aéreas",
                "codigo_iata": "AD",
                "pais": "Brasil",
            },
            {
                "nome": "Gol Linhas Aéreas",
                "codigo_iata": "G3",
                "pais": "Brasil",
            },
        ]

        for dados in companhias_data:
            CompanhiaAerea.objects.get_or_create(
                codigo_iata=dados["codigo_iata"],
                defaults=dados,
            )

        # =========================
        # Aeronaves
        # Seu model Aeronave usa companhia_aerea como CharField,
        # então aqui salvamos apenas o nome da companhia.
        # =========================

        aeronave_1, _ = Aeronave.objects.get_or_create(
            modelo="Airbus A320",
            companhia_aerea="Latam Airlines Brasil",
            defaults={
                "capacidade": 180,
            },
        )

        aeronave_2, _ = Aeronave.objects.get_or_create(
            modelo="Embraer E195",
            companhia_aerea="Azul Linhas Aéreas",
            defaults={
                "capacidade": 136,
            },
        )

        aeronave_3, _ = Aeronave.objects.get_or_create(
            modelo="Boeing 737-800",
            companhia_aerea="Gol Linhas Aéreas",
            defaults={
                "capacidade": 186,
            },
        )

        # =========================
        # Portões
        # =========================

        portao_1, _ = PortaoEmbarque.objects.get_or_create(
            numero_portao="A01",
            defaults={
                "localizacao": "Terminal 1",
                "status": "livre",
            },
        )

        portao_2, _ = PortaoEmbarque.objects.get_or_create(
            numero_portao="B02",
            defaults={
                "localizacao": "Terminal 2",
                "status": "ocupado",
            },
        )

        portao_3, _ = PortaoEmbarque.objects.get_or_create(
            numero_portao="C03",
            defaults={
                "localizacao": "Terminal 3",
                "status": "livre",
            },
        )

        # =========================
        # Voos
        # Atenção: no seu model Voo, origem e destino são CharField,
        # não ForeignKey para Aeroporto.
        # Então vamos salvar "GRU - São Paulo", por exemplo.
        # =========================

        agora = timezone.now()

        voos_data = [
            {
                "numero_voo": "MM1001",
                "origem": "GRU - São Paulo",
                "destino": "REC - Recife",
                "partida": agora + timedelta(days=1, hours=8),
                "chegada": agora + timedelta(days=1, hours=11),
                "status": "programado",
                "aeronave": aeronave_1,
                "portao": portao_1,
            },
            {
                "numero_voo": "MM1002",
                "origem": "REC - Recife",
                "destino": "GRU - São Paulo",
                "partida": agora + timedelta(days=2, hours=9),
                "chegada": agora + timedelta(days=2, hours=12),
                "status": "programado",
                "aeronave": aeronave_1,
                "portao": portao_2,
            },
            {
                "numero_voo": "MM2001",
                "origem": "GRU - São Paulo",
                "destino": "POA - Porto Alegre",
                "partida": agora + timedelta(days=1, hours=14),
                "chegada": agora + timedelta(days=1, hours=16),
                "status": "programado",
                "aeronave": aeronave_3,
                "portao": portao_3,
            },
            {
                "numero_voo": "MM3001",
                "origem": "BSB - Brasília",
                "destino": "MAO - Manaus",
                "partida": agora + timedelta(days=3, hours=10),
                "chegada": agora + timedelta(days=3, hours=14),
                "status": "atrasado",
                "aeronave": aeronave_2,
                "portao": portao_1,
            },
            {
                "numero_voo": "MM4001",
                "origem": "CNF - Belo Horizonte",
                "destino": "BSB - Brasília",
                "partida": agora + timedelta(days=4, hours=7),
                "chegada": agora + timedelta(days=4, hours=9),
                "status": "programado",
                "aeronave": aeronave_2,
                "portao": portao_2,
            },
        ]

        voos = {}

        for dados in voos_data:
            voo, _ = Voo.objects.get_or_create(
                numero_voo=dados["numero_voo"],
                defaults=dados,
            )
            voos[dados["numero_voo"]] = voo

        # =========================
        # Tarifas
        # =========================

        for voo in voos.values():
            Tarifa.objects.get_or_create(
                voo=voo,
                classe="economy",
                defaults={
                    "preco_base": Decimal("499.90"),
                    "taxas": Decimal("89.90"),
                    "ativa": True,
                },
            )

            Tarifa.objects.get_or_create(
                voo=voo,
                classe="premium_economy",
                defaults={
                    "preco_base": Decimal("799.90"),
                    "taxas": Decimal("109.90"),
                    "ativa": True,
                },
            )

            Tarifa.objects.get_or_create(
                voo=voo,
                classe="executiva",
                defaults={
                    "preco_base": Decimal("1299.90"),
                    "taxas": Decimal("149.90"),
                    "ativa": True,
                },
            )

        # =========================
        # Promoções
        # =========================

        Promocao.objects.get_or_create(
            titulo="São Paulo para Recife",
            defaults={
                "descricao": "Promoção especial para voos nacionais.",
                "origem": aeroportos["GRU"],
                "destino": aeroportos["REC"],
                "preco_a_partir_de": Decimal("499.90"),
                "data_inicio": agora.date(),
                "data_fim": (agora + timedelta(days=30)).date(),
                "ativa": True,
            },
        )

        Promocao.objects.get_or_create(
            titulo="Brasília para Manaus",
            defaults={
                "descricao": "Conheça o Norte do Brasil com tarifa promocional.",
                "origem": aeroportos["BSB"],
                "destino": aeroportos["MAO"],
                "preco_a_partir_de": Decimal("599.90"),
                "data_inicio": agora.date(),
                "data_fim": (agora + timedelta(days=30)).date(),
                "ativa": True,
            },
        )

        # =========================
        # Usuários, passageiros e funcionários
        # =========================

        usuario_passageiro, criado = UsuarioCustomizado.objects.get_or_create(
            username="joao",
            defaults={
                "email": "joao@email.com",
                "tipo": "passageiro",
                "first_name": "João",
                "last_name": "Silva",
            },
        )

        if criado:
            usuario_passageiro.set_password("123456")
            usuario_passageiro.save()

        passageiro, _ = Passageiro.objects.get_or_create(
            cpf_passaporte="12345678900",
            defaults={
                "usuario": usuario_passageiro,
                "nome": "João Silva",
                "data_nascimento": "1998-05-20",
                "contato": "(11) 99999-9999",
                "nacionalidade": "Brasileira",
            },
        )

        conta, _ = ContaMilhas.objects.get_or_create(
            passageiro=passageiro,
            defaults={
                "saldo": 15000,
                "numero_programa": "MM-JOAO-001",
            },
        )

        TransacaoMilhas.objects.get_or_create(
            conta=conta,
            tipo="acumulo",
            quantidade=15000,
            descricao="Milhas iniciais de boas-vindas",
        )

        usuario_funcionario, criado = UsuarioCustomizado.objects.get_or_create(
            username="funcionario",
            defaults={
                "email": "funcionario@email.com",
                "tipo": "funcionario",
                "first_name": "Maria",
                "last_name": "Souza",
            },
        )

        if criado:
            usuario_funcionario.set_password("123456")
            usuario_funcionario.save()

        Funcionario.objects.get_or_create(
            matricula="FUNC001",
            defaults={
                "usuario": usuario_funcionario,
                "nome": "Maria Souza",
                "cargo": "atendente",
                "contato": "(31) 98888-8888",
            },
        )

        usuario_admin, criado = UsuarioCustomizado.objects.get_or_create(
            username="admin_teste",
            defaults={
                "email": "admin@email.com",
                "tipo": "administrador",
                "first_name": "Admin",
                "last_name": "Teste",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if criado:
            usuario_admin.set_password("123456")
            usuario_admin.save()

        # =========================
        # Reserva, pagamento, bilhete, bagagem, check-in e notificação
        # =========================

        voo_reserva = voos["MM1001"]

        reserva, _ = Reserva.objects.get_or_create(
            passageiro=passageiro,
            voo=voo_reserva,
            assento="12A",
            defaults={
                "status": "confirmada",
            },
        )

        Pagamento.objects.get_or_create(
            reserva=reserva,
            defaults={
                "valor_total": Decimal("589.80"),
                "metodo": "pix",
                "status": "aprovado",
                "data_pagamento": agora,
            },
        )

        Bilhete.objects.get_or_create(
            reserva=reserva,
            defaults={
                "codigo": "BIL-MM1001-JOAO",
            },
        )

        Bagagem.objects.get_or_create(
            numero_rastreio="BAG123456",
            defaults={
                "reserva": reserva,
                "peso": Decimal("18.50"),
                "status": "despachada",
            },
        )

        CheckIn.objects.get_or_create(
            passageiro=passageiro,
            voo=voo_reserva,
            defaults={
                "status": "realizado",
            },
        )

        Notificacao.objects.get_or_create(
            passageiro=passageiro,
            mensagem="Seu voo MM1001 está confirmado. Boa viagem!",
            tipo="geral",
            defaults={
                "lida": False,
            },
        )

        self.stdout.write(self.style.SUCCESS("Banco populado com sucesso!"))