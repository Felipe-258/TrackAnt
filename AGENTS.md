# TrackAnt — Guía para Agentes

## Resumen del Proyecto

**TrackAnt** es un tracker de finanzas personales con multi-tenancy por "colonia" de hormigas. Auth dual: usuarios anónimos (colonia invitada) y registrados (colonia propia). Local-first con SQLite. Desktop/web con Django + HTMX + Alpine.js + Tailwind CSS.

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Django >=5.0,<5.1 |
| API | Django REST Framework >=3.15 |
| Filtros | django-filter >=25.1 |
| HTMX | django-htmx >=1.19 |
| Forms | django-widget-tweaks, django-crispy-forms + crispy-tailwind |
| CSS | Tailwind CSS (CDN) con paleta custom |
| JS | HTMX + Alpine.js 3.x + Chart.js 4.4.7 (CDN) |
| Iconos | Lucide (CDN) |
| DB | SQLite |
| Image | Pillow (ImageField) |
| Dates | python-dateutil (relativedelta) |

**CDNs en `base.html`** (versiones pinned):
- `tailwindcss.com` — config inline
- `lucide@0.462.0`
- `htmx.org@2.0.4`
- `alpinejs@3.14.9`
- `chart.js@4.4.7`

## Estructura de Directorios

```
TrackAnt/
├── manage.py, requirements.txt, VERSION
├── trackant/          # Config Django (settings, urls, wsgi, utils)
├── templates/         # base.html, components/, partials/
├── static/            # manifest.json, sw.js, js/haptics.js
├── users/             # CustomUser, Colony, auth, settings
├── finances/          # Core: Transaction, Category, Tag, Currency, Dashboard
├── goals/             # Metas de ahorro (Goal)
├── debts/             # Deudas y préstamos (Debt, DebtPayment)
├── budgets/           # Presupuestos mensuales (Budget)
├── subscriptions/     # Suscripciones (Subscription, SubscriptionPayment, services)
├── splits/            # Gastos compartidos (SplitGroup, SplitExpense)
├── ants/              # Colonia visual (vistas, template tags, CSS)
├── api/               # Router API central + stats endpoints
├── backups/           # Command: backup_db
├── docs/              # responsive-patterns.md, browser-tools.md, colony-system.md
├── scripts/           # run.sh, trackant.desktop
└── venv/
```

## Sistema Colony (Multi-tenancy)

**CRÍTICO**: Todos los modelos tienen `colony = ForeignKey('users.Colony')`. Todas las vistas usan `request.colony` (inyectado por `ColonyMiddleware`), NO `request.user`, para filtrar datos.

- **Colony**: owner, members (M2M), is_guest, default_currency, config fields
- **Auth dual**: anónimo → colonia invitada (`is_guest=True`); registrado → colonia propia
- **Filtros datos privados**: `filter(colony=request.colony)`
- **Filtros datos globales**: `filter(Q(colony=colony) | Q(colony__isnull=True))` (Currency, Category, Tag)
- **Ref completa**: `docs/colony-system.md`

## Apps y Sus Propósitos

### `users` — Auth y Colony
Modelos: `CustomUser` (AbstractUser), `Colony`
- Colony config: `auto_create_debt_transactions`, `auto_create_split_transactions`, `budget_alert_threshold` (50-100), `debt_show_days` (1-365)
- ColonyMiddleware inyecta `request.colony`
- URLs: `/welcome/`, `/login/`, `/registro/`, `/logout/`, `/settings/`, `/settings/backup/`

### `finances` — App Core
Modelos: `Currency`, `Category`, `Tag`, `Transaction`
- **Dashboard** (`/`): KPIs por moneda, gráficos torta/barras, últimas 10 transacciones, widget colonia
- **Transacciones** (`/transactions/`): CRUD HTMX, búsqueda, filtro por mes
- **Ingresos/Gastos**: Listados con `list_type` filtrado
- **Tags dual**: M2M `Tag` + `custom_tags` JSONField
- **Transaction.goal**: FK opcional → auto-actualiza `current_amount` con F() expressions
- **Transaction.receipt**: ImageField para subir comprobantes
- `seed_data [--colony-id]`: crea 6 monedas, 21 categorías, 8 tags

### `goals` — Metas de Ahorro
Modelo: `Goal` — CRUD con barras de progreso. Auto-marca `is_achieved` cuando `current_amount >= target_amount`.

### `debts` — Deudas
Modelos: `Debt`, `DebtPayment` — Tipos: OWE/OWED. Auto-settled cuando `remaining <= 0`. Si `colony.auto_create_debt_transactions`, al pagar crea Transaction EXPENSE.

