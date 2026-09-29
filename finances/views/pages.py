from decimal import Decimal, InvalidOperation
import calendar
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q, F, Count, ProtectedError
from django.utils import timezone
from django.conf import settings
from datetime import date, timedelta
import json
from ..models import Transaction, Category, Currency
from goals.models import Reserve
from subscriptions.models import Subscription, SubscriptionPayment
from debts.models import Debt
from budgets.models import Budget
from installments.models import Installment
from ..forms import TransactionForm, CategoryForm

logger = logging.getLogger(__name__)

CATEGORY_ICONS = ['wallet','banknote','credit-card','coins','shopping-cart','shopping-bag','pizza','coffee','utensils','salad','bus','car','train','home','building','lightbulb','heart-pulse','graduation-cap','film','music','gamepad-2','shirt','laptop','smartphone','paw-print','plane','dumbbell','gift','briefcase','trending-up','piggy-bank','scale','receipt-text','stethoscope','wrench','sparkles','star','package','wifi','heart','calculator','cloud']
CATEGORY_COLORS = ['#6E4E38','#A07858','#C4943A','#D4A857','#8BA864','#6E8F4C','#D4764A','#C16645','#7A3F23','#8A6348','#485D35','#5A753F']
MONTHS_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


def _colony_objects(model, colony):
    return model.objects.filter(Q(colony=colony) | Q(colony__isnull=True))


def _month_filter(qs, year=None, month=None):
    today = timezone.now().date()
    y = year or today.year
    m = month or today.month
    return qs.filter(date__year=y, date__month=m)


def _update_reserve_progress(reserve_id, amount, colony):
    if not reserve_id:
        return
    try:
        reserve = Reserve.objects.get(pk=reserve_id, colony=colony)
        if not reserve.has_target:
            Reserve.objects.filter(pk=reserve.pk).update(current_amount=F('current_amount') + Decimal(str(amount)))
            return
        new_amount = reserve.current_amount + Decimal(str(amount))
        if new_amount >= reserve.target_amount:
            Reserve.objects.filter(pk=reserve.pk).update(current_amount=F('current_amount') + Decimal(str(amount)), is_achieved=True)
        else:
            Reserve.objects.filter(pk=reserve.pk).update(current_amount=F('current_amount') + Decimal(str(amount)))
    except Reserve.DoesNotExist:
        logger.warning('Reserve %s not found for colony %s', reserve_id, colony.id)
    except ValueError:
        logger.warning('Invalid amount %s for reserve %s', amount, reserve_id)


