from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from datetime import date

from users.models import Colony
from finances.models import Currency
from splits.models import SplitGroup, SplitExpense, SplitPayment


class SplitDebtsTests(TestCase):
    def setUp(self):
        self.colony = Colony.objects.create(name='Test')
        self.ars = Currency.objects.create(code='ARS', symbol='$', name='Peso')
        self.usd = Currency.objects.create(code='USD', symbol='U$S', name='Dolar')
        self.client = Client()
        session = self.client.session
        session['colony_id'] = self.colony.id
        session['welcome_seen'] = True
        session.save()

    def _group(self, members=('Ana', 'Juan', 'Pedro')):
        return SplitGroup.objects.create(colony=self.colony, name='Viaje', members=list(members))

    def _expense(self, group, desc, amount, paid_by, currency=None):
        n = len(group.members)
        share = float((Decimal(amount) / n).quantize(Decimal('0.01')))
        return SplitExpense.objects.create(
            group=group, description=desc, amount=amount,
            currency=currency or self.ars, paid_by=paid_by, date=date.today(),
            shares={m: share for m in group.members},
        )

    def test_balance_by_currency_no_mix(self):
        g = self._group()
        self._expense(g, 'cena', '100', 'Ana')          # ARS
        self._expense(g, 'hotel', '30', 'Juan', self.usd)  # USD
        bal = g.balance_by_currency()
        # cena 100 entre 3: Ana +100 -33.33 (su parte) = 66.67
        self.assertEqual(bal['ARS']['Ana'], Decimal('66.67'))
        self.assertEqual(bal['ARS']['Juan'], Decimal('-33.33'))
        # hotel USD 30 entre 3 pagado por Juan: +30 -10 (su parte) = 20
        self.assertEqual(bal['USD']['Juan'], Decimal('20.00'))
        self.assertEqual(bal['USD']['Ana'], Decimal('-10.00'))

    def test_settle_debts_greedy(self):
        g = self._group()
        self._expense(g, 'cena', '300', 'Ana')
        debts = g.settle_debts()
        ars = [d for d in debts if d['currency_code'] == 'ARS']
        total = sum(d['amount'] for d in ars)
        self.assertEqual(total, Decimal('200.00'))  # Juan + Pedro pagan 100 c/u
        payers = {d['payer'] for d in ars}
        self.assertEqual(payers, {'Juan', 'Pedro'})
        for d in ars:
            self.assertEqual(d['payee'], 'Ana')

    def test_preference_realizable(self):
        g = self._group()
        self._expense(g, 'cena', '300', 'Ana')  # Juan y Pedro deben, Ana acreedora
        # Pedro prefiere pagarle a Juan? Juan es deudor, no acreedor -> no realizable.
        # Caso realizable: Pedro debe 100, Ana acreedora 200 -> Pedro prefiere Ana ya es default.
        # Preferencia distinta: agregar gasto pagado por Pedro para que Ana deba a Pedro.
        g.payment_preferences = {'Juan': 'Pedro'}
        g.save(update_fields=['payment_preferences'])
        # si Pedro es acreedor neto...
        g2 = self._group()
        self._expense(g2, 'a', '200', 'Ana')
        self._expense(g2, 'b', '400', 'Pedro')
        # neto: Ana +200 -133.33 = +66.67? recalcular: 2 gastos /3 personas
        g2.payment_preferences = {'Juan': 'Pedro'}
        g2.save(update_fields=['payment_preferences'])
        debts = g2.settle_debts()
        juan_debts = [d for d in debts if d['payer'] == 'Juan']
        # si Pedro acreedor, Juan le paga a Pedro primero
        self.assertTrue(any(d['payee'] == 'Pedro' for d in juan_debts))

    def test_preference_not_realizable_falls_back(self):
        g = self._group()
        self._expense(g, 'cena', '300', 'Ana')
        # Pedro tambien debe (nadie le debe a el) -> preferencia Juan->Pedro no realizable
        g.payment_preferences = {'Juan': 'Pedro'}
        g.save(update_fields=['payment_preferences'])
        debts = g.settle_debts()
        ars = [d for d in debts if d['currency_code'] == 'ARS']
        self.assertTrue(ars)
        # nadie paga a Pedro (no es acreedor)
        self.assertFalse(any(d['payee'] == 'Pedro' for d in ars))

    def test_payment_reduces_debt(self):
        g = self._group()
        self._expense(g, 'cena', '300', 'Ana')
        # Juan paga 100 a Ana
        SplitPayment.objects.create(group=g, payer='Juan', payee='Ana', amount='100', currency=self.ars, date=date.today())
        debts = g.settle_debts()
        juan = [d for d in debts if d['payer'] == 'Juan']
        juan_total = sum(d['amount'] for d in juan)
        self.assertEqual(juan_total, Decimal('0.00'))  # ya no debe
        # Pedro sigue debiendo 100
        pedro = sum(d['amount'] for d in debts if d['payer'] == 'Pedro')
        self.assertEqual(pedro, Decimal('100.00'))

    def test_payment_add_and_delete_via_http(self):
        g = self._group()
        self._expense(g, 'cena', '300', 'Ana')
        resp = self.client.post(reverse('splits:split_payment_add', args=[g.pk]), {
            'payer': 'Juan', 'payee': 'Ana', 'amount': '100', 'currency': 'ARS',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(SplitPayment.objects.filter(group=g).exists())
        p = SplitPayment.objects.get(group=g)
        # delete
        self.client.post(reverse('splits:split_payment_delete', args=[p.pk]))
        self.assertFalse(SplitPayment.objects.filter(group=g).exists())

    def test_preference_add_remove_via_http(self):
        g = self._group()
        resp = self.client.post(reverse('splits:split_preference_add', args=[g.pk]), {
            'payer': 'Juan', 'payee': 'Pedro',
        })
        self.assertEqual(resp.status_code, 302)
        g.refresh_from_db()
        self.assertEqual(g.payment_preferences, {'Juan': 'Pedro'})
        self.client.post(reverse('splits:split_preference_remove', args=[g.pk]), {'payer': 'Juan'})
        g.refresh_from_db()
        self.assertEqual(g.payment_preferences, {})

    def test_detail_renders(self):
        g = self._group()
        self._expense(g, 'cena', '300', 'Ana')
        resp = self.client.get(reverse('splits:split_group_detail', args=[g.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Deudas pendientes')
        self.assertContains(resp, 'le debe')