### `budgets` — Presupuestos
Modelo: `Budget` (unique: category, month, year) — `BudgetQuerySet.with_spent()` anota total gastado para evitar N+1.

### `subscriptions` — Suscripciones
Modelos: `Subscription`, `SubscriptionPayment`
- Signal `post_save`: crea primer SubscriptionPayment automáticamente
- Services: `mark_as_paid()` crea Transaction + próximo pago; `mark_as_unpaid()` revierte
- Ciclos: WEEKLY, MONTHLY, YEARLY

### `splits` — Gastos Compartidos
Modelos: `SplitGroup`, `SplitExpense` — Si `colony.auto_create_split_transactions`, al crear gasto crea Transaction EXPENSE.

### `ants` — Colonia Visual
Sin modelos. `ants/utils.py`: computa estado (clima, hormigas, reina, hojas). `ants/templatetags/ant_tags.py`: tags/filtros custom. `ants/static/ants/css/colony.css`: animaciones.

### `backups` — Backup DB
Command: `python manage.py backup_db` — crea backup en `~/.trackant/backups/`, limpia >30 días.

### `api` — Router API
Router central + 3 stats endpoints.

## Modelos — Relaciones Clave

```
users.Colony ──┬── Transaction, Goal, Debt, Budget
              ├── Subscription, SplitGroup, SplitExpense
              └── Currency, Category, Tag

users.CustomUser ──┬── Colony.owner (PROTECT)
                   └── Colony.members (M2M)

Currency ──┬── Transaction, Goal, Debt, Budget, SplitExpense

Category ──┬── Transaction, Budget (solo EXPENSE)
           └── Subscription (SET_NULL)

Tag ←──M2M──→ Transaction

Transaction ──┬── SubscriptionPayment.transaction (SET_NULL)
              └── Goal (FK, SET_NULL) — auto-actualiza progreso

Subscription ──< SubscriptionPayment (CASCADE)

Debt ──< DebtPayment (CASCADE)

SplitGroup ──< SplitExpense (CASCADE)
```

## API REST

Router en `/api/v1/` con `PageNumberPagination` (page_size=25). Sin auth. Filtros: `DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`.

| Endpoint | App | ViewSet |
|---|---|---|
| `currencies/` | finances | ModelViewSet |
| `categories/` | finances | ModelViewSet |
| `tags/` | finances | ModelViewSet |
| `transactions/` | finances | ModelViewSet |
| `goals/` | goals | ModelViewSet |
| `debts/` | debts | ModelViewSet |
| `debt-payments/` | debts | ModelViewSet |
| `budgets/` | budgets | ModelViewSet |
| `subscriptions/` | subscriptions | ModelViewSet |
| `subscription-payments/` | subscriptions | ReadOnly + action `toggle` |
| `split-groups/` | splits | ModelViewSet |
| `split-expenses/` | splits | ModelViewSet |
| `stats/` | api | GET: balance, income/expense, counts |
| `stats/by-category/` | api | GET: gastos por categoría del mes |
| `stats/monthly/` | api | GET: income/expense por mes del año |

## URLs de Páginas

```
/                          → finances:dashboard
/transactions/             → finances:transaction_list (+ add, edit, delete)
/transactions/quick-add/   → finances:transaction_quick_add (POST HTMX)
/incomes/                  → finances:income_list
/expenses/                 → finances:expense_list
/categories/               → finances:category_list
/goals/                    → goals:goal_list (+ add, edit, delete, add-progress)
/debts/                    → debts:debt_list (+ add, edit, delete, detail)
/budgets/                  → budgets:budget_list (+ add, edit, delete)
/subscriptions/            → subscriptions:subscription_list (+ add, edit, delete)
/splits/                   → splits:split_list (+ groups/add, detail, edit, delete)
/ants/colony/              → ants:colony_view
/ants/playground/          → playground (solo DEBUG)
/welcome/                  → users:welcome
/login/                    → users:login
/registro/                 → users:registro
/logout/                   → users:logout
/settings/                 → users:settings
/settings/backup/          → users:backup_download
/admin/                    → Django admin
```

## Sistema de Diseño

**Paleta Tailwind custom:**
| Paleta | Uso |
|---|---|
| `earth` | Fondos, bordes, texto neutro, chrome UI |
| `clay` | Gastos, montos negativos, delete |
| `sage` | Ingresos, montos positivos, éxito |
| `gold` | Metas, progreso, suscripciones, acentos |

**Modo Oscuro**: class-based, toggle Alpine.js, persistido en localStorage.

**Layout**: Sidebar fijo `w-64`, header sticky con backdrop blur, footer fijo. Quick Add modal via `$dispatch('open-quick-add')`.

**PWA**: Bottom tab bar (Home, Ingresos, Gastos, Metas, Más). View Transitions API para transiciones entre páginas. Service worker en `static/sw.js`.