def _monthly_summary(colony):
    today = timezone.now().date()

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

    reserve_rows = (
        Reserve.objects.filter(colony=colony)
        .values('currency__code', 'currency__symbol')
        .annotate(total=Sum('current_amount'))
    )
    reserve_by_currency = {r['currency__code']: float(r['total'] or 0) for r in reserve_rows}
    reserve_symbol = {r['currency__code']: r['currency__symbol'] for r in reserve_rows}
    existing_codes = {b['code'] for b in balance_by_currency}
    for b in balance_by_currency:
        b['balance'] = b['balance'] - reserve_by_currency.get(b['code'], 0.0)
    for code, reserved in reserve_by_currency.items():
        if code not in existing_codes:
            balance_by_currency.append({
                'code': code,
                'symbol': reserve_symbol.get(code, ''),
                'income': 0,
                'expenses': 0,
                'balance': -reserved,
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


def _delta(current, previous):
    if not previous:
        return None
    return (current - previous) / abs(previous) * 100


def _list_for_type(type_value):
    if type_value == 'INCOME':
        return 'finances:income_list'
    if type_value == 'EXPENSE':
        return 'finances:expense_list'
    return 'finances:transaction_list'


def _ant_expenses(colony, currency, year, month):
    """Detecta gastos hormiga por categoría en un mes/moneda.

    Umbral efectivo = min(tope absoluto, % del ingreso mensual).
    # ponytail: umbral por moneda seleccionada, sin convertir; usar rate_to_base si hace falta multi-moneda real.
    """
    if currency is None:
        return {'threshold': 0.0, 'threshold_absolute': 0.0, 'income': 0.0,
                'categories': [], 'ant_total': 0.0, 'ant_pct_expenses': 0.0, 'ant_pct_income': 0.0}

    income = Transaction.objects.filter(
        colony=colony, type='INCOME', currency=currency, date__year=year, date__month=month
    ).aggregate(s=Sum('amount'))['s'] or Decimal('0')

    max_amount = colony.ant_expense_max_amount or Decimal('0')
    if income > 0:
        cap = (income * colony.ant_expense_income_pct / Decimal('100')).quantize(Decimal('0.01'))
        threshold = min(max_amount, cap)
    else:
        threshold = max_amount

    rows = (
        Transaction.objects.filter(
            colony=colony, type='EXPENSE', currency=currency, date__year=year, date__month=month
        ).values('category__name', 'category__icon', 'category__color')
        .annotate(
            total=Sum('amount'),
            count=Count('id'),
            small_count=Count('id', filter=Q(amount__lte=threshold)),
            small_total=Sum('amount', filter=Q(amount__lte=threshold)),
        )
        .order_by('-small_total')
    )

    total_expenses = sum((r['total'] or Decimal('0')) for r in rows)
    categories = []
    for r in rows:
        if r['small_count'] and r['small_count'] >= colony.ant_expense_min_count:
            small_total = r['small_total'] or Decimal('0')
            categories.append({
                'name': r['category__name'],
                'icon': r['category__icon'],
                'color': r['category__color'],
                'total': float(r['total'] or 0),
                'count': r['count'],
                'small_count': r['small_count'],
                'small_total': float(small_total),
                'pct_expenses': float(small_total / total_expenses * 100) if total_expenses else 0.0,
                'pct_income': float(small_total / income * 100) if income else 0.0,
            })

    ant_total = sum(c['small_total'] for c in categories)
    return {
        'threshold': float(threshold),
        'threshold_absolute': float(max_amount),
        'income': float(income),
        'categories': categories,
        'ant_total': ant_total,
        'ant_pct_expenses': (ant_total / float(total_expenses) * 100) if total_expenses else 0.0,
        'ant_pct_income': (ant_total / float(income) * 100) if income else 0.0,
    }


def analytics(request):
    colony = request.colony
    today = timezone.now().date()

    month_param = request.GET.get('mes', '')
    try:
        y, m = month_param.split('-')
        year, month = int(y), int(m)
        if not 1 <= month <= 12:
            raise ValueError
    except (ValueError, AttributeError):
        year, month = today.year, today.month

    if month > 1:
        prev_year, prev_month = year, month - 1
    else:
        prev_year, prev_month = year - 1, 12

    currencies = list(Currency.objects.filter(Q(colony=colony) | Q(colony__isnull=True)).order_by('code'))
    codes = [c.code for c in currencies]
    selected = request.GET.get('currency', '')
    if selected not in codes:
        default_code = colony.default_currency.code if colony.default_currency else None
        selected = default_code if default_code in codes else (codes[0] if codes else '')
    currency = next((c for c in currencies if c.code == selected), None)
    symbol = currency.symbol if currency else '$'

    def month_totals(y, m):
        row = Transaction.objects.filter(
            colony=colony, currency=currency, date__year=y, date__month=m
        ).aggregate(
            income=Sum('amount', filter=Q(type='INCOME')),
            expenses=Sum('amount', filter=Q(type='EXPENSE')),
        )
        income = float(row['income'] or 0)
        expenses = float(row['expenses'] or 0)
        return income, expenses, income - expenses

    income, expenses, balance = month_totals(year, month)
    p_income, p_expenses, p_balance = month_totals(prev_year, prev_month)
    kpis = {
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'income_delta': _delta(income, p_income),
        'expenses_delta': _delta(expenses, p_expenses),
        'balance_delta': _delta(balance, p_balance),
    }

    prev_rows = {
        r['category__name']: float(r['total'] or 0)
        for r in Transaction.objects.filter(
            colony=colony, currency=currency, type='EXPENSE', date__year=prev_year, date__month=prev_month
        ).values('category__name').annotate(total=Sum('amount'))
    }
    by_category = []
    for r in (
        Transaction.objects.filter(
            colony=colony, currency=currency, type='EXPENSE', date__year=year, date__month=month
        ).values('category__id', 'category__name', 'category__icon', 'category__color')
        .annotate(total=Sum('amount')).order_by('-total')
    ):
        total = float(r['total'] or 0)
        prev_total = prev_rows.get(r['category__name'], 0.0)
        by_category.append({
            'category_id': r['category__id'],
            'name': r['category__name'],
            'icon': r['category__icon'],
            'color': r['category__color'],
            'total': total,
            'pct': (total / expenses * 100) if expenses else 0.0,
            'prev_total': prev_total,
            'delta': _delta(total, prev_total),
        })

    # ponytail: carga eager de las tx del mes; endpoint HTMX si un mes trae demasiadas.
    tx_by_category = {}
    for tx in (
        Transaction.objects.filter(
            colony=colony, currency=currency, type='EXPENSE', date__year=year, date__month=month
        ).select_related('category').order_by('-date', '-id')
    ):
        tx_by_category.setdefault(tx.category_id, []).append({
            'date': tx.date,
            'note': tx.note,
            'amount': float(tx.amount),
        })
    for c in by_category:
        c['transactions'] = tx_by_category.get(c['category_id'], [])

    months = []
    ty, tm = year, month
    for _ in range(12):
        months.append((ty, tm))
        tm -= 1
        if tm == 0:
            tm = 12
            ty -= 1
    months.reverse()
    trend = []
    for ty, tm in months:
        row = Transaction.objects.filter(
            colony=colony, currency=currency, date__year=ty, date__month=tm
        ).aggregate(
            income=Sum('amount', filter=Q(type='INCOME')),
            expenses=Sum('amount', filter=Q(type='EXPENSE')),
        )
        trend.append({
            'label': MONTHS_ES[tm - 1],
            'income': float(row['income'] or 0),
            'expenses': float(row['expenses'] or 0),
        })

    budgets = []
    if currency:
        for b in Budget.objects.filter(
            colony=colony, month=month, year=year, currency=currency
        ).select_related('category').with_spent():
            budgets.append({
                'name': b.category.name,
                'icon': b.category.icon,
                'limit': float(b.limit_amount),
                'spent': float(b.spent()),
                'pct': b.pct(),
                'status': b.status(),
            })

    days_in_month = calendar.monthrange(year, month)[1]
    if (year, month) == (today.year, today.month):
        days_elapsed = today.day
    elif (year, month) < (today.year, today.month):
        days_elapsed = days_in_month
    else:
        days_elapsed = 0
    projection = (expenses / days_elapsed * days_in_month) if days_elapsed else expenses

    ant = _ant_expenses(colony, currency, year, month)

    next_year, next_month = (year, month + 1) if month < 12 else (year + 1, 1)

    return render(request, 'finances/analytics.html', {
        'year': year,
        'month': month,
        'month_label': f'{MONTHS_ES[month - 1]} {year}',
        'prev_link': f'{prev_year}-{prev_month:02d}',
        'next_link': f'{next_year}-{next_month:02d}',
        'currencies': currencies,
        'selected_currency': selected,
        'symbol': symbol,
        'kpis': kpis,
        'by_category': by_category,
        'trend': trend,
        'budgets': budgets,
        'projection': projection,
        'projection_delta': _delta(projection, expenses),
        'ant': ant,
        'by_category_json': [{'name': c['name'], 'total': c['total'], 'color': c['color']} for c in by_category],
        'trend_json': trend,
    })


def dashboard(request):
    colony = request.colony
    ctx = _monthly_summary(colony)
    ctx['balance_json'] = ctx['balance_by_currency']
    ctx['kpis_json'] = ctx['kpis_by_currency']
    ctx['recent_transactions'] = Transaction.objects.filter(colony=colony).select_related('category', 'currency')[:10]
    ctx['reserves_count'] = Reserve.objects.filter(colony=colony, is_achieved=False).count()
    ctx['active_reserves_list'] = list(Reserve.objects.filter(colony=colony, is_achieved=False).only('id', 'name'))

    today = timezone.now().date()
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

    deadline_threshold = timezone.now().date() + timedelta(days=colony.debt_show_days)
    pending_debts = Debt.objects.filter(
        colony=colony,
        is_settled=False,
        debt_type='OWE',
        deadline__lte=deadline_threshold,
    ).select_related('currency').order_by('deadline')[:5]
    ctx['pending_debts'] = pending_debts

    pending_installments = Installment.objects.filter(
        purchase__colony=colony,
        is_paid=False,
        due_date__year=today.year,
        due_date__month=today.month,
    ).select_related('purchase', 'purchase__currency').order_by('due_date')[:5]
    ctx['pending_installments'] = pending_installments

    upcoming_subscriptions = Subscription.objects.filter(
        colony=colony,
        is_active=True,
    ).select_related('currency', 'category').order_by('next_date')[:5]
    ctx['upcoming_subscriptions'] = upcoming_subscriptions

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
    qs = Transaction.objects.filter(colony=colony).select_related('category', 'currency')
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
    type_param = request.GET.get('type')
    return_url = _list_for_type(type_param) if type_param else 'finances:transaction_list'
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, colony=colony)
        if form.is_valid():
            t = form.save(commit=False)
            t.colony = colony
            t.save()
            form.save_m2m()
            reserve_id = form.cleaned_data.get('reserve')
            if reserve_id:
                _update_reserve_progress(reserve_id, t.amount, colony)
            messages.success(request, f'Transaccion registrada: {t}')
            if request.htmx:
                return render(request, 'components/toast.html', {'message': 'Transaccion guardada'}, status=201)
            return redirect(_list_for_type(t.type) if type_param else 'finances:transaction_list')
    else:
        initial = {'date': date.today(), 'type': type_param or 'EXPENSE'}
        form = TransactionForm(initial=initial, colony=colony)

    return render(request, 'finances/transaction_form.html', {'form': form, 'return_url': return_url})


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
            reserve_id = form.cleaned_data.get('reserve')
            if reserve_id:
                _update_reserve_progress(reserve_id, t.amount, colony)
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
        old_reserve = t.reserve
        form = TransactionForm(request.POST, request.FILES, instance=t, colony=colony)
        if form.is_valid():
            t = form.save()
            new_reserve = form.cleaned_data.get('reserve')
            if new_reserve and new_reserve != old_reserve:
                _update_reserve_progress(new_reserve, t.amount, colony)
            messages.success(request, 'Transaccion actualizada')
            return redirect('finances:transaction_list')
    else:
        form = TransactionForm(instance=t, colony=colony)

    cat = t.category
    ctx = {
        'form': form,
        'transaction': t,
        'return_url': 'finances:transaction_list',
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
        'can_create': bool(request.user.is_authenticated),
    })


