from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta

from users.models import Colony
from finances.models import Currency, Category, Transaction
from subscriptions.models import Subscription, SubscriptionPayment
from subscriptions.services import create_initial_payment, mark_as_paid


class VariableSubscriptionTests(TestCase):
    def setUp(self):
        self.colony = Colony.objects.create(name='Test')
        self.currency = Currency.objects.create(code='ARS', symbol='$', name='Peso')
        self.cat = Category.objects.create(colony=None, name='Servicios', type='EXPENSE')
        Transaction.objects.create(
            colony=self.colony, type='INCOME', amount=10000,
            currency=self.currency, category=self.cat, date=date.today(),
        )
        self.client = Client()
        session = self.client.session
        session['colony_id'] = self.colony.id
        session['welcome_seen'] = True
        session.save()

    def _sub(self, **kw):
        defaults = dict(
            colony=self.colony, name='Luz', amount=100, currency=self.currency,
            cycle='MONTHLY', next_date=date.today() + timedelta(days=5),
            is_active=True, is_variable=True, auto_debit=True,
        )
        defaults.update(kw)
        s = Subscription.objects.create(**defaults)
        return s

    def _payment(self, sub):
        return SubscriptionPayment.objects.create(
            subscription=sub, due_date=sub.next_date, is_paid=False
        )

    def test_variable_never_auto_debits(self):
        sub = self._sub(next_date=date.today() - timedelta(days=1))
        create_initial_payment(sub)
        payments = SubscriptionPayment.objects.filter(subscription=sub)
        self.assertTrue(payments.exists())
        self.assertTrue(all(not p.is_paid for p in payments))

    def test_mark_as_paid_uses_real_amount(self):
        sub = self._sub()
        payment = self._payment(sub)
        tx = mark_as_paid(payment, amount=3250)
        tx.refresh_from_db()
        self.assertEqual(tx.amount, 3250)
        payment.refresh_from_db()
        self.assertTrue(payment.is_paid)
        self.assertEqual(payment.transaction, tx)

    def test_toggle_variable_requires_amount(self):
        sub = self._sub()
        payment = self._payment(sub)
        resp = self.client.post(reverse('subscriptions:payment_toggle', args=[payment.pk]), {})
        self.assertRedirects(resp, reverse('subscriptions:subscription_list'))
        payment.refresh_from_db()
        self.assertFalse(payment.is_paid)
        tx = Transaction.objects.filter(colony=self.colony, type='EXPENSE').count()
        self.assertEqual(tx, 0)

    def test_toggle_variable_with_amount(self):
        sub = self._sub()
        payment = self._payment(sub)
        resp = self.client.post(reverse('subscriptions:payment_toggle', args=[payment.pk]), {'amount': '420.50'})
        self.assertRedirects(resp, reverse('subscriptions:subscription_list'))
        payment.refresh_from_db()
        self.assertTrue(payment.is_paid)
        self.assertEqual(payment.transaction.amount, 420.50)

    def test_form_forces_auto_debit_off(self):
        resp = self.client.post(reverse('subscriptions:subscription_add'), {
            'name': 'Agua', 'amount': '150', 'currency': self.currency.pk,
            'cycle': 'MONTHLY', 'next_date': '2026-09-01',
            'auto_debit': 'on', 'is_variable': 'on', 'is_active': 'on',
        })
        sub = Subscription.objects.get(name='Agua')
        self.assertTrue(sub.is_variable)
        self.assertFalse(sub.auto_debit)