**Iconos**: Lucide CDN `<i data-lucide="name" class="lucide">`. Sizes: `.lucide` (1.25em), `.lucide-sm` (1em), `.lucide-lg` (1.5em). Se recrean en cada swap HTMX.

## Patrones de Código

### Vistas
- **Páginas**: Function-based views en `views/pages.py`
- **API**: DRF `ModelViewSet` en `views/api.py`
- Stats API: `@api_view(['GET'])` function-based
- URLs: `app_name` definido, snake_case para names
- Templates: `{% url 'app:name' %}`

### Colony Pattern (en TODAS las vistas)
```python
# Helper
def _colony_objects(request, model):
    return model.objects.filter(colony=request.colony)

# En vista
colony = request.colony
queryset = Transaction.objects.filter(colony=colony)

# En ViewSet
def get_queryset(self):
    return Transaction.objects.filter(colony=self.request.colony)

def perform_create(self, serializer):
    serializer.save(colony=self.request.colony)
```

### Templates
- Heredan de `'base.html'`. Bloques: `title`, `page_title`, `page_subtitle`, `content`, `extra_scripts`
- Nombres: `<app>/<modelo>_<accion>.html`
- Parciales: `<app>/partials/<name>.html`

### HTMX
- CRUD interactions HTMX-driven. `request.htmx` check para partial vs full redirect
- Tags: autocomplete debounce 300ms. Transacciones: search debounce 500ms

### Alpine.js
- Estado global: `sidebarOpen`, `darkMode` (body `x-data`)
- Quick add: `quickAddModal()` + `quickCategoryDropdown()`
- Transacciones: search toggle `searchOpen` en mobile

### Django Admin
Todos los modelos registrados. Verbose names en español.

### Seed Data
`python manage.py seed_data [--colony-id PK]` — Idempotente. Sin `--colony-id` crea datos globales.

## Convenciones Importantes

1. **Decimal, nunca float**: `DecimalField` → siempre `Decimal()`. `Decimal + float` → `TypeError`.
2. **F() expressions**: Updates atómicos: `Model.objects.filter(pk=pk).update(campo=F('campo') + valor)`
3. **select_related('currency')**: Siempre en templates que acceden a `goal.currency.symbol`
4. **request.colony, NO request.user**: Para filtrar datos en todas las vistas
5. **request.resolver_match.namespace**: Para active state del sidebar
6. **Mensajes Django**: En `base.html`, estilos por tag (success=sage, error=clay, warning=gold, info=earth)
7. **View Transitions**: Elementos fixed deben tener `view-transition-name: none`
8. **Nunca commitear** sin que el usuario lo pida explícitamente
9. **Nunca git push a main** sin autorización explícita
10. **Cambios en main**: Actualizar imagen Docker en GHCR con `./build-push-deploy.sh`
11. **Testear en Docker**, no en local. Session cookies, middleware, env vars difieren

## Comandos de Desarrollo

```bash
source venv/bin/activate
python manage.py runserver
python manage.py makemigrations && python manage.py migrate
python manage.py seed_data [--colony-id PK]
python manage.py test
python manage.py check
python manage.py backup_db
python manage.py createsuperuser
./scripts/run.sh  # crea venv, migra, seed, runserver 0.0.0.0:8000
```

## Settings Clave

- `AUTH_USER_MODEL = 'users.CustomUser'`
- `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'`
- `LANGUAGE_CODE = 'es-AR'`
- `TIME_ZONE = 'America/Argentina/Buenos_Aires'`
- `DEBUG`: env `TRACKANT_DEBUG`, default `True`
- `SECRET_KEY`: env `TRACKANT_SECRET_KEY`, fallback inseguro
- `DATA_DIR`: `~/.trackant/` (DB: `db.sqlite3`, backups en `backups/`)
- `MEDIA_URL = 'media/'`, `MEDIA_ROOT = BASE_DIR / 'media'`
- `SESSION_SAVE_EVERY_REQUEST = True`, `SESSION_COOKIE_AGE` = 2 semanas
- `CRISPY_TEMPLATE_PACK = 'tailwind'`
- `COLONY_MIDDLEWARE`: `'users.middleware.ColonyMiddleware'` (orden importa)
- Sin password validators. REST sin auth, paginación 25

## Bugs Conocidos (Lecciones)

- **Decimal + float**: Siempre `Decimal(amount)`, nunca `float()` con DecimalField
- **position: absolute en dropdowns**: Se corta por `overflow-y-auto`. Usar `position: fixed` + `getBoundingClientRect()`
- **ants/utils.py hardcoded 80%**: `budget_alerts` usa 80% fijo, no `colony.budget_alert_threshold`
