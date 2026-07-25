from decimal import Decimal
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q, F
from django.utils import timezone
from datetime import date, timedelta
import json
from ..models import Transaction, Category, Currency, Tag
from goals.models import Goal
from subscriptions.models import SubscriptionPayment
from debts.models import Debt
from budgets.models import Budget
from ..forms import TransactionForm

logger = logging.getLogger(__name__)


def _colony_objects(model, colony):
    return model.objects.filter(Q(colony=colony) | Q(colony__isnull=True))


def _month_filter(qs, year=None, month=None):
    today = date.today()
    y = year or today.year
    m = month or today.month
    return qs.filter(date__year=y, date__month=m)


def _update_goal_progress(goal_id, amount, colony):
    if not goal_id:
        return
    try:
        goal = Goal.objects.get(pk=goal_id, colony=colony)
        new_amount = goal.current_amount + Decimal(str(amount))
        if new_amount >= goal.target_amount:
            Goal.objects.filter(pk=goal.pk).update(current_amount=F('current_amount') + Decimal(str(amount)), is_achieved=True)
        else:
            Goal.objects.filter(pk=goal.pk).update(current_amount=F('current_amount') + Decimal(str(amount)))
    except Goal.DoesNotExist:
        logger.warning('Goal %s not found for colony %s', goal_id, colony.id)
    except ValueError:
        logger.warning('Invalid amount %s for goal %s', amount, goal_id)


def _monthly_summary(colony):
    today = date.today()

    balance_rows = (
        Transaction.objects.filter(colony=colony)
        .values('currency__code', 'currency__symbol')
        .annotate(
            total_income=Sum('amount', filter=Q(type='INCOME')),
            total_expenses=Sum('amount', filter=Q(type='EXPENSE')),
        )
        .order_by('currency__code')
    )
    balance_by_currency = []
    for row in balance_rows:
        income = float(row['total_income'] or 0)
        expense = float(row['total_expenses'] or 0)
        balance_by_currency.append({
            'code': row['currency__code'],
            'symbol': row['currency__symbol'],
            'income': income,
            'expenses': expense,
            'balance': income - expense,
        })

    month_rows = (
        Transaction.objects.filter(colony=colony, date__year=today.year, date__month=today.month)
        .values('currency__code', 'currency__symbol')
        .annotate(
            income=Sum('amount', filter=Q(type='INCOME')),
            expenses=Sum('amount', filter=Q(type='EXPENSE')),
        )
        .order_by('currency__code')
    )
    kpis_by_currency = []
    for row in month_rows:
        kpis_by_currency.append({
            'code': row['currency__code'],
            'symbol': row['currency__symbol'],
            'income': float(row['income'] or 0),
            'expenses': float(row['expenses'] or 0),
        })

    return {
        'balance_by_currency': balance_by_currency,
        'kpis_by_currency': kpis_by_currency,
    }


def dashboard(request):
    colony = request.colony
    ctx = _monthly_summary(colony)
    ctx['balance_json'] = ctx['balance_by_currency']
    ctx['kpis_json'] = ctx['kpis_by_currency']
    ctx['recent_transactions'] = Transaction.objects.filter(colony=colony).select_related('category', 'currency')[:10]
    ctx['goals_count'] = Goal.objects.filter(colony=colony, is_achieved=False).count()
    ctx['active_goals_list'] = list(Goal.objects.filter(colony=colony, is_achieved=False).only('id', 'name'))

    today = date.today()
    pending_subs = SubscriptionPayment.objects.filter(
        subscription__colony=colony,
        subscription__is_active=True,
        is_paid=False,
        due_date__lte=today,
    ).select_related('subscription__currency', 'subscription__category').order_by('due_date')[:5]
    ctx['pending_subscriptions'] = pending_subs

    budget_alerts = Budget.objects.filter(
        colony=colony,
        month=today.month,
        year=today.year,
    ).select_related('category', 'currency').with_spent()
    threshold = colony.budget_alert_threshold
    budget_alerts = [b for b in budget_alerts if b.pct() >= threshold]
    ctx['budget_alerts'] = budget_alerts[:5]

    deadline_threshold = date.today() + timedelta(days=colony.debt_show_days)
    pending_debts = Debt.objects.filter(
        colony=colony,
        is_settled=False,
        debt_type='OWE',
        deadline__lte=deadline_threshold,
    ).select_related('currency').order_by('deadline')[:5]
    ctx['pending_debts'] = pending_debts

    category_by_currency = {}
    month_expenses = Transaction.objects.filter(
        colony=colony,
        type='EXPENSE',
        date__year=today.year,
        date__month=today.month,
    ).values('currency__code', 'category__name', 'category__color').annotate(total=Sum('amount'))

    for e in month_expenses:
        code = e['currency__code']
        if code not in category_by_currency:
            category_by_currency[code] = {'labels': [], 'values': [], 'colors': []}
        category_by_currency[code]['labels'].append(e['category__name'])
        category_by_currency[code]['values'].append(float(e['total']))
        category_by_currency[code]['colors'].append(e['category__color'])

    monthly_by_currency = {}
    all_year_data = (
        Transaction.objects.filter(colony=colony, date__year=today.year)
        .values('currency__code', 'date__month', 'type')
        .annotate(total=Sum('amount'))
    )
    for row in all_year_data:
        code = row['currency__code']
        m = row['date__month']
        if code not in monthly_by_currency:
            monthly_by_currency[code] = {'incomes': [0.0] * 12, 'expenses': [0.0] * 12}
        if row['type'] == 'INCOME':
            monthly_by_currency[code]['incomes'][m - 1] = float(row['total'])
        else:
            monthly_by_currency[code]['expenses'][m - 1] = float(row['total'])

    ctx['category_by_currency_json'] = category_by_currency
    ctx['monthly_by_currency_json'] = monthly_by_currency

    return render(request, 'finances/dashboard.html', ctx)


