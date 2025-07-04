from core.management.commands.base_seed import BaseSeedCommand
from address.models import Address


class Command(BaseSeedCommand):
    seed_name = "addresses"
    seed_description = "Endereços brasileiros"
    help = 'Seed endereços com dados realistas brasileiros'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Número de endereços para criar (padrão: 50)'
        )

    def handle_seed(self, fake, *args, **options):
        """Executa o seed de endereços"""
        count = options['count']
        addresses = self._create_addresses(fake, count)
        
        return {"endereços": addresses}

    def _clear_data(self, options):
        """Limpa endereços existentes"""
        self.stdout.write('🧹 Removendo endereços existentes...')
        deleted_count = Address.objects.count()
        Address.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'✅ {deleted_count} endereços removidos!')
        )

    def _create_addresses(self, fake, count):
        """Cria endereços com dados realistas brasileiros"""
        self.stdout.write(f'📍 Criando {count} endereços...')
        
        # Estados brasileiros mais populosos
        brazilian_states = [
            ('SP', 'São Paulo'),
            ('RJ', 'Rio de Janeiro'), 
            ('MG', 'Minas Gerais'),
            ('RS', 'Rio Grande do Sul'),
            ('PR', 'Paraná'),
            ('SC', 'Santa Catarina'),
            ('BA', 'Bahia'),
            ('GO', 'Goiás'),
            ('PE', 'Pernambuco'),
            ('CE', 'Ceará')
        ]
        
        addresses = []
        created_count = 0
        
        for i in range(count):
            state_code, state_name = fake.random_element(brazilian_states)
            
            # CEP brasileiro válido (formato: 12345678)
            cep = fake.postcode().replace('-', '')
            if len(cep) != 8:
                cep = f"{fake.random_int(min=10000, max=99999)}{fake.random_int(min=100, max=999)}"
            
            # Garantir que o CEP + número seja único
            number = fake.random_int(min=1, max=9999)
            max_attempts = 10
            attempts = 0
            
            while Address.objects.filter(cep=cep, number=number).exists() and attempts < max_attempts:
                cep = f"{fake.random_int(min=10000, max=99999)}{fake.random_int(min=100, max=999)}"
                number = fake.random_int(min=1, max=9999)
                attempts += 1
            
            if attempts >= max_attempts:
                continue  # Pular se não conseguir encontrar combinação única
            
            # Coordenadas aproximadas do Brasil
            lat_bounds = (-33.7, 5.3)  # Sul a Norte
            lon_bounds = (-73.9, -34.7)  # Oeste a Leste
            
            address = Address(
                cep=cep,
                country='Brasil',
                state=state_name,
                city=fake.city(),
                neighborhood=fake.bairro() if hasattr(fake, 'bairro') else f"Bairro {fake.word()}",
                street=fake.street_name(),
                number=number,
                latitude=fake.pyfloat(
                    left_digits=2, right_digits=6, 
                    positive=False,
                    min_value=lat_bounds[0], max_value=lat_bounds[1]
                ),
                longitude=fake.pyfloat(
                    left_digits=2, right_digits=6,
                    positive=False, 
                    min_value=lon_bounds[0], max_value=lon_bounds[1]
                ),
            )
            addresses.append(address)
            created_count += 1

        # Usar bulk_create para performance
        try:
            Address.objects.bulk_create(addresses, ignore_conflicts=True)
            actual_created = Address.objects.filter(
                cep__in=[a.cep for a in addresses]
            ).count()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ {actual_created} endereços criados!')
            )
            
            return actual_created
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar endereços: {e}')
            )
            return 0
