from core.management.commands.base_seed import BaseSeedCommand
from consent_form.models import ConsentTerm


class Command(BaseSeedCommand):
    seed_name = "seed_consent_terms"
    seed_description = "Termos de consentimento"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--terms",
            type=int,
            default=5,
            help="Quantidade de versões de termos para criar (default: 5)",
        )

    def _clear_data(self, options):
        self.stdout.write("🧹 Limpando termos de consentimento… ", ending="")
        ConsentTerm.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("OK"))

    def handle_seed(self, fake, *args, **options):
        n = options.get("terms", 5)

        # versões sequenciais 1..n com URLs fakes
        objs = [
            ConsentTerm(version=i + 1, url=fake.url()) for i in range(n)
        ]
        created = self.bulk_create_with_progress(ConsentTerm, objs, batch_size=100)

        return {"terms_created": len(created)}