def category_list(request):
    colony = request.colony
    categories = _colony_objects(Category, colony)
    can_manage = bool(request.user.is_authenticated)
    return render(request, 'finances/category_list.html', {'categories': categories, 'can_manage': can_manage, 'colony': colony})


def category_add(request):
    colony = request.colony
    if not request.user.is_authenticated:
        return redirect('finances:category_list')
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cat = form.save(commit=False)
        cat.colony = colony
        cat.save()
        messages.success(request, f'Categoría creada: {cat.name}')
        if request.htmx:
            if request.POST.get('from') == 'page':
                return _category_list_content(request)
            return _category_options_response(request, form.cleaned_data['type'])
        return redirect('finances:category_list')
    return render(request, 'finances/partials/category_form.html', {
        'form': form,
        'form_url': 'finances:category_add',
        'title': 'Nueva categoría',
        'icon_list': CATEGORY_ICONS,
        'color_list': CATEGORY_COLORS,
    })


def category_edit(request, pk):
    colony = request.colony
    if not request.user.is_authenticated:
        return redirect('finances:category_list')
    cat = get_object_or_404(Category, pk=pk, colony=colony)
    form = CategoryForm(request.POST or None, instance=cat)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Categoría actualizada: {cat.name}')
        if request.htmx:
            if request.POST.get('from') == 'page':
                return _category_list_content(request)
            return _category_options_response(request, form.cleaned_data['type'])
        return redirect('finances:category_list')
    return render(request, 'finances/partials/category_form.html', {
        'form': form,
        'form_url': 'finances:category_edit',
        'form_pk': pk,
        'title': 'Editar categoría',
        'icon_list': CATEGORY_ICONS,
        'color_list': CATEGORY_COLORS,
    })


