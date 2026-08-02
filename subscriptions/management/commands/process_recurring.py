from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q


class Command(BaseCommand):
    help = 'Procesa vencimientos de suscripciones, cuotas y gastos recurrentes'

    def handle(self, *args, **options):
        today = timezone.now().date()
        created = 0

        created += self._process_subscriptions(today)
        created += self._process_installments(today)
        created += self._process_recurring(today)

        self.stdout.write(self.style.SUCCESS(f'Transacciones creadas: {created}'))

    def _process_subscriptions(self, today):
        from subscriptions.models import Subscription, SubscriptionPayment
        count = 0

        subscriptions = Subscription.objects.filter(
            is_active=True,
            auto_debit=True,
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
                is_recurring=True,
            )
            inst.is_paid = True
            inst.paid_date = today
            inst.transaction = tx
            inst.save()

            from installments.views.pages import _check_completed
            _check_completed(inst.purchase)

            count += 1

        return count

    def _process_recurring(self, today):
        from recurring.models import RecurringTransaction
        from finances.models import Transaction
        count = 0

        rts = RecurringTransaction.objects.filter(
            is_active=True,
            next_date__lte=today,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        ).select_related('currency', 'category')

        for rt in rts:
            tx = Transaction.objects.create(
                colony=rt.colony,
                type='EXPENSE',
                amount=rt.amount,
                currency=rt.currency,
                category=rt.category,
                date=today,
                note=rt.note or rt.name,
                is_recurring=True,
            )

            rt.next_date = self._calc_next(rt)
            rt.save(update_fields=['next_date'])
            count += 1

        return count

    def _calc_next(self, rt):
        from trackant.utils import cap_day
        d = rt.next_date
        if rt.cycle == 'WEEKLY':
            return d + timedelta(weeks=1)
        elif rt.cycle == 'BIWEEKLY':
            return d + timedelta(weeks=2)
        elif rt.cycle == 'MONTHLY':
            next_d = d + relativedelta(months=1)
            if rt.day_of_month:
                next_d = next_d.replace(day=cap_day(next_d.year, next_d.month, rt.day_of_month))
            return next_d
        elif rt.cycle == 'BIMONTHLY':
            next_d = d + relativedelta(months=2)
            if rt.day_of_month:
                next_d = next_d.replace(day=cap_day(next_d.year, next_d.month, rt.day_of_month))
            return next_d
        elif rt.cycle == 'YEARLY':
            return d + relativedelta(years=1)
        return d
