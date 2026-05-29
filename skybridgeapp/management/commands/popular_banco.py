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

    def handle(self, *args, **options):
        argumentos = ['--limpar'] if options['limpar'] else []
        call_command('seed', *argumentos, stdout=self.stdout)