def category_delete(request, pk):
    colony = request.colony
    if not request.user.is_authenticated:
        return redirect('finances:category_list')
    cat = get_object_or_404(Category, pk=pk, colony=colony)
    if request.method == 'POST':
        error = None
        try:
            name = cat.name
            cat.delete()
            messages.success(request, f'Categoría eliminada: {name}')
        except ProtectedError:
            error = f'No se puede eliminar "{cat.name}": tiene transacciones asociadas'
        if request.htmx:
            if request.POST.get('from') == 'page':
                if error:
                    return render(request, 'finances/partials/category_delete_confirm.html', {
                        'category': cat, 'error': error,
                    })
                return _category_list_content(request)
            return _category_options_response(request, 'EXPENSE')
        if error:
            messages.error(request, error)
        return redirect('finances:category_list')
    return render(request, 'finances/partials/category_delete_confirm.html', {'category': cat})


def _category_list_content(request):
    colony = request.colony
    categories = _colony_objects(Category, colony)
    return render(request, 'finances/partials/category_list_content.html', {
        'categories': categories,
        'can_manage': bool(request.user.is_authenticated),
        'colony': colony,
    })


def _category_options_response(request, type_val):
    colony = request.colony
    selected = request.GET.get('selected', '')
    qs = Category.objects.filter(Q(colony=colony) | Q(colony__isnull=True), type=type_val)
    return render(request, 'finances/partials/category_options.html', {
        'categories': qs,
        'selected': int(selected) if selected.isdigit() else '',
        'can_create': bool(request.user.is_authenticated),
    })


