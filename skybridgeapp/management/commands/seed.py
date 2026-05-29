from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from skybridgeapp.models import (
    Aeroporto,
    Aeronave,
    CompanhiaAerea,
    PortaoEmbarque,
    Promocao,
    Reserva,
    Tarifa,
    Voo,
)


GERADO_PREFIXO = 'SB'
PROMO_PREFIXO = 'Oferta nacional'
VOOS_LEGADOS_EXEMPLO = [
    'MM1001', 'MM1002', 'MM2001', 'MM3001', 'MM4001',
    'MM5001', 'MM5002', 'MM5003', 'MM5004', 'MM5005',
    'MM5006', 'MM5007', 'MM5008',
]


class Command(BaseCommand):
    help = "Popula o banco de dados com voos nacionais de exemplo."

    aeroportos_data = [
        ('GRU', 'Aeroporto Internacional de Guarulhos', 'Sao Paulo', 'SP'),
        ('GIG', 'Aeroporto Internacional do Galeao', 'Rio de Janeiro', 'RJ'),
        ('BSB', 'Aeroporto Internacional de Brasilia', 'Brasilia', 'DF'),
        ('REC', 'Aeroporto Internacional do Recife', 'Recife', 'PE'),
        ('SSA', 'Aeroporto Internacional de Salvador', 'Salvador', 'BA'),
        ('MAO', 'Aeroporto Internacional de Manaus', 'Manaus', 'AM'),
        ('BEL', 'Aeroporto Internacional de Belem', 'Belem', 'PA'),
        ('CWB', 'Aeroporto Internacional Afonso Pena', 'Curitiba', 'PR'),
        ('POA', 'Aeroporto Internacional de Porto Alegre', 'Porto Alegre', 'RS'),
        ('CGB', 'Aeroporto Internacional Marechal Rondon', 'Cuiaba', 'MT'),
    ]

    duracoes_minutos = {
        ('GRU', 'GIG'): 65,
        ('GRU', 'CWB'): 70,
        ('GRU', 'BSB'): 105,
        ('GRU', 'POA'): 110,
        ('GRU', 'CGB'): 135,
        ('GRU', 'SSA'): 145,
        ('GRU', 'REC'): 180,
        ('GRU', 'BEL'): 210,
        ('GRU', 'MAO'): 240,
        ('BSB', 'REC'): 150,
        ('BSB', 'SSA'): 120,
        ('BSB', 'MAO'): 190,
        ('BSB', 'BEL'): 160,
        ('BSB', 'CGB'): 105,
        ('REC', 'SSA'): 85,
        ('MAO', 'BEL'): 125,
        ('CWB', 'POA'): 80,
        ('BEL', 'REC'): 155,
        ('CGB', 'MAO'): 145,
    }

    precos_base = {
        ('GRU', 'GIG'): Decimal('179.90'),
        ('GRU', 'CWB'): Decimal('209.90'),
        ('GRU', 'BSB'): Decimal('279.90'),
        ('GRU', 'POA'): Decimal('259.90'),
        ('GRU', 'CGB'): Decimal('379.90'),
        ('GRU', 'SSA'): Decimal('299.90'),
        ('GRU', 'REC'): Decimal('329.90'),
        ('GRU', 'BEL'): Decimal('559.90'),
        ('GRU', 'MAO'): Decimal('599.90'),
        ('BSB', 'REC'): Decimal('359.90'),
        ('BSB', 'SSA'): Decimal('329.90'),
        ('BSB', 'MAO'): Decimal('519.90'),
        ('BSB', 'BEL'): Decimal('449.90'),
        ('BSB', 'CGB'): Decimal('289.90'),
        ('REC', 'SSA'): Decimal('219.90'),
        ('MAO', 'BEL'): Decimal('339.90'),
        ('CWB', 'POA'): Decimal('229.90'),
        ('BEL', 'REC'): Decimal('429.90'),
        ('CGB', 'MAO'): Decimal('469.90'),
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Remove apenas voos, tarifas e promocoes de exemplo criados por este comando.',
        )

    def handle(self, *args, **options):
        if options['limpar']:
            removidos = self._limpar_dados_exemplo()
            self.stdout.write(self.style.SUCCESS(
                f"Dados de exemplo removidos: {removidos['voos']} voos, "
                f"{removidos['tarifas']} tarifas e {removidos['promocoes']} promocoes."
            ))
            return

        self.stdout.write("Criando malha nacional de exemplo...")

        aeroportos = self._criar_aeroportos()
        self._criar_companhias()
        aeronaves = self._criar_aeronaves()
        portoes = self._criar_portoes()
        voos = self._criar_voos(aeroportos, aeronaves, portoes)
        total_tarifas = self._criar_tarifas(voos)
        total_promocoes = self._criar_promocoes(aeroportos)

        self.stdout.write(self.style.SUCCESS(
            f"Banco populado com sucesso! {len(aeroportos)} aeroportos, "
            f"{len(voos)} voos, {total_tarifas} tarifas e {total_promocoes} promocoes."
        ))

    def _limpar_dados_exemplo(self):
        voos_gerados = Voo.objects.filter(
            Q(numero_voo__startswith=GERADO_PREFIXO) | Q(numero_voo__in=VOOS_LEGADOS_EXEMPLO)
        )
        voos_protegidos = Reserva.objects.filter(voo__in=voos_gerados).values_list('voo_id', flat=True)
        voos_removiveis = voos_gerados.exclude(id__in=voos_protegidos)

        tarifas_removidas = Tarifa.objects.filter(voo__in=voos_removiveis).delete()[0]
        voos_removidos = voos_removiveis.delete()[0]
        promocoes_removidas = Promocao.objects.filter(titulo__startswith=PROMO_PREFIXO).delete()[0]

        if voos_gerados.filter(id__in=voos_protegidos).exists():
            self.stdout.write(self.style.WARNING(
                'Alguns voos de exemplo foram mantidos porque possuem reservas vinculadas.'
            ))

        return {
            'voos': voos_removidos,
            'tarifas': tarifas_removidas,
            'promocoes': promocoes_removidas,
        }

    def _criar_aeroportos(self):
        aeroportos = {}
        for codigo, nome, cidade, estado in self.aeroportos_data:
            aeroporto, _ = Aeroporto.objects.update_or_create(
                codigo_iata=codigo,
                defaults={
                    'nome': nome,
                    'cidade': cidade,
                    'estado': estado,
                    'pais': 'Brasil',
                },
            )
            aeroportos[codigo] = aeroporto
        return aeroportos

    def _criar_companhias(self):
        for dados in [
            {'nome': 'Sky Bridge Linhas Aereas', 'codigo_iata': 'SB', 'pais': 'Brasil'},
            {'nome': 'Azul Linhas Aereas', 'codigo_iata': 'AD', 'pais': 'Brasil'},
            {'nome': 'Gol Linhas Aereas', 'codigo_iata': 'G3', 'pais': 'Brasil'},
        ]:
            CompanhiaAerea.objects.update_or_create(
                codigo_iata=dados['codigo_iata'],
                defaults=dados,
            )

    def _criar_aeronaves(self):
        aeronaves_data = [
            ('Airbus A320', 'Sky Bridge Linhas Aereas', 180),
            ('Embraer E195', 'Azul Linhas Aereas', 136),
            ('Boeing 737-800', 'Gol Linhas Aereas', 186),
        ]
        aeronaves = []

        for modelo, companhia, capacidade in aeronaves_data:
            aeronave, _ = Aeronave.objects.update_or_create(
                modelo=modelo,
                companhia_aerea=companhia,
                defaults={'capacidade': capacidade},
            )
            aeronaves.append(aeronave)

        return aeronaves

    def _criar_portoes(self):
        portoes_data = [
            ('A01', 'Terminal 1', 'livre'),
            ('A02', 'Terminal 1', 'livre'),
            ('B01', 'Terminal 2', 'livre'),
            ('B02', 'Terminal 2', 'ocupado'),
            ('C01', 'Terminal 3', 'livre'),
        ]
        portoes = []

        for numero, localizacao, status in portoes_data:
            portao, _ = PortaoEmbarque.objects.update_or_create(
                numero_portao=numero,
                defaults={'localizacao': localizacao, 'status': status},
            )
            portoes.append(portao)

        return portoes

    def _criar_voos(self, aeroportos, aeronaves, portoes):
        rotas = self._rotas_nacionais()
        inicio = timezone.localdate() + timedelta(days=1)
        fim = date(inicio.year, 12, 31)
        if inicio > fim:
            fim = inicio + timedelta(days=180)

        voos = []
        data_atual = inicio

        while data_atual <= fim:
            for indice, rota in enumerate(rotas, start=1):
                if not self._deve_criar_voo(data_atual, rota['frequencia']):
                    continue

                partida = self._datetime_voo(data_atual, indice)
                chegada = partida + timedelta(minutes=self._duracao_rota(rota['origem'], rota['destino']))
                numero_voo = f"{GERADO_PREFIXO}{data_atual:%y%m%d}{indice:03d}"

                voo, _ = Voo.objects.update_or_create(
                    numero_voo=numero_voo,
                    defaults={
                        'origem': self._rotulo_aeroporto(aeroportos[rota['origem']]),
                        'destino': self._rotulo_aeroporto(aeroportos[rota['destino']]),
                        'partida': partida,
                        'chegada': chegada,
                        'status': 'programado',
                        'aeronave': aeronaves[indice % len(aeronaves)],
                        'portao': portoes[indice % len(portoes)],
                    },
                )
                voos.append((voo, rota, data_atual, indice))

            data_atual += timedelta(days=1)

        return voos

    def _rotas_nacionais(self):
        rotas = []
        aeroportos_sem_gru = ['GIG', 'BSB', 'REC', 'SSA', 'MAO', 'BEL', 'CWB', 'POA', 'CGB']

        for codigo in aeroportos_sem_gru:
            rotas.append({'origem': 'GRU', 'destino': codigo, 'frequencia': 'diaria'})
            rotas.append({'origem': codigo, 'destino': 'GRU', 'frequencia': 'diaria'})

        for codigo in ['REC', 'SSA', 'MAO', 'BEL', 'CGB']:
            rotas.append({'origem': 'BSB', 'destino': codigo, 'frequencia': 'quatro_semana'})
            rotas.append({'origem': codigo, 'destino': 'BSB', 'frequencia': 'quatro_semana'})

        for origem, destino in [('REC', 'SSA'), ('MAO', 'BEL'), ('CWB', 'POA'), ('BEL', 'REC'), ('CGB', 'MAO')]:
            rotas.append({'origem': origem, 'destino': destino, 'frequencia': 'tres_semana'})
            rotas.append({'origem': destino, 'destino': origem, 'frequencia': 'tres_semana'})

        return rotas

    def _deve_criar_voo(self, data_voo, frequencia):
        if frequencia == 'diaria':
            return True
        if frequencia == 'quatro_semana':
            return data_voo.weekday() in {0, 2, 4, 6}
        if frequencia == 'tres_semana':
            return data_voo.weekday() in {1, 3, 5}
        return False

    def _datetime_voo(self, data_voo, indice_rota):
        hora = 6 + ((indice_rota * 2) % 15)
        minuto = (indice_rota * 10) % 60
        naive = datetime.combine(data_voo, time(hour=hora, minute=minuto))
        return timezone.make_aware(naive, timezone.get_current_timezone())

    def _criar_tarifas(self, voos):
        voos_objetos = [voo for voo, _, _, _ in voos]
        Tarifa.objects.filter(voo__in=voos_objetos).delete()

        tarifas = []
        for voo, rota, data_voo, indice_rota in voos:
            preco_economy = self._preco_rota(rota['origem'], rota['destino'], data_voo, indice_rota)
            tarifas.extend([
                self._tarifa(voo, 'economy', preco_economy, Decimal('49.90')),
                self._tarifa(voo, 'premium_economy', preco_economy * Decimal('1.55'), Decimal('79.90')),
                self._tarifa(voo, 'executiva', preco_economy * Decimal('2.35'), Decimal('119.90')),
            ])

        Tarifa.objects.bulk_create(tarifas, batch_size=1000)
        return len(tarifas)

    def _tarifa(self, voo, classe, preco_base, taxas):
        return Tarifa(
            voo=voo,
            classe=classe,
            preco_base=self._moeda(preco_base),
            taxas=self._moeda(taxas),
            ativa=True,
        )

    def _preco_rota(self, origem, destino, data_voo, indice_rota):
        preco = self._preco_base_rota(origem, destino)

        if data_voo.weekday() in {4, 5, 6}:
            preco *= Decimal('1.12')
        if data_voo.day in {7, 17, 27} or indice_rota % 9 == 0:
            preco *= Decimal('0.88')

        return self._moeda(preco)

    def _preco_base_rota(self, origem, destino):
        chave = self._chave_rota(origem, destino)
        return self.precos_base.get(chave, Decimal('399.90'))

    def _duracao_rota(self, origem, destino):
        chave = self._chave_rota(origem, destino)
        return self.duracoes_minutos.get(chave, 130)

    def _chave_rota(self, origem, destino):
        if (origem, destino) in self.precos_base or (origem, destino) in self.duracoes_minutos:
            return origem, destino
        return destino, origem

    def _criar_promocoes(self, aeroportos):
        hoje = timezone.localdate()
        promocoes = [
            ('Sao Paulo para Rio de Janeiro', 'GRU', 'GIG', '189.90'),
            ('Sao Paulo para Recife', 'GRU', 'REC', '329.90'),
            ('Sao Paulo para Brasilia', 'GRU', 'BSB', '289.90'),
            ('Porto Alegre para Sao Paulo', 'POA', 'GRU', '259.90'),
            ('Brasilia para Manaus', 'BSB', 'MAO', '519.90'),
        ]

        for titulo, origem, destino, preco in promocoes:
            Promocao.objects.update_or_create(
                titulo=f'{PROMO_PREFIXO}: {titulo}',
                defaults={
                    'descricao': 'Oferta nacional de exemplo para a landing page.',
                    'origem': aeroportos[origem],
                    'destino': aeroportos[destino],
                    'preco_a_partir_de': Decimal(preco),
                    'data_inicio': hoje,
                    'data_fim': date(hoje.year, 12, 31),
                    'ativa': True,
                },
            )

        return len(promocoes)

    def _rotulo_aeroporto(self, aeroporto):
        return f'{aeroporto.codigo_iata} - {aeroporto.cidade}'

    def _moeda(self, valor):
        return Decimal(valor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