def _transaction_list(request, type_filter=None):
    colony = request.colony
    qs = Transaction.objects.filter(colony=colony).select_related('category', 'currency').prefetch_related('tags')
    if type_filter:
        qs = qs.filter(type=type_filter)

    search = request.GET.get('q', '')
    if search:
        qs = qs.filter(Q(note__icontains=search) | Q(category__name__icontains=search))

    month = request.GET.get('month', '')
    if month:
        try:
            y, m = month.split('-')
            qs = qs.filter(date__year=int(y), date__month=int(m))
        except (ValueError, AttributeError):
            pass

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'finances/transaction_list.html', {
        'transactions': page,
        'page': page,
        'search': search,
        'month': month or date.today().strftime('%Y-%m'),
        'list_type': type_filter or 'all',
    })


def transaction_list(request):
    return _transaction_list(request)


def income_list(request):
    return _transaction_list(request, type_filter='INCOME')


def expense_list(request):
    return _transaction_list(request, type_filter='EXPENSE')


def transaction_add(request):
    colony = request.colony
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, colony=colony)
        if form.is_valid():
            t = form.save(commit=False)
            t.colony = colony
            t.save()
            form.save_m2m()
            goal_id = form.cleaned_data.get('goal')
            if goal_id:
                _update_goal_progress(goal_id, t.amount, colony)
            messages.success(request, f'Transaccion registrada: {t}')
            if request.htmx:
                return render(request, 'components/toast.html', {'message': 'Transaccion guardada'}, status=201)
            return redirect('finances:transaction_list')
    else:
        initial = {'date': date.today(), 'type': request.GET.get('type', 'EXPENSE')}
        form = TransactionForm(initial=initial, colony=colony)

    return render(request, 'finances/transaction_form.html', {'form': form, 'tag_ids': '[]', 'custom_tags': '[]'})


def transaction_quick_add(request):
    colony = request.colony
    if request.method == 'POST':
        post_data = request.POST.copy()
        if not post_data.get('currency'):
            default_currency = Currency.objects.filter(
                Q(colony=colony) | Q(colony__isnull=True)
            ).first()
            if default_currency:
                post_data['currency'] = default_currency.pk
        form = TransactionForm(post_data, colony=colony)
        if form.is_valid():
            t = form.save(commit=False)
            t.colony = colony
            t.save()
            goal_id = form.cleaned_data.get('goal')
            if goal_id:
                _update_goal_progress(goal_id, t.amount, colony)
            messages.success(request, f'Transaccion registrada: {t}')
            if request.htmx:
                return render(request, 'components/toast.html', {'message': 'Transaccion guardada'}, status=201)
            return redirect('finances:transaction_list')
        if request.htmx:
            return render(request, 'components/toast.html', {'message': 'Error en el formulario'}, status=400)
    return redirect('finances:transaction_add')


def transaction_edit(request, pk):
    colony = request.colony
    t = get_object_or_404(Transaction, pk=pk, colony=colony)
    if request.method == 'POST':
        old_goal = t.goal
        form = TransactionForm(request.POST, request.FILES, instance=t, colony=colony)
        if form.is_valid():
            t = form.save()
            new_goal = form.cleaned_data.get('goal')
            if new_goal and new_goal != old_goal:
                _update_goal_progress(new_goal, t.amount, colony)
            messages.success(request, 'Transaccion actualizada')
            return redirect('finances:transaction_list')
    else:
        form = TransactionForm(instance=t, colony=colony)

    cat = t.category
    ctx = {
        'form': form,
        'transaction': t,
        'initial_category_id': cat.pk if cat else '',
        'initial_category_name': cat.name if cat else 'Seleccionar categoría',
        'initial_category_icon': cat.icon if cat else '',
    }
    return render(request, 'finances/transaction_form.html', ctx)


def transaction_delete(request, pk):
    colony = request.colony
    t = get_object_or_404(Transaction, pk=pk, colony=colony)
    if request.method == 'POST':
        t.delete()
        messages.success(request, 'Transaccion eliminada')
        if request.htmx:
            return render(request, 'components/toast.html', {'message': 'Transaccion eliminada'})
        return redirect('finances:transaction_list')
    return render(request, 'finances/transaction_confirm_delete.html', {'transaction': t})


def transaction_category_options(request):
    colony = request.colony
    type_val = request.GET.get('type', 'EXPENSE')
    selected = request.GET.get('selected', '')
    qs = Category.objects.filter(Q(colony=colony) | Q(colony__isnull=True), type=type_val)
    return render(request, 'finances/partials/category_options.html', {
        'categories': qs,
        'selected': int(selected) if selected.isdigit() else '',
    })


def tag_search(request):
    colony = request.colony
    q = request.GET.get('q', '')
    tags = Tag.objects.filter(Q(colony=colony) | Q(colony__isnull=True), name__icontains=q)[:10] if q else Tag.objects.none()
    return render(request, 'finances/partials/tag_results.html', {'tags': tags, 'query': q})


def category_list(request):
    colony = request.colony
    categories = _colony_objects(Category, colony)
    return render(request, 'finances/category_list.html', {'categories': categories})
