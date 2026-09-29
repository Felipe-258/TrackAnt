from django.core.management.base import BaseCommand
from finances.models import Currency, Category


class Command(BaseCommand):
    help = 'Seed initial data: currencies and categories'

    def add_arguments(self, parser):
        parser.add_argument('--colony-id', type=int, default=None,
                            help='ID de colonia para crear datos personalizados')

    def handle(self, *args, **options):
        colony_id = options['colony_id']
        self._currencies(colony_id)
        self._categories(colony_id)
        self.stdout.write(self.style.SUCCESS('✅ Datos iniciales creados'))

    def _currencies(self, colony_id):
        currencies = [
            ('ARS', '$', 'Peso Argentino', 1.0),
            ('USD', 'U$S', 'Dólar Estadounidense', 1200.0),
            ('EUR', '€', 'Euro', 1300.0),
            ('BRL', 'R$', 'Real Brasileño', 220.0),
            ('CLP', '$', 'Peso Chileno', 1.3),
            ('UYU', '$U', 'Peso Uruguayo', 30.0),
        ]
        for code, symbol, name, rate in currencies:
            Currency.objects.get_or_create(
                code=code, colony_id=colony_id,
                defaults={'symbol': symbol, 'name': name, 'rate_to_base': rate}
            )
        self.stdout.write(f'  Monedas: {len(currencies)} creadas')

    def _categories(self, colony_id):
        income_categories = [
            ('Salario', 'wallet', '#6E8F4C'),
            ('Freelance', 'briefcase', '#8BA864'),
            ('Inversiones', 'trending-up', '#C4943A'),
            ('Regalos', 'gift', '#D4A857'),
            ('Ventas', 'shopping-bag', '#A07858'),
            ('Otros ingresos', 'package', '#8A6348'),
        ]
        expense_categories = [
            ('Comida', 'pizza', '#D4764A'),
            ('Supermercado', 'shopping-cart', '#C16645'),
            ('Transporte', 'bus', '#A0522D'),
            ('Vivienda', 'home', '#6E4E38'),
            ('Servicios', 'lightbulb', '#8A6348'),
            ('Salud', 'heart-pulse', '#5A753F'),
            ('Educación', 'graduation-cap', '#485D35'),
            ('Entretenimiento', 'film', '#ECA776'),
            ('Ropa', 'shirt', '#E4864C'),
            ('Tecnología', 'laptop', '#7A3F23'),
            ('Mascotas', 'heart', '#B89472'),
            ('Viajes', 'plane', '#C4943A'),
            ('Gimnasio', 'dumbbell', '#5C2E19'),
            ('Regalos', 'gift', '#D4A857'),
            ('Otros gastos', 'package', '#8A6348'),
        ]
        for name, icon, color in income_categories:
            Category.objects.get_or_create(
                name=name, type='INCOME', colony_id=colony_id,
                defaults={'icon': icon, 'color': color}
            )
        for name, icon, color in expense_categories:
            Category.objects.get_or_create(
                name=name, type='EXPENSE', colony_id=colony_id,
                defaults={'icon': icon, 'color': color}
            )
        self.stdout.write(f'  Categorías: {len(income_categories) + len(expense_categories)} creadas')
