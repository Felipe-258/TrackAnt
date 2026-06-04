from django.core.management.base import BaseCommand
from finances.models import Currency, Category, Tag


class Command(BaseCommand):
    help = 'Seed initial data: currencies, categories, and tags'

    def handle(self, *args, **options):
        self._currencies()
        self._categories()
        self._tags()
        self.stdout.write(self.style.SUCCESS('✅ Datos iniciales creados'))

    def _currencies(self):
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
                code=code,
                defaults={'symbol': symbol, 'name': name, 'rate_to_base': rate}
            )
        self.stdout.write(f'  Monedas: {len(currencies)} creadas')

    def _categories(self):
        income_categories = [
            ('Salario', '💰', '#6E8F4C'),
            ('Freelance', '💼', '#8BA864'),
            ('Inversiones', '📈', '#C4943A'),
            ('Regalos', '🎁', '#D4A857'),
            ('Ventas', '🛍️', '#A07858'),
            ('Otros ingresos', '📦', '#8A6348'),
        ]
        expense_categories = [
            ('Comida', '🍕', '#D4764A'),
            ('Supermercado', '🛒', '#C16645'),
            ('Transporte', '🚌', '#A0522D'),
            ('Vivienda', '🏠', '#6E4E38'),
            ('Servicios', '💡', '#8A6348'),
            ('Salud', '🏥', '#5A753F'),
            ('Educación', '📚', '#485D35'),
            ('Entretenimiento', '🎬', '#ECA776'),
            ('Ropa', '👕', '#E4864C'),
            ('Tecnología', '💻', '#7A3F23'),
            ('Mascotas', '🐱', '#B89472'),
            ('Viajes', '✈️', '#C4943A'),
            ('Gimnasio', '🏋️', '#5C2E19'),
            ('Regalos', '🎁', '#D4A857'),
            ('Otros gastos', '📦', '#8A6348'),
        ]
        for name, icon, color in income_categories:
            Category.objects.get_or_create(
                name=name, type='INCOME',
                defaults={'icon': icon, 'color': color}
            )
        for name, icon, color in expense_categories:
            Category.objects.get_or_create(
                name=name, type='EXPENSE',
                defaults={'icon': icon, 'color': color}
            )
        self.stdout.write(f'  Categorías: {len(income_categories) + len(expense_categories)} creadas')

    def _tags(self):
        tags = [
            ('urgente', '#D4764A'),
            ('recurrente', '#6E8F4C'),
            ('importante', '#C4943A'),
            ('compartido', '#8BA864'),
            ('trabajo', '#7A3F23'),
            ('personal', '#A07858'),
            ('viaje', '#C4943A'),
            ('hogar', '#6E4E38'),
        ]
        for name, color in tags:
            Tag.objects.get_or_create(name=name, defaults={'color': color})
        self.stdout.write(f'  Tags: {len(tags)} creados')