def conversion(request):
    from ..exchange import convert, fetch_exchange_rates, rates_stale, last_updated

    colony = request.colony

    fetch_status = None
    if request.method == 'POST' and request.POST.get('action') == 'fetch':
        ok, fetch_status = fetch_exchange_rates(force=True)
    else:
        try:
            if rates_stale():
                _, fetch_status = fetch_exchange_rates()
        except Exception:
            fetch_status = 'No se pudo actualizar las cotizaciones'

    currencies = list(Currency.objects.filter(Q(colony=colony) | Q(colony__isnull=True)).order_by('code'))
    for c in currencies:
        c.rate_value = f'{c.rate_to_base:.4f}'

    rates = {c.code: c.rate_to_base for c in currencies}
    rates_json = {c.code: float(c.rate_to_base) for c in currencies}

    from ..exchange import available_balances
    available = available_balances(colony)

    result = None
    default_from = (colony.default_currency.code if colony.default_currency else 'ARS')
    from_code = default_from
    to_code = 'EUR' if from_code == 'USD' else 'USD'
    amount_str = ''

    if request.method == 'POST' and request.POST.get('action') == 'convert':
        from_code = request.POST.get('from', 'ARS')
        to_code = request.POST.get('to', 'USD')
        amount_str = request.POST.get('amount', '')

        if from_code == to_code:
            messages.error(request, 'No podés convertir a la misma moneda')
            return redirect('finances:conversion')

        try:
            amount = Decimal(amount_str)
        except (InvalidOperation, ValueError):
            amount = None

        if amount is None or amount <= 0:
            messages.error(request, 'Ingresá un monto válido')
            return redirect('finances:conversion')

        converted = convert(amount, from_code, to_code, rates)
        if converted is None:
            messages.error(request, 'Moneda inválida para la conversión')
            return redirect('finances:conversion')

        converted = converted.quantize(Decimal('0.01'))
        if converted <= 0:
            messages.error(request, 'El resultado de la conversión es 0')
            return redirect('finances:conversion')

        if colony.require_funds_for_conversion:
            avail = available.get(from_code)
            if avail is not None and amount > Decimal(str(avail)):
                messages.error(request, f'No tenés suficientes {from_code} (disponible: {avail:,.2f}). Convertí desde otra moneda.')
                return redirect('finances:conversion')

        from_cur = next((c for c in currencies if c.code == from_code), None)
        to_cur = next((c for c in currencies if c.code == to_code), None)
        if not from_cur or not to_cur:
            messages.error(request, 'Moneda no encontrada')
            return redirect('finances:conversion')

        note = f'Conversión: {amount} {from_code} → {converted} {to_code}'
        exp_cat, _ = Category.objects.get_or_create(
            colony=colony, name='Conversión de moneda', type='EXPENSE',
            defaults={'icon': 'arrows-right-left', 'color': '#C4943A'},
        )
        inc_cat, _ = Category.objects.get_or_create(
            colony=colony, name='Conversión de moneda', type='INCOME',
            defaults={'icon': 'arrows-right-left', 'color': '#C4943A'},
        )

        Transaction.objects.create(
            colony=colony, type='EXPENSE', amount=amount,
            currency=from_cur, category=exp_cat,
            date=timezone.now().date(), note=note,
        )
        Transaction.objects.create(
            colony=colony, type='INCOME', amount=converted,
            currency=to_cur, category=inc_cat,
            date=timezone.now().date(), note=note,
        )

        messages.success(request, f'Convertidos {amount} {from_code} → {converted} {to_code}')
        return redirect('finances:conversion')

    if request.method == 'POST' and request.POST.get('action') == 'save_rates':
        from django.utils import timezone as _tz
        saved = 0
        now = _tz.now()
        for c in currencies:
            val = request.POST.get(f'rate_{c.code}')
            if val:
                try:
                    c.rate_to_base = Decimal(val).quantize(Decimal('0.0001'))
                    c.rates_updated_at = now
                    c.save(update_fields=['rate_to_base', 'rates_updated_at'])
                    saved += 1
                except (InvalidOperation, ValueError):
                    continue
        messages.success(request, f'Cotizaciones guardadas ({saved} monedas)')
        return redirect('finances:conversion')

    quick = [
        {'code': c.code, 'symbol': c.symbol, 'name': c.name, 'to_ars': c.rate_to_base}
        for c in currencies if c.code != 'ARS'
    ]

    ctx = {
        'currencies': currencies,
        'rates_json': rates_json,
        'result': result,
        'from_code': from_code,
        'to_code': to_code,
        'default_from': default_from,
        'amount': amount_str,
        'available': available,
        'require_funds': colony.require_funds_for_conversion,
        'available_json': available,
        'quick': quick,
        'fetch_status': fetch_status,
        'last_updated': last_updated(),
        'interval_hours': settings.EXCHANGE_INTERVAL_HOURS if hasattr(settings, 'EXCHANGE_INTERVAL_HOURS') else 6,
    }
    if request.htmx:
        return render(request, 'finances/partials/rates_section.html', ctx)
    return render(request, 'finances/conversion.html', ctx)
