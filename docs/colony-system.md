# Colony System — Multi-tenancy en TrackAnt

## Visión General

TrackAnt usa un sistema de multi-tenancy basado en el modelo `Colony`. Cada usuario (o invitado anónimo) tiene una "colonia" que agrupa todos sus datos. **TODOS los modelos de todas las apps tienen `colony = ForeignKey('users.Colony', on_delete=models.CASCADE)`**.

## Modelos

### CustomUser (`users/models.py`)
Extiende `AbstractUser`. Configurado en settings como `AUTH_USER_MODEL = 'users.CustomUser'`.

### Colony (`users/models.py`)
Modelo central de multi-tenancy.

**Campos:**
- `name` — Nombre de la colonia
- `owner` — FK a CustomUser (PROTECT). El dueño de la colonia
- `members` — M2M a CustomUser. Miembros de la colonia
- `is_guest` — Boolean. True para colonias de usuarios anónimos
- `default_currency` — FK a Currency. Moneda por defecto para la colonia
- `auto_create_debt_transactions` — Boolean (default False). Al pagar una deuda, crea una Transaction EXPENSE automáticamente
- `auto_create_split_transactions` — Boolean (default False). Al crear un gasto compartido, crea una Transaction EXPENSE automáticamente
- `budget_alert_threshold` — Integer (50-100, default 80). Umbral de alerta de presupuesto en dashboard
- `debt_show_days` — Integer (1-365, default 7). Días de anticipación para mostrar deudas con deadline próximo

## ColonyMiddleware (`users/middleware.py`)

Se ejecuta en cada request. Flujo:

1. Si el usuario está autenticado, usa su colonia (o crea una si no tiene)
2. Si es anónimo, crea/usar una "colonia invitada" (`is_guest=True`)
3. Inyecta `request.colony` en el request
4. Si el usuario no ha visto el welcome screen, redirige a `/welcome/`

**Excepciones** (no pasan por middleware): `/welcome/`, `/login/`, `/registro/`, `/static/`, `/media/`, `/api/`

## Auth Dual

### Usuarios Anónimos
- Se crea automáticamente una `Colony` con `is_guest=True`
- Los datos persisten en la sesión del navegador
- No pueden compartir datos con otros usuarios

### Usuarios Registrados
- Se crea una `Colony` propia al registrarse
- Pueden invitar miembros a su colonia
- Datos persistentes en la DB

## Patrón de Filtros de Datos

### Datos Privados (Transaction, Reserve, Debt, Budget, etc.)
```python
# En views:
colony = request.colony
queryset = Transaction.objects.filter(colony=colony)

# En ViewSets:
def get_queryset(self):
    return Transaction.objects.filter(colony=self.request.colony)

def perform_create(self, serializer):
    serializer.save(colony=self.request.colony)
```

### Datos Globales (Currency, Category)
```python
# Muestran datos de la colonia DEL USUARIO + datos globales (sin colonia)
from django.db.models import Q
queryset = Category.objects.filter(Q(colony=colony) | Q(colony__isnull=True))
```

## Auto-creación de Transactions

Hay múltiples puntos de entrada que crean Transactions automáticamente:

### Subscriptions (`subscriptions/services.py`)
- `mark_as_paid(payment)` — Crea Transaction EXPENSE con categoría de la suscripción
- Signal `post_save` en Subscription — Crea el primer SubscriptionPayment automáticamente

### Debts (`debts/views/pages.py`)
- Al pagar una deuda, si `colony.auto_create_debt_transactions` es True:
  - Crea categoría "Pago de deuda" con `get_or_create`
  - Crea Transaction EXPENSE

### Splits (`splits/views/pages.py`)
- Al crear un gasto compartido, si `colony.auto_create_split_transactions` es True:
  - Crea categoría "Gasto compartido" con `get_or_create`
  - Crea Transaction EXPENSE

## Transaction.reserve — Auto-actualización de Saldo

El modelo `Transaction` tiene un FK opcional a `Reserve`:
```python
reserve = models.ForeignKey('goals.Reserve', on_delete=models.SET_NULL, null=True, blank=True)
```

Al crear/editar una transacción (solo INCOME, solo reservas con objetivo):
1. `_update_reserve_progress()` actualiza `current_amount` de la reserva usando F() expressions
2. Auto-setea `is_achieved=True` cuando `current_amount >= target_amount`

**Ubicación**: `finances/views/pages.py:36-53`

## SubscriptionPayment — Modelo No Documentado

Modelo generado por signal al crear una Subscription.

**Campos:**
- `subscription` — FK a Subscription (CASCADE)
- `due_date` — Fecha de vencimiento
- `is_paid` — Boolean
- `paid_date` — Fecha de pago (nullable)
- `transaction` — FK a Transaction (SET_NULL, nullable). Se vincula al marcar como pagado

**Flujo:**
1. Al crear Subscription → signal crea primer SubscriptionPayment
2. Al marcar como pagado → se crea Transaction y se vincula
3. Se calcula próximo vencimiento y se crea siguiente SubscriptionPayment

## Services Layer (`subscriptions/services.py`)

### `mark_as_paid(payment)`
1. Crea Transaction EXPENSE
2. Actualiza `is_paid=True` y `paid_date=today`
3. Calcula próxima fecha con `calculate_next_due_date()`
4. Crea próximo SubscriptionPayment

### `mark_as_unpaid(payment)`
1. Elimina la Transaction vinculada
2. Desmarca el pago
3. Elimina pagos futuros no pagados
4. Retrocede la fecha de la suscripción

### `calculate_next_due_date(current_date, cycle)`
- WEEKLY: +1 week
- MONTHLY: +1 month
- YEARLY: +1 year

Usa `dateutil.relativedelta`.

## Settings de Colony en Dashboard

El dashboard (`finances/views/pages.py`) usa estos campos para filtrar:

```python
# Alertas de presupuesto
threshold = colony.budget_alert_threshold  # Filtra presupuestos que superan este %
over_budget = [b for b in budgets if b.pct() >= threshold]

# Deudas próximas
deadline_threshold = date.today() + timedelta(days=colony.debt_show_days)
upcoming_deadlines = debts.filter(deadline__lte=deadline_threshold)
```

**Inconsistencia conocida**: `ants/utils.py` usa 80% hardcoded en lugar de `colony.budget_alert_threshold`.
