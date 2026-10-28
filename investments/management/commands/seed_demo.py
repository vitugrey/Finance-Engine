from django.core.management.base import BaseCommand
from core.demo_seed import reset_and_seed_demo


class Command(BaseCommand):
    help = "Restaura e popula o banco de dados local com os dados demonstrativos oficiais da GreyWorks Finance Engine."

    def handle(self, *args, **options):
        reset_and_seed_demo()
        self.stdout.write(
            self.style.SUCCESS("Dados demonstrativos do Finance Engine (by GreyWorks) carregados com sucesso!")
        )
