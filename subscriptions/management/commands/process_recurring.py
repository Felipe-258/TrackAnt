from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Procesa vencimientos de suscripciones y cuotas'

    def handle(self, *args, **options):
        today = timezone.now().date()
        created = 0

        created += self._process_subscriptions(today)
        created += self._process_installments(today)

        self.stdout.write(self.style.SUCCESS(f'Transacciones creadas: {created}'))

    def _process_subscriptions(self, today):
        from subscriptions.models import Subscription, SubscriptionPayment
        count = 0

        subscriptions = Subscription.objects.filter(
            is_active=True,
            auto_debit=True,
            is_variable=False,
            next_date__lte=today,
        ).select_related('currency', 'category')

        for sub in subscriptions:
            payment = SubscriptionPayment.objects.filter(
                subscription=sub,
                is_paid=False,
                due_date=today,
            ).first()

            if payment:
                from subscriptions.services import process_due_payment
                if process_due_payment(payment):
                    count += 1

        return count

    def _process_installments(self, today):
        from installments.models import Installment
        from finances.models import Transaction
        count = 0

        installments = Installment.objects.filter(
            is_paid=False,
            purchase__auto_debit=True,
            due_date__lte=today,
            purchase__is_completed=False,
        ).select_related('purchase', 'purchase__currency', 'purchase__category')

        for inst in installments:
            from trackant.utils import get_expense_category
            tx = Transaction.objects.create(
                colony=inst.purchase.colony,
                type='EXPENSE',
                amount=inst.amount,
                currency=inst.purchase.currency,
                category=get_expense_category(inst.purchase.colony_id, inst.purchase.category),
                date=today,
                note=f'Cuota {inst.number}/{inst.purchase.installments_count} - {inst.purchase.name}',
            )
            inst.is_paid = True
            inst.paid_date = today
            inst.transaction = tx
            inst.save()

            from installments.views.pages import _check_completed
            _check_completed(inst.purchase)

            count += 1

        return count
