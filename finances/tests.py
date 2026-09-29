from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from finances.models import Category, Currency, Transaction
from finances.views.pages import _ant_expenses
from users.models import Colony


class AntExpensesTests(TestCase):
    def setUp(self):
        self.currency = Currency.objects.create(code='ARS', symbol='$', name='Peso')
        self.colony = Colony.objects.create(name='Test', is_guest=True, default_currency=self.currency,
                                            ant_expense_max_amount=Decimal('5000'),
                                            ant_expense_income_pct=Decimal('1.00'),
                                            ant_expense_min_count=3)
        self.cat_small = Category.objects.create(colony=self.colony, name='Kiosco', type='EXPENSE')
        self.cat_big = Category.objects.create(colony=self.colony, name='Alquiler', type='EXPENSE')
        self.today = date.today()

    def _tx(self, amount, category, type='EXPENSE'):
        return Transaction.objects.create(colony=self.colony, type=type, amount=Decimal(str(amount)),
                                          currency=self.currency, category=category, date=self.today)

    def test_hybrid_threshold_uses_income_cap(self):
        self._tx(100000, self.cat_big, type='INCOME')
        for _ in range(3):
            self._tx(500, self.cat_small)
        self._tx(3000, self.cat_big)

        result = _ant_expenses(self.colony, self.currency, self.today.year, self.today.month)

        self.assertEqual(result['threshold'], 1000.0)
        names = [c['name'] for c in result['categories']]
        self.assertIn('Kiosco', names)
        self.assertNotIn('Alquiler', names)

    def test_absolute_threshold_when_no_income(self):
        for _ in range(3):
            self._tx(4000, self.cat_small)

        result = _ant_expenses(self.colony, self.currency, self.today.year, self.today.month)

        self.assertEqual(result['threshold'], 5000.0)
        self.assertEqual(len(result['categories']), 1)
        self.assertEqual(result['categories'][0]['small_count'], 3)

    def test_min_count_not_reached(self):
        self._tx(100000, self.cat_big, type='INCOME')
        self._tx(500, self.cat_small)

        result = _ant_expenses(self.colony, self.currency, self.today.year, self.today.month)

        self.assertEqual(result['categories'], [])


class AnalyticsViewTests(TestCase):
    def test_page_renders(self):
        session = self.client.session
        session['welcome_seen'] = True
        session.save()

        resp = self.client.get('/analisis/')

        self.assertEqual(resp.status_code, 200)
        self.assertIn('projection', resp.context)


class TransactionNavigationTests(TestCase):
    def setUp(self):
        self.currency = Currency.objects.create(code='ARS', symbol='$', name='Peso')
        self.colony = Colony.objects.create(name='Test', is_guest=True, default_currency=self.currency)
        self.cat_income = Category.objects.create(colony=self.colony, name='Sueldo', type='INCOME')
        self.cat_expense = Category.objects.create(colony=self.colony, name='Comida', type='EXPENSE')
        session = self.client.session
        session['colony_id'] = self.colony.id
        session['welcome_seen'] = True
        session.save()

    def _post(self, type_value):
        cat = self.cat_income if type_value == 'INCOME' else self.cat_expense
        return self.client.post('/transactions/add/?type=' + type_value, {
            'type': type_value,
            'amount': '100',
            'currency': self.currency.pk,
            'category': cat.pk,
            'date': '2026-09-27',
            'note': '',
        })

    def test_add_income_redirects_to_income_list(self):
        resp = self._post('INCOME')
        self.assertRedirects(resp, reverse('finances:income_list'))

    def test_add_expense_redirects_to_expense_list(self):
        resp = self._post('EXPENSE')
        self.assertRedirects(resp, reverse('finances:expense_list'))

    def test_cancel_returns_to_origin_list(self):
        self.assertEqual(self.client.get('/transactions/add/?type=INCOME').context['return_url'],
                         'finances:income_list')
        self.assertEqual(self.client.get('/transactions/add/?type=EXPENSE').context['return_url'],
                         'finances:expense_list')
        self.assertEqual(self.client.get('/transactions/add/').context['return_url'],
                         'finances:transaction_list')


class AnalyticsCategoryDetailTests(TestCase):
    def setUp(self):
        self.currency = Currency.objects.create(code='ARS', symbol='$', name='Peso')
        self.colony = Colony.objects.create(name='Test', is_guest=True, default_currency=self.currency)
        cat = Category.objects.create(colony=self.colony, name='Salud', type='EXPENSE')
        Transaction.objects.create(colony=self.colony, type='EXPENSE', amount=Decimal('500'),
                                   currency=self.currency, category=cat, date=date.today(), note='Farmacia')
        session = self.client.session
        session['colony_id'] = self.colony.id
        session['welcome_seen'] = True
        session.save()

    def test_category_detail_carries_transactions(self):
        resp = self.client.get('/analisis/')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['by_category']), 1)
        cat = resp.context['by_category'][0]
        self.assertEqual(len(cat['transactions']), 1)
        self.assertEqual(cat['transactions'][0]['note'], 'Farmacia')
        self.assertNotIn('transactions', resp.context['by_category_json'][0])
