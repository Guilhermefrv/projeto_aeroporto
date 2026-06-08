from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Popula o banco de dados com dados iniciais do Sky Bridge."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Remove apenas dados de exemplo criados pelo comando.',
        )
        parser.add_argument(
            '--usuarios-demo',
            action='store_true',
            help='Cria usuarios de demonstracao para apresentar os fluxos do sistema.',
        )

    def handle(self, *args, **options):
        argumentos = []
        if options['limpar']:
            argumentos.append('--limpar')
        if options['usuarios_demo']:
            argumentos.append('--usuarios-demo')
        call_command('seed', *argumentos, stdout=self.stdout)
