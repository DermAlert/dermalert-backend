from django.conf import settings
from django.core.management.base import BaseCommand
from core.minio_utils import (
    create_bucket_if_not_exists,
    set_read_only_prefixes,
    upload_test_file,
)


class Command(BaseCommand):
    """
    Configura o MinIO/S3 para o projeto:

    • Verifica/Cria o bucket
    • Libera leitura anônima no prefixo static/
    • (Opcional) Faz upload de um arquivo de teste
    """

    help = "Cria bucket (se não existir) e aplica bucket-policy em static/* e media/*"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-policy",
            action="store_true",
            help="Não aplica a bucket-policy (apenas cria/verifica o bucket)",
        )
        parser.add_argument(
            "--test-upload",
            action="store_true",
            help="Envia um arquivo de teste depois da configuração",
        )

    def handle(self, *args, **opts):
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        self.stdout.write(f"Bucket alvo: {bucket}")

        # 1) bucket
        self.stdout.write("‣ Verificando bucket… ", ending="")
        create_bucket_if_not_exists(bucket)
        self.stdout.write(self.style.SUCCESS("OK"))

        # 2) policy
        if not opts["skip_policy"]:
            self.stdout.write("‣ Aplicando bucket-policy em static/* e media/*… ", ending="")
            set_read_only_prefixes(bucket)
            self.stdout.write(self.style.SUCCESS("OK"))

        # 3) upload de teste
        if opts["test_upload"]:
            self.stdout.write("‣ Enviando arquivo de teste… ", ending="")
            if upload_test_file():
                self.stdout.write(self.style.SUCCESS("OK"))
            else:
                self.stdout.write(self.style.ERROR("Falhou"))
