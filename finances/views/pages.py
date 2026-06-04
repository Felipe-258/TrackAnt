from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, date
from ..models import Transaction, Category, Currency, Tag
from goals.models import Goal
from ..forms import TransactionForm, CategoryForm


def _month_filter(qs, year=None, month=None):
    today = date.today()
    y = year or today.year
    m = month or today.month
    return qs.filter(date__year=y, date__month=m)


def _monthly_summary():
    today = date.today()
    month_qs = Transaction.objects.filter(date__year=today.year, date__month=today.month)
    incomes = month_qs.filter(type='INCOME').aggregate(s=Sum('amount'))['s'] or 0
    expenses = month_qs.filter(type='EXPENSE').aggregate(s=Sum('amount'))['s'] or 0
    total = Transaction.objects.aggregate(
        i=Sum('amount', filter=Q(type='INCOME')),
        e=Sum('amount', filter=Q(type='EXPENSE')),
    )
    balance = (total['i'] or 0) - (total['e'] or 0)
    return {
        'monthly_income': incomes,
        'monthly_expenses': expenses,
        'total_balance': balance,
    }


def dashboard(request):
    ctx = _monthly_summary()
    ctx['recent_transactions'] = Transaction.objects.select_related('category', 'currency')[:10]
    ctx['goals_count'] = Goal.objects.filter(is_achieved=False).count()
    ctx['active_goals_list'] = list(Goal.objects.filter(is_achieved=False).only('id', 'name'))

    today = date.today()
    month_expenses = Transaction.objects.filter(
        type='EXPENSE',
        date__year=today.year,
        date__month=today.month,
    ).values('category__name', 'category__color').annotate(total=Sum('amount'))

    ctx['category_labels'] = [e['category__name'] for e in month_expenses]
    ctx['category_values'] = [float(e['total']) for e in month_expenses]
    ctx['category_colors'] = [e['category__color'] for e in month_expenses]

    months_data = []
    for m in range(1, today.month + 1):
        m_incomes = Transaction.objects.filter(type='INCOME', date__year=today.year, date__month=m).aggregate(s=Sum('amount'))['s'] or 0
        m_expenses = Transaction.objects.filter(type='EXPENSE', date__year=today.year, date__month=m).aggregate(s=Sum('amount'))['s'] or 0
        months_data.append({'income': float(m_incomes), 'expense': float(m_expenses)})

    ctx['monthly_incomes'] = [m['income'] for m in months_data]
    ctx['monthly_expenses_data'] = [m['expense'] for m in months_data]

    return render(request, 'finances/dashboard.html', ctx)


def _transaction_list(request, type_filter=None):
    qs = Transaction.objects.select_related('category', 'currency').prefetch_related('tags')
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
    })


def transaction_list(request):
    return _transaction_list(request)


def income_list(request):
    return _transaction_list(request, type_filter='INCOME')


def expense_list(request):
    return _transaction_list(request, type_filter='EXPENSE')


def transaction_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            t = form.save()
            messages.success(request, f'Transacción registrada: {t}')
            if request.htmx:
                return render(request, 'components/toast.html', {'message': '✅ Transacción guardada'}, status=201)
            return redirect('finances:transaction_list')
    else:
        initial = {'date': date.today(), 'type': request.GET.get('type', 'EXPENSE')}
        form = TransactionForm(initial=initial)

    return render(request, 'finances/transaction_form.html', {'form': form, 'tag_ids': '[]', 'custom_tags': '[]'})


def transaction_edit(request, pk):
    t = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=t)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transacción actualizada')
            return redirect('finances:transaction_list')
    else:
        form = TransactionForm(instance=t)
    return render(request, 'finances/transaction_form.html', {'form': form, 'transaction': t})


def transaction_delete(request, pk):
    t = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        t.delete()
        messages.success(request, 'Transacción eliminada')
        if request.htmx:
            return render(request, 'components/toast.html', {'message': '🗑️ Transacción eliminada'})
        return redirect('finances:transaction_list')
    return render(request, 'finances/transaction_confirm_delete.html', {'transaction': t})


def transaction_category_options(request):
    type_val = request.GET.get('type', 'EXPENSE')
    selected = request.GET.get('selected', '')
    qs = Category.objects.filter(type=type_val)
    return render(request, 'finances/partials/category_options.html', {
        'categories': qs,
        'selected': int(selected) if selected.isdigit() else '',
    })


def tag_search(request):
    q = request.GET.get('q', '')
    tags = Tag.objects.filter(name__icontains=q)[:10] if q else Tag.objects.none()
    return render(request, 'finances/partials/tag_results.html', {'tags': tags, 'query': q})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'finances/category_list.html', {'categories': categories})
