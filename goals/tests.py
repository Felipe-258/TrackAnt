from django.test import TestCase, Client
from django.urls import reverse

from users.models import Colony, CustomUser
from finances.models import Currency
from goals.models import Reserve


class ReserveTests(TestCase):
    def setUp(self):
        self.colony = Colony.objects.create(name='Test')
        self.currency = Currency.objects.create(code='ARS', symbol='$', name='Peso')
        self.client = Client()
        session = self.client.session
        session['colony_id'] = self.colony.id
        session['welcome_seen'] = True
        session.save()

    def test_create_without_target(self):
        r = Reserve.objects.create(
            colony=self.colony, name='Fondo', currency=self.currency,
            target_amount=None, current_amount=0,
        )
        self.assertFalse(r.has_target)
        self.assertIsNone(r.progress_pct())
        self.assertIsNone(r.remaining())

    def test_deposit_updates_balance(self):
        r = Reserve.objects.create(
            colony=self.colony, name='Fondo', currency=self.currency,
            target_amount=None, current_amount=0,
        )
        self.client.post(reverse('reserves:deposit', args=[r.pk]), {'amount': '100'})
        r.refresh_from_db()
        self.assertEqual(r.current_amount, 100)

    def test_withdraw_limited_by_balance(self):
        r = Reserve.objects.create(
            colony=self.colony, name='Fondo', currency=self.currency,
            target_amount=None, current_amount=50,
        )
        self.client.post(reverse('reserves:withdraw', args=[r.pk]), {'amount': '200'})
        r.refresh_from_db()
        self.assertEqual(r.current_amount, 50)

    def test_achieved_when_target_met(self):
        r = Reserve.objects.create(
            colony=self.colony, name='Obj', currency=self.currency,
            target_amount=100, current_amount=0,
        )
        self.client.post(reverse('reserves:deposit', args=[r.pk]), {'amount': '100'})
        r.refresh_from_db()
        self.assertTrue(r.is_achieved)
        self.assertEqual(r.progress_pct(), 100)

    def test_deposit_partial_with_target(self):
        r = Reserve.objects.create(
            colony=self.colony, name='Obj', currency=self.currency,
            target_amount=1000, current_amount=0,
        )
        self.client.post(reverse('reserves:deposit', args=[r.pk]), {'amount': '250'})
        r.refresh_from_db()
        self.assertEqual(r.current_amount, 250)
        self.assertFalse(r.is_achieved)
        self.assertEqual(r.progress_pct(), 25)

    def test_reserve_excluded_from_available(self):
        from finances.exchange import available_balances
        Reserve.objects.create(
            colony=self.colony, name='Fondo', currency=self.currency,
            target_amount=None, current_amount=250,
        )
        bal = available_balances(self.colony)
        self.assertEqual(bal['ARS'], -250)
