from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from finances.models import Transaction


def create_initial_payment(subscription):
    from .models import SubscriptionPayment
    today = timezone.now().date()

    payment, _ = SubscriptionPayment.objects.get_or_create(
        subscription=subscription,
        due_date=subscription.next_date,
        defaults={'is_paid': False}
    )

    if subscription.is_variable:
        return

    if subscription.auto_debit and subscription.next_date <= today and not payment.is_paid:
        _process_payment(payment, subscription)


def process_due_payment(payment):
    subscription = payment.subscription
    if subscription.is_variable:
        return False
    if not subscription.auto_debit:
        return False
    if payment.is_paid:
        return False
    _process_payment(payment, subscription)
    return True


def _process_payment(payment, subscription):
    if subscription.is_variable:
        return
    if not subscription.colony_id:
        return

    from trackant.utils import get_expense_category
    transaction = Transaction.objects.create(
        colony_id=subscription.colony_id,
        type='EXPENSE',
        amount=subscription.amount,
        currency=subscription.currency,
        category=get_expense_category(subscription.colony_id, subscription.category),
        date=payment.due_date,
        note=f'Suscripción: {subscription.name}',
    )

    payment.is_paid = True
    payment.paid_date = timezone.now().date()
    payment.transaction = transaction
    payment.save(update_fields=['is_paid', 'paid_date', 'transaction'])

    next_date = calculate_next_due_date(payment.due_date, subscription.cycle)
    subscription.next_date = next_date
    subscription.save(update_fields=['next_date'])

    from .models import SubscriptionPayment
    SubscriptionPayment.objects.get_or_create(
        subscription=subscription,
        due_date=next_date,
        defaults={'is_paid': False}
    )


def calculate_next_due_date(current_date, cycle):
    if cycle == 'WEEKLY':
        return current_date + timedelta(weeks=1)
    elif cycle == 'MONTHLY':
        return current_date + relativedelta(months=1)
    elif cycle == 'YEARLY':
        return current_date + relativedelta(years=1)
    return current_date


def mark_as_paid(payment, amount=None):
    from .models import SubscriptionPayment
    from trackant.utils import get_expense_category
    subscription = payment.subscription
    paid_amount = amount if amount is not None else subscription.amount

    transaction = Transaction.objects.create(
        colony=subscription.colony,
        type='EXPENSE',
        amount=paid_amount,
        currency=subscription.currency,
        category=get_expense_category(subscription.colony_id, subscription.category),
        date=payment.due_date,
        note=f'Suscripción: {subscription.name}',
    )

    payment.is_paid = True
    payment.paid_date = timezone.now().date()
    payment.transaction = transaction
    payment.save()

    next_date = calculate_next_due_date(payment.due_date, subscription.cycle)
    subscription.next_date = next_date
    subscription.save()

    next_payment, created = SubscriptionPayment.objects.get_or_create(
        subscription=subscription,
        due_date=next_date,
        defaults={'is_paid': False}
    )

    return transaction


def mark_as_unpaid(payment):
    from .models import SubscriptionPayment

    if payment.transaction:
        payment.transaction.delete()
        payment.transaction = None

    payment.is_paid = False
    payment.paid_date = None
    payment.save()

    subscription = payment.subscription

    next_payments = SubscriptionPayment.objects.filter(
        subscription=subscription,
        due_date__gt=payment.due_date,
        is_paid=False
    )
    next_payments.delete()

    subscription.next_date = payment.due_date
    subscription.save()
